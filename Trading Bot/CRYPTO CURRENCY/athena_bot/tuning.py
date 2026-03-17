from __future__ import annotations

import statistics
from collections import OrderedDict

import pandas as pd

from .config import AthenaBotConfig
from .utils import now_utc, to_iso, write_json


class TuningEvaluator:
    TUNING_KEYS = (
        "trend_4h_fast_ema",
        "trend_4h_slow_ema",
        "trigger_1h_ema",
        "breakout_lookback",
        "min_volume_ratio",
        "per_position_risk",
        "max_total_open_risk",
        "breakout_buffer_bps",
        "transition_block_threshold",
    )

    CANDIDATE_VALUES = {
        "trend_4h_fast_ema": (12, 20, 30),
        "trend_4h_slow_ema": (34, 50, 72),
        "trigger_1h_ema": (12, 20, 30),
        "breakout_lookback": (12, 20, 30),
        "min_volume_ratio": (0.5, 0.6, 0.8),
        "per_position_risk": (0.0035, 0.005, 0.0075),
        "max_total_open_risk": (0.01, 0.02),
        "breakout_buffer_bps": (5.0, 10.0, 20.0),
        "transition_block_threshold": (0.80, 0.90, 0.95),
    }

    def __init__(self, runtime, config: AthenaBotConfig | None = None):
        self.runtime = runtime
        self.config = config or runtime.config

    def build_candidate_set(self) -> list[dict]:
        baseline = self._parameter_snapshot(self.config)
        candidates: list[dict] = [
            {
                "id": "baseline",
                "label": "Baseline",
                "kind": "baseline",
                "overrides": {},
                "parameters": baseline,
            }
        ]
        seen = {self._candidate_key(baseline)}

        curated_candidates = [
            (
                "trend_12_34",
                "Trend 12/34",
                "trend_pair",
                {
                    "trend_4h_fast_ema": 12,
                    "trend_4h_slow_ema": 34,
                },
            ),
            (
                "trend_12_50",
                "Trend 12/50",
                "trend_pair",
                {
                    "trend_4h_fast_ema": 12,
                    "trend_4h_slow_ema": 50,
                },
            ),
            (
                "trend_30_72",
                "Trend 30/72",
                "trend_pair",
                {
                    "trend_4h_fast_ema": 30,
                    "trend_4h_slow_ema": 72,
                },
            ),
            (
                "trigger_fast",
                "Trigger Fast",
                "trigger_pack",
                {
                    "trigger_1h_ema": 12,
                    "breakout_lookback": 12,
                    "breakout_buffer_bps": 5.0,
                },
            ),
            (
                "trigger_slow",
                "Trigger Slow",
                "trigger_pack",
                {
                    "trigger_1h_ema": 30,
                    "breakout_lookback": 30,
                    "breakout_buffer_bps": 20.0,
                },
            ),
            (
                "volume_loose",
                "Volume Loose",
                "filter_pack",
                {
                    "min_volume_ratio": 0.5,
                },
            ),
            (
                "volume_strict",
                "Volume Strict",
                "filter_pack",
                {
                    "min_volume_ratio": 0.8,
                },
            ),
            (
                "risk_light",
                "Risk Light",
                "risk_pack",
                {
                    "per_position_risk": 0.0035,
                    "max_total_open_risk": 0.01,
                },
            ),
            (
                "risk_heavy",
                "Risk Heavy",
                "risk_pack",
                {
                    "per_position_risk": 0.0075,
                    "max_total_open_risk": 0.02,
                },
            ),
            (
                "transition_tight",
                "Transition Tight",
                "guardrail_pack",
                {
                    "transition_block_threshold": 0.80,
                },
            ),
            (
                "transition_loose",
                "Transition Loose",
                "guardrail_pack",
                {
                    "transition_block_threshold": 0.95,
                },
            ),
            (
                "balanced_filter",
                "Balanced Filter",
                "combo",
                {
                    "trend_4h_fast_ema": 12,
                    "trend_4h_slow_ema": 50,
                    "trigger_1h_ema": 20,
                    "breakout_lookback": 20,
                    "min_volume_ratio": 0.8,
                    "per_position_risk": 0.0035,
                    "max_total_open_risk": 0.02,
                    "breakout_buffer_bps": 10.0,
                    "transition_block_threshold": 0.90,
                },
            ),
            (
                "conservative_guardrails",
                "Conservative Guardrails",
                "combo",
                {
                    "trend_4h_fast_ema": 20,
                    "trend_4h_slow_ema": 72,
                    "trigger_1h_ema": 30,
                    "breakout_lookback": 30,
                    "min_volume_ratio": 0.8,
                    "per_position_risk": 0.0035,
                    "max_total_open_risk": 0.01,
                    "breakout_buffer_bps": 20.0,
                    "transition_block_threshold": 0.80,
                },
            ),
        ]
        for candidate_id, label, kind, overrides in curated_candidates:
            self._append_candidate(
                candidates,
                seen,
                candidate_id=candidate_id,
                label=label,
                kind=kind,
                baseline=baseline,
                overrides=overrides,
            )

        return candidates

    def evaluate_candidates(
        self,
        symbols: list[str],
        windows: list[int],
        candidate_set: list[dict] | None = None,
        top: int = 10,
        refresh: bool = False,
    ) -> dict:
        symbols = symbols or list(self.config.symbols)
        candidate_set = candidate_set or self.build_candidate_set()
        if refresh:
            self.runtime.refresh_data(symbols)

        latest_close = self._latest_common_close(symbols)
        earliest_close = self._earliest_common_close(symbols)
        latest_ts = pd.Timestamp(latest_close)
        earliest_ts = pd.Timestamp(earliest_close)

        candidate_results: list[dict] = []
        window_summaries: OrderedDict[str, list[dict]] = OrderedDict()
        for candidate in candidate_set:
            params = candidate["parameters"]
            override_config = self.config.with_overrides(**params)
            override_config.symbols = tuple(symbols)
            stream = self.runtime.replay.prepare_signal_stream(
                symbols=symbols,
                from_ts=earliest_ts.isoformat(),
                to_ts=latest_ts.isoformat(),
                config_override=override_config,
                refresh=False,
            )

            completed_trades_total = 0
            failed_reasons: list[str] = []
            window_results: list[dict] = []

            for window_days in windows:
                requested_start = latest_ts - pd.Timedelta(days=int(window_days))
                effective_start = max(requested_start, earliest_ts)
                first_pass = self.runtime.replay.run_portfolio(
                    symbols=symbols,
                    from_ts=effective_start.isoformat(),
                    to_ts=latest_ts.isoformat(),
                    config_override=override_config,
                    refresh=False,
                    signal_stream=stream,
                )
                if not first_pass.invariants["passed"]:
                    failed_reasons.append(f"ledger_invariants:{window_days}d")
                if first_pass.max_drawdown_pct > 4.0:
                    failed_reasons.append(f"drawdown_limit:{window_days}d")

                completed_trades_total += first_pass.completed_trades
                summary = {
                    "window_days": int(window_days),
                    "requested_from": requested_start.isoformat(),
                    "effective_from": effective_start.isoformat(),
                    "to": latest_ts.isoformat(),
                    "truncated_to_available_history": bool(effective_start > requested_start),
                    "deterministic": None,
                    "deterministic_checked": False,
                    "trades": first_pass.trades,
                    "completed_trades": first_pass.completed_trades,
                    "fills": first_pass.fills,
                    "return_pct": first_pass.return_pct,
                    "max_drawdown_pct": first_pass.max_drawdown_pct,
                    "realized_pnl": first_pass.realized_pnl,
                    "unrealized_pnl": first_pass.unrealized_pnl,
                    "exposure_pct": first_pass.exposure_pct,
                    "turnover": first_pass.turnover,
                    "action_counts": first_pass.action_counts,
                    "reason_code_counts": first_pass.reason_code_counts,
                    "blocking_reasons_by_symbol": first_pass.blocking_reasons_by_symbol,
                    "opportunity_diagnostics": first_pass.opportunity_diagnostics,
                    "per_asset": first_pass.per_asset,
                    "invariants": first_pass.invariants,
                    "deterministic_signature": first_pass.deterministic_signature,
                }
                window_results.append(summary)

            if completed_trades_total < 2:
                failed_reasons.append("completed_trades_lt_2")

            if not failed_reasons:
                for idx, window_days in enumerate(windows):
                    second_pass = self.runtime.replay.run_portfolio(
                        symbols=symbols,
                        from_ts=window_results[idx]["effective_from"],
                        to_ts=window_results[idx]["to"],
                        config_override=override_config,
                        refresh=False,
                        signal_stream=stream,
                    )
                    deterministic = (
                        window_results[idx]["deterministic_signature"]
                        == second_pass.deterministic_signature
                    )
                    window_results[idx]["deterministic"] = deterministic
                    window_results[idx]["deterministic_checked"] = True
                    if not deterministic:
                        failed_reasons.append(f"non_deterministic:{window_days}d")

            ranking = self._ranking_metrics(window_results)
            result = {
                **candidate,
                "passed": not failed_reasons,
                "failed_reasons": sorted(set(failed_reasons)),
                "completed_trades_total": completed_trades_total,
                "ranking": ranking,
                "windows": window_results,
            }
            candidate_results.append(result)
            window_summaries[candidate["id"]] = window_results

        leaderboard = sorted(candidate_results, key=self._leaderboard_sort_key)
        baseline = next(item for item in candidate_results if item["id"] == "baseline")
        recommendation = self._recommendation(leaderboard, baseline)
        current_live_state = self._current_live_state(symbols, latest_ts)

        report = {
            "generated_at": to_iso(now_utc()),
            "symbols": symbols,
            "windows": windows,
            "latest_common_close": latest_ts.isoformat(),
            "earliest_common_close": earliest_ts.isoformat(),
            "current_live_state": current_live_state,
            "baseline": baseline,
            "leaderboard": leaderboard,
            "recommendation": recommendation,
            "search_policy": {
                "type": "bounded_curated_matrix",
                "candidate_count": len(candidate_set),
                "notes": [
                    "Baseline included explicitly.",
                    "Trend, trigger, risk, and guardrail variants are drawn only from the approved candidate values.",
                    "The default matrix is intentionally representative rather than exhaustive so the report remains runnable on the current intraday corpus.",
                    "Winning parameters are not applied automatically.",
                ],
            },
            "limitations": [
                "Current intraday evidence is about 30 days deep because Kraken OHLC is the active fallback source.",
                "Rolling windows are therefore limited to 7d, 14d, and 30d on the frozen local candle corpus.",
                "Report rankings emphasize robustness over absolute return.",
            ],
        }
        artifact_paths = self._write_artifacts(
            report=report,
            candidate_results=candidate_results,
            window_summaries=window_summaries,
            top=top,
        )
        report["artifacts"] = artifact_paths
        write_json(self.config.tuning_dir / "latest_tuning_report.json", report)
        return report

    def _parameter_snapshot(self, config: AthenaBotConfig) -> dict:
        return {key: getattr(config, key) for key in self.TUNING_KEYS}

    def _candidate_key(self, parameters: dict) -> tuple:
        return tuple((key, parameters[key]) for key in self.TUNING_KEYS)

    def _append_candidate(
        self,
        candidates: list[dict],
        seen: set[tuple],
        candidate_id: str,
        label: str,
        kind: str,
        baseline: dict,
        overrides: dict,
    ) -> None:
        parameters = dict(baseline)
        parameters.update(overrides)
        if parameters["trend_4h_fast_ema"] >= parameters["trend_4h_slow_ema"]:
            return
        key = self._candidate_key(parameters)
        if key in seen:
            return
        seen.add(key)
        candidates.append(
            {
                "id": candidate_id,
                "label": label,
                "kind": kind,
                "overrides": overrides,
                "parameters": parameters,
            }
        )

    def _ranking_metrics(self, window_results: list[dict]) -> dict:
        returns = [window["return_pct"] for window in window_results]
        drawdowns = [window["max_drawdown_pct"] for window in window_results]
        turnovers = [window["turnover"] for window in window_results]
        return {
            "worst_window_drawdown": round(max(drawdowns) if drawdowns else 0.0, 4),
            "non_negative_windows": int(sum(1 for value in returns if value >= 0)),
            "median_window_return": round(statistics.median(returns) if returns else 0.0, 4),
            "avg_turnover": round(statistics.mean(turnovers) if turnovers else 0.0, 4),
        }

    def _leaderboard_sort_key(self, candidate: dict) -> tuple:
        ranking = candidate["ranking"]
        if candidate["passed"]:
            return (
                0,
                ranking["worst_window_drawdown"],
                -ranking["non_negative_windows"],
                -ranking["median_window_return"],
                ranking["avg_turnover"],
                candidate["id"],
            )
        return (
            1,
            len(candidate["failed_reasons"]),
            candidate["ranking"]["worst_window_drawdown"],
            -candidate["ranking"]["non_negative_windows"],
            candidate["id"],
        )

    def _recommendation(self, leaderboard: list[dict], baseline: dict) -> dict:
        top_valid = next((item for item in leaderboard if item["passed"]), baseline)
        deltas = self._parameter_deltas(baseline["parameters"], top_valid["parameters"])
        baseline_rank = baseline["ranking"]
        top_rank = top_valid["ranking"]
        improves_first = top_rank["worst_window_drawdown"] < baseline_rank["worst_window_drawdown"]
        improves_second = top_rank["non_negative_windows"] > baseline_rank["non_negative_windows"]
        ties_or_better_first = top_rank["worst_window_drawdown"] <= baseline_rank["worst_window_drawdown"]
        ties_or_better_second = top_rank["non_negative_windows"] >= baseline_rank["non_negative_windows"]

        if top_valid["id"] != "baseline" and improves_first and improves_second:
            decision = "adopt"
            rationale = "Top candidate improved the first two robustness dimensions versus baseline."
        elif top_valid["id"] != "baseline" and ties_or_better_first and ties_or_better_second and deltas:
            decision = "watch"
            rationale = "Top candidate did not clear the full adoption bar, but it matched or improved the first two robustness dimensions without forcing a config change."
        else:
            decision = "keep baseline"
            rationale = "No candidate beat baseline on the first two robustness dimensions, so current defaults remain the recommendation."
            top_valid = baseline
            deltas = {}

        return {
            "decision": decision,
            "candidate_id": top_valid["id"],
            "candidate_label": top_valid["label"],
            "parameter_deltas": deltas,
            "rationale": rationale,
            "confidence": "moderate" if decision != "adopt" else "measured",
            "limitations_note": "Confidence is capped by the current ~30 day intraday horizon and Kraken-fallback market data coverage.",
        }

    def _parameter_deltas(self, baseline: dict, candidate: dict) -> dict:
        return {
            key: {"from": baseline[key], "to": candidate[key]}
            for key in self.TUNING_KEYS
            if baseline[key] != candidate[key]
        }

    def _current_live_state(self, symbols: list[str], latest_ts: pd.Timestamp) -> dict:
        latest_scan = self.runtime.ledger.read_latest_scan()
        freshness = {
            symbol: self.runtime.bar_store.data_health(symbol, "1h").to_dict()
            for symbol in symbols
        }
        data_horizon = {}
        for symbol in symbols:
            bars = self.runtime.bar_store.load_bars(symbol, "1h")
            if bars.empty:
                data_horizon[symbol] = {"bars": 0, "hours": 0.0}
                continue
            horizon_hours = (
                pd.Timestamp(bars["ts_close"].iloc[-1]) - pd.Timestamp(bars["ts_open"].iloc[0])
            ).total_seconds() / 3600.0
            data_horizon[symbol] = {
                "bars": int(len(bars)),
                "hours": round(horizon_hours, 2),
                "first_open": pd.Timestamp(bars["ts_open"].iloc[0]).isoformat(),
                "last_close": pd.Timestamp(bars["ts_close"].iloc[-1]).isoformat(),
            }
        return {
            "latest_common_close": latest_ts.isoformat(),
            "freshness": freshness,
            "latest_scan": latest_scan,
            "data_horizon": data_horizon,
        }

    def _latest_common_close(self, symbols: list[str]) -> str:
        closes = []
        for symbol in symbols:
            bars = self.runtime.bar_store.load_bars(symbol, "1h")
            if bars.empty:
                raise ValueError(f"No 1h bars available for {symbol}")
            closes.append(pd.Timestamp(bars["ts_close"].iloc[-1]))
        return min(closes).isoformat()

    def _earliest_common_close(self, symbols: list[str]) -> str:
        closes = []
        for symbol in symbols:
            bars = self.runtime.bar_store.load_bars(symbol, "1h")
            if bars.empty:
                raise ValueError(f"No 1h bars available for {symbol}")
            closes.append(pd.Timestamp(bars["ts_close"].iloc[0]))
        return max(closes).isoformat()

    def _write_artifacts(
        self,
        report: dict,
        candidate_results: list[dict],
        window_summaries: OrderedDict[str, list[dict]],
        top: int,
    ) -> dict:
        tuning_dir = self.config.tuning_dir
        tuning_dir.mkdir(parents=True, exist_ok=True)

        leaderboard = report["leaderboard"]
        report_json_path = tuning_dir / "latest_tuning_report.json"
        report_md_path = tuning_dir / "latest_tuning_report.md"
        candidate_matrix_path = tuning_dir / "candidate_matrix.json"
        window_summaries_path = tuning_dir / "window_summaries.json"

        write_json(candidate_matrix_path, {"candidates": candidate_results})
        write_json(window_summaries_path, dict(window_summaries))
        report_md_path.write_text(
            self._render_markdown_report(report, top=top),
            encoding="utf-8",
        )

        return {
            "report_json": str(report_json_path),
            "report_markdown": str(report_md_path),
            "candidate_matrix": str(candidate_matrix_path),
            "window_summaries": str(window_summaries_path),
        }

    def _render_markdown_report(self, report: dict, top: int) -> str:
        baseline = report["baseline"]
        baseline_window = max(baseline["windows"], key=lambda item: item["window_days"])
        recommendation = report["recommendation"]
        leaderboard = report["leaderboard"][:top]
        lines = [
            "# Athena Bot Portfolio Tuning Report",
            "",
            f"Generated: {report['generated_at']}",
            f"Latest common close: {report['latest_common_close']}",
            f"Universe: {', '.join(report['symbols'])}",
            "",
            "## Current Live State Snapshot",
            f"- Latest common close: {report['current_live_state']['latest_common_close']}",
            f"- Latest scan command: {report['current_live_state']['latest_scan'].get('command', 'none')}",
            f"- Candidate search policy: {report['search_policy']['type']} ({report['search_policy']['candidate_count']} candidates)",
            "",
            "## Baseline Rolling Windows",
            "| Window | Return % | Max DD % | Completed Trades | Exposure % | Turnover |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
        for window in baseline["windows"]:
            lines.append(
                f"| {window['window_days']}d | {window['return_pct']:.4f} | {window['max_drawdown_pct']:.4f} | {window['completed_trades']} | {window['exposure_pct']:.4f} | {window['turnover']:.4f} |"
            )

        lines.extend([
            "",
            "## Per-Asset Attribution (Baseline Longest Window)",
            "| Symbol | Return Contribution % | Realized PnL | Unrealized PnL | Trades | Wins | Losses | Avg Hold Hours | Avg Stop Distance % | Stop Hits |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ])
        for symbol in report["symbols"]:
            asset = baseline_window["per_asset"].get(symbol, {})
            lines.append(
                f"| {symbol} | {asset.get('return_contribution_pct', 0.0):.4f} | {asset.get('realized_pnl', 0.0):.4f} | {asset.get('unrealized_pnl', 0.0):.4f} | {asset.get('trade_count', 0)} | {asset.get('win_count', 0)} | {asset.get('loss_count', 0)} | {asset.get('avg_hold_hours', 0.0):.4f} | {asset.get('avg_stop_distance_pct', 0.0):.4f} | {asset.get('stop_hit_count', 0)} |"
            )

        lines.extend([
            "",
            "## Top Blocking Reasons By Symbol (Baseline Longest Window)",
        ])
        for symbol in report["symbols"]:
            reason_counts = baseline_window["blocking_reasons_by_symbol"].get(symbol, {})
            ordered = sorted(reason_counts.items(), key=lambda item: (-item[1], item[0]))[:5]
            if ordered:
                rendered = ", ".join(f"{name}={count}" for name, count in ordered)
            else:
                rendered = "none"
            lines.append(f"- {symbol}: {rendered}")

        lines.extend([
            "",
            "## Candidate Leaderboard",
            "| Rank | Candidate | Status | Worst DD % | Non-Neg Windows | Median Return % | Avg Turnover | Completed Trades |",
            "| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |",
        ])
        for idx, candidate in enumerate(leaderboard, start=1):
            status = "PASS" if candidate["passed"] else f"FAIL ({'; '.join(candidate['failed_reasons'])})"
            ranking = candidate["ranking"]
            lines.append(
                f"| {idx} | {candidate['label']} | {status} | {ranking['worst_window_drawdown']:.4f} | {ranking['non_negative_windows']} | {ranking['median_window_return']:.4f} | {ranking['avg_turnover']:.4f} | {candidate['completed_trades_total']} |"
            )

        lines.extend([
            "",
            "## Recommendation Summary",
            f"- Decision: {recommendation['decision']}",
            f"- Candidate: {recommendation['candidate_label']} ({recommendation['candidate_id']})",
            f"- Rationale: {recommendation['rationale']}",
            f"- Confidence: {recommendation['confidence']}",
            f"- Limitation note: {recommendation['limitations_note']}",
            "- Suggested parameter deltas:",
        ])
        if recommendation["parameter_deltas"]:
            for key, delta in recommendation["parameter_deltas"].items():
                lines.append(f"  - {key}: {delta['from']} -> {delta['to']}")
        else:
            lines.append("  - none")

        lines.extend([
            "",
            "## Opportunity Diagnostics (Baseline Longest Window)",
            "| Symbol | Blocked By Trigger | Blocked By Corridor | Blocked By Portfolio Risk Cap |",
            "| --- | ---: | ---: | ---: |",
        ])
        for symbol in report["symbols"]:
            opportunity = baseline_window["opportunity_diagnostics"]["by_symbol"].get(symbol, {})
            lines.append(
                f"| {symbol} | {opportunity.get('blocked_by_trigger', 0)} | {opportunity.get('blocked_by_corridor', 0)} | {opportunity.get('blocked_by_portfolio_risk_cap', 0)} |"
            )

        lines.extend([
            "",
            "## Limitations",
        ])
        for note in report["limitations"]:
            lines.append(f"- {note}")
        return "\n".join(lines) + "\n"
