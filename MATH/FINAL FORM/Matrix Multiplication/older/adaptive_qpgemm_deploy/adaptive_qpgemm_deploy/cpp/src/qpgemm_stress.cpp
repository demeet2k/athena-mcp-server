#include <torch/script.h>
#include <torch/torch.h>

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <mutex>
#include <numeric>
#include <random>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

static double percentile(std::vector<double> v, double p) {
    if (v.empty()) return 0.0;
    std::sort(v.begin(), v.end());
    double idx = (p / 100.0) * (static_cast<double>(v.size()) - 1.0);
    size_t lo = static_cast<size_t>(std::floor(idx));
    size_t hi = static_cast<size_t>(std::ceil(idx));
    double w = idx - static_cast<double>(lo);
    return v[lo] * (1.0 - w) + v[hi] * w;
}

#ifdef __linux__
static double rss_mb_linux() {
    // Read RSS from /proc/self/statm (resident pages)
    std::ifstream f("/proc/self/statm");
    long size = 0, resident = 0;
    if (!(f >> size >> resident)) return -1.0;
    long page_size = sysconf(_SC_PAGESIZE);
    double bytes = static_cast<double>(resident) * static_cast<double>(page_size);
    return bytes / (1024.0 * 1024.0);
}
#else
static double rss_mb_linux() { return -1.0; }
#endif

static void usage(const char* argv0) {
    std::cerr
        << "Usage:\n"
        << "  " << argv0 << " <model.pt> [seconds=60] [workers=8] [batch=32] [input_size=2048]\n"
        << "         [device=cpu|cuda] [intra_threads=0] [interop_threads=0] [jit_opt=0|1]\n"
        << "         [sample_size=5000] [report_every_s=5]\n\n"
        << "Description:\n"
        << "  Multi-threaded stress test. Each worker repeatedly runs forward().\n"
        << "  Latencies are sampled via reservoir sampling (bounded memory).\n"
        << "  Periodic throughput and (approx) p50/p99 are reported.\n\n"
        << "Notes:\n"
        << "  - For device=cuda, the tool synchronizes around forward() for accurate timing.\n"
        << "  - If you run many workers, consider setting intra_threads=1 and interop_threads=1\n"
        << "    to avoid oversubscription.\n";
}

struct Reservoir {
    explicit Reservoir(size_t cap, uint64_t seed)
        : cap_(cap), gen_(static_cast<std::mt19937_64::result_type>(seed)) {}

    void add(double x) {
        ++seen_;
        if (cap_ == 0) return;
        if (samples_.size() < cap_) {
            samples_.push_back(x);
            return;
        }
        std::uniform_int_distribution<uint64_t> dist(0, seen_ - 1);
        uint64_t j = dist(gen_);
        if (j < cap_) {
            samples_[static_cast<size_t>(j)] = x;
        }
    }

    std::vector<double> samples() const { return samples_; }

private:
    size_t cap_;
    uint64_t seen_ = 0;
    std::vector<double> samples_;
    std::mt19937_64 gen_;
};

