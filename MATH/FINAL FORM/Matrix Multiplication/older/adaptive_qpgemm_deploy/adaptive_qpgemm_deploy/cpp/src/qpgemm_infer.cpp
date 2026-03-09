#include <torch/script.h>
#include <torch/torch.h>

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <unordered_map>
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

static void usage(const char* argv0) {
    std::cerr
        << "Usage:\n"
        << "  " << argv0 << " <model.pt> [batch=32] [input_size=2048] [warmup=20] [iters=200]\n"
        << "         [device=cpu|cuda] [intra_threads=0] [interop_threads=0] [jit_opt=0|1]\n\n"
        << "Notes:\n"
        << "  - intra_threads=0 means keep PyTorch default.\n"
        << "  - For accurate CUDA timing, this tool synchronizes around forward().\n";
}

int main(int argc, const char* argv[]) {
    if (argc < 2) {
        usage(argv[0]);
        return 2;
    }

    try {
        std::string model_path = argv[1];
        int64_t batch = (argc > 2) ? std::stoll(argv[2]) : 32;
        int64_t input_size = (argc > 3) ? std::stoll(argv[3]) : 2048;
        int warmup = (argc > 4) ? std::stoi(argv[4]) : 20;
        int iters = (argc > 5) ? std::stoi(argv[5]) : 200;
        std::string device_str = (argc > 6) ? std::string(argv[6]) : "cpu";
        int intra_threads = (argc > 7) ? std::stoi(argv[7]) : 0;
        int interop_threads = (argc > 8) ? std::stoi(argv[8]) : 0;
        int jit_opt = (argc > 9) ? std::stoi(argv[9]) : 0;

        if (batch <= 0 || input_size <= 0 || warmup < 0 || iters <= 0) {
            throw std::runtime_error("Invalid numeric args.");
        }

        if (intra_threads > 0) at::set_num_threads(intra_threads);
        if (interop_threads > 0) at::set_num_interop_threads(interop_threads);

        c10::Device device = c10::kCPU;
        bool use_cuda = false;
        if (device_str == "cuda") {
            if (!torch::cuda::is_available()) {
                throw std::runtime_error("device=cuda requested but torch::cuda::is_available() is false. "
                                         "You must use a CUDA-enabled LibTorch build.");
            }
            device = c10::kCUDA;
            use_cuda = true;
        }

        // Load module + embedded extra files (metadata).
        torch::jit::ExtraFilesMap extra_files;
        extra_files["qpgemm_meta.json"] = "";
        extra_files["qpgemm_layer_report.json"] = "";

        c10::InferenceMode guard; // inference-only mode
        torch::jit::Module module = torch::jit::load(model_path, device, extra_files);
        module.eval();

        if (!extra_files["qpgemm_meta.json"].empty()) {
            std::cout << "[meta] qpgemm_meta.json:\n" << extra_files["qpgemm_meta.json"] << "\n";
        } else {
            std::cout << "[meta] qpgemm_meta.json: (not found in artifact)\n";
        }

        if (!extra_files["qpgemm_layer_report.json"].empty()) {
            std::cout << "[meta] qpgemm_layer_report.json: (embedded, " << extra_files["qpgemm_layer_report.json"].size()
                      << " bytes)\n";
        }

        if (jit_opt != 0) {
            // System-dependent inference optimizations (do not re-save).
            module = torch::jit::optimize_for_inference(module);
            std::cout << "[jit] optimize_for_inference applied in-memory.\n";
        }

        // Prepare input
        auto opts = torch::TensorOptions().dtype(torch::kFloat32).device(device);
        torch::Tensor x = torch::randn({batch, input_size}, opts);

        std::vector<torch::jit::IValue> inputs;
        inputs.emplace_back(x);

        // Warmup
        for (int i = 0; i < warmup; ++i) {
            auto y = module.forward(inputs).toTensor();
            (void)y;
        }
        if (use_cuda) torch::cuda::synchronize();

        // Timed runs
        std::vector<double> lat_ms;
        lat_ms.reserve(static_cast<size_t>(iters));

        for (int i = 0; i < iters; ++i) {
            if (use_cuda) torch::cuda::synchronize();
            auto t0 = std::chrono::high_resolution_clock::now();
            auto y = module.forward(inputs).toTensor();
            (void)y;
            if (use_cuda) torch::cuda::synchronize();
            auto t1 = std::chrono::high_resolution_clock::now();
            double ms = std::chrono::duration<double, std::milli>(t1 - t0).count();
            lat_ms.push_back(ms);
        }

        double p50 = percentile(lat_ms, 50);
        double p90 = percentile(lat_ms, 90);
        double p99 = percentile(lat_ms, 99);
        double mean = std::accumulate(lat_ms.begin(), lat_ms.end(), 0.0) / std::max<size_t>(lat_ms.size(), 1);

        std::cout << "\n[Result]\n";
        std::cout << "  device: " << device_str << "\n";
        std::cout << "  batch: " << batch << "\n";
        std::cout << "  input_size: " << input_size << "\n";
        std::cout << "  warmup: " << warmup << "\n";
        std::cout << "  iters: " << iters << "\n";
        if (intra_threads > 0) std::cout << "  intra_threads: " << intra_threads << "\n";
        if (interop_threads > 0) std::cout << "  interop_threads: " << interop_threads << "\n";
        std::cout << "  latency_ms: p50=" << p50 << " p90=" << p90 << " p99=" << p99 << " mean=" << mean << "\n";
        std::cout << "  throughput_samples_per_s@p50: " << (static_cast<double>(batch) / (p50 / 1000.0)) << "\n";

        return 0;
    } catch (const c10::Error& e) {
        std::cerr << "LibTorch error: " << e.what() << "\n";
        return 1;
    } catch (const std::exception& e) {
        std::cerr << "Exception: " << e.what() << "\n";
        return 1;
    }
}