int main(int argc, const char* argv[]) {
    if (argc < 2) {
        usage(argv[0]);
        return 2;
    }

    try {
        std::string model_path = argv[1];
        int seconds = (argc > 2) ? std::stoi(argv[2]) : 60;
        int workers = (argc > 3) ? std::stoi(argv[3]) : 8;
        int64_t batch = (argc > 4) ? std::stoll(argv[4]) : 32;
        int64_t input_size = (argc > 5) ? std::stoll(argv[5]) : 2048;
        std::string device_str = (argc > 6) ? std::string(argv[6]) : "cpu";
        int intra_threads = (argc > 7) ? std::stoi(argv[7]) : 0;
        int interop_threads = (argc > 8) ? std::stoi(argv[8]) : 0;
        int jit_opt = (argc > 9) ? std::stoi(argv[9]) : 0;
        size_t sample_size = (argc > 10) ? static_cast<size_t>(std::stoll(argv[10])) : 5000;
        int report_every_s = (argc > 11) ? std::stoi(argv[11]) : 5;

        if (seconds <= 0 || workers <= 0 || batch <= 0 || input_size <= 0 || report_every_s <= 0) {
            throw std::runtime_error("Invalid args.");
        }

        if (intra_threads > 0) at::set_num_threads(intra_threads);
        if (interop_threads > 0) at::set_num_interop_threads(interop_threads);

        c10::Device device = c10::kCPU;
        bool use_cuda = false;
        if (device_str == "cuda") {
            if (!torch::cuda::is_available()) {
                throw std::runtime_error("device=cuda requested but CUDA is not available in this LibTorch build.");
            }
            device = c10::kCUDA;
            use_cuda = true;
        }

        torch::jit::ExtraFilesMap extra_files;
        extra_files["qpgemm_meta.json"] = "";
        c10::InferenceMode guard;
        torch::jit::Module module = torch::jit::load(model_path, device, extra_files);
        module.eval();

        if (jit_opt != 0) {
            module = torch::jit::optimize_for_inference(module);
        }

        std::atomic<bool> stop{false};
        std::atomic<long long> calls{0};
        std::atomic<double> total_ms{0.0};
        std::atomic<double> max_ms{0.0};

        std::mutex sample_mutex;
        std::vector<double> global_samples;
        global_samples.reserve(sample_size * static_cast<size_t>(workers));

        auto worker_fn = [&](int tid) {
            // Per-thread input
            auto opts = torch::TensorOptions().dtype(torch::kFloat32).device(device);
            torch::Tensor x = torch::randn({batch, input_size}, opts);
            std::vector<torch::jit::IValue> inputs;
            inputs.emplace_back(x);

            // Warmup a bit
            for (int i = 0; i < 10; ++i) {
                auto y = module.forward(inputs).toTensor();
                (void)y;
            }
            if (use_cuda) torch::cuda::synchronize();

            Reservoir rsv(sample_size, static_cast<uint64_t>(tid + 12345));

            while (!stop.load(std::memory_order_relaxed)) {
                if (use_cuda) torch::cuda::synchronize();
                auto t0 = std::chrono::high_resolution_clock::now();
                auto y = module.forward(inputs).toTensor();
                (void)y;
                if (use_cuda) torch::cuda::synchronize();
                auto t1 = std::chrono::high_resolution_clock::now();

                double ms = std::chrono::duration<double, std::milli>(t1 - t0).count();
                rsv.add(ms);

                calls.fetch_add(1, std::memory_order_relaxed);

                // atomic add for double is not lock-free; use CAS loop
                double cur = total_ms.load(std::memory_order_relaxed);
                while (!total_ms.compare_exchange_weak(cur, cur + ms, std::memory_order_relaxed)) {}

                // max update
                double m = max_ms.load(std::memory_order_relaxed);
                while (ms > m && !max_ms.compare_exchange_weak(m, ms, std::memory_order_relaxed)) {}
            }

            // Merge samples at end
            auto s = rsv.samples();
            std::lock_guard<std::mutex> lk(sample_mutex);
            global_samples.insert(global_samples.end(), s.begin(), s.end());
        };

        std::vector<std::thread> threads;
        threads.reserve(static_cast<size_t>(workers));
        for (int i = 0; i < workers; ++i) {
            threads.emplace_back(worker_fn, i);
        }

        auto start = std::chrono::steady_clock::now();
        auto next_report = start + std::chrono::seconds(report_every_s);

        long long last_calls = 0;
        auto last_time = start;

        while (true) {
            auto now = std::chrono::steady_clock::now();
            if (now - start >= std::chrono::seconds(seconds)) break;

            if (now >= next_report) {
                long long c = calls.load(std::memory_order_relaxed);
                double elapsed_s = std::chrono::duration<double>(now - start).count();
                double window_s = std::chrono::duration<double>(now - last_time).count();
                long long delta_calls = c - last_calls;

                double cps = (window_s > 0) ? (static_cast<double>(delta_calls) / window_s) : 0.0;
                double samples_per_s = cps * static_cast<double>(batch);

                // compute approx percentiles from current merged samples (best-effort).
                // We snapshot the samples vector under lock; this is cheap because it's bounded.
                std::vector<double> snap;
                {
                    std::lock_guard<std::mutex> lk(sample_mutex);
                    snap = global_samples;
                }
                double p50 = percentile(snap, 50);
                double p99 = percentile(snap, 99);
                double rss = rss_mb_linux();

                std::cout << "[t=" << elapsed_s << "s] "
                          << "calls/s=" << cps
                          << " samples/s≈" << samples_per_s
                          << " p50_ms≈" << p50
                          << " p99_ms≈" << p99
                          << " max_ms=" << max_ms.load(std::memory_order_relaxed);
                if (rss > 0) std::cout << " rss_mb≈" << rss;
                std::cout << "\n";

                last_calls = c;
                last_time = now;
                next_report = now + std::chrono::seconds(report_every_s);
            }

            std::this_thread::sleep_for(std::chrono::milliseconds(50));
        }

        stop.store(true);
        for (auto& t : threads) t.join();

        // Final stats
        long long c = calls.load(std::memory_order_relaxed);
        double tot_ms = total_ms.load(std::memory_order_relaxed);
        double mean_ms = (c > 0) ? (tot_ms / static_cast<double>(c)) : 0.0;

        // We already merged all samples from each thread.
        double p50 = percentile(global_samples, 50);
        double p90 = percentile(global_samples, 90);
        double p99 = percentile(global_samples, 99);

        std::cout << "\n[Final]\n";
        std::cout << "  device: " << device_str << "\n";
        std::cout << "  workers: " << workers << "\n";
        std::cout << "  seconds: " << seconds << "\n";
        std::cout << "  batch: " << batch << "\n";
        std::cout << "  input_size: " << input_size << "\n";
        if (intra_threads > 0) std::cout << "  intra_threads: " << intra_threads << "\n";
        if (interop_threads > 0) std::cout << "  interop_threads: " << interop_threads << "\n";
        std::cout << "  total_calls: " << c << "\n";
        std::cout << "  mean_ms: " << mean_ms << "\n";
        std::cout << "  p50_ms≈" << p50 << " p90_ms≈" << p90 << " p99_ms≈" << p99 << "\n";
        std::cout << "  max_ms: " << max_ms.load(std::memory_order_relaxed) << "\n";
        std::cout << "  approx_throughput_samples_per_s: "
                  << (static_cast<double>(c) * static_cast<double>(batch) / static_cast<double>(seconds)) << "\n";

        return 0;
    } catch (const c10::Error& e) {
        std::cerr << "LibTorch error: " << e.what() << "\n";
        return 1;
    } catch (const std::exception& e) {
        std::cerr << "Exception: " << e.what() << "\n";
        return 1;
    }
}
