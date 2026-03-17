from __future__ import annotations

from datetime import timedelta
from typing import Iterable

import requests

from .config import AthenaBotConfig
from .models import Candle
from .utils import latest_closed_bar, parse_ts, timeframe_delta, to_iso


class MarketDataProvider:
    """Fetch incremental OHLCV data from Binance spot market data."""

    def __init__(self, config: AthenaBotConfig | None = None):
        self.config = config or AthenaBotConfig()
        self.session = requests.Session()

    def fetch(
        self,
        symbol: str,
        timeframe: str,
        since_ts: str | None = None,
    ) -> list[Candle]:
        if timeframe not in ("1h", "4h"):
            raise ValueError(f"Unsupported timeframe: {timeframe}")

        exchange_symbol = self.config.source_symbols[symbol]
        delta = timeframe_delta(timeframe)
        end_bound = latest_closed_bar(timeframe=timeframe)
        start_dt = self._resolve_start(since_ts, delta, end_bound)
        if start_dt >= end_bound:
            return []

        candles: list[Candle] = []
        cursor = start_dt
        while cursor < end_bound:
            chunk = self._fetch_chunk(symbol, exchange_symbol, timeframe, cursor, end_bound)
            if not chunk:
                break
            parsed = list(self._parse_klines(symbol, timeframe, chunk))
            if not parsed:
                break
            candles.extend(parsed)
            next_open = parse_ts(parsed[-1].ts_open)
            if next_open is None:
                break
            cursor = next_open + delta
        return candles

    def _resolve_start(self, since_ts: str | None, delta: timedelta, end_bound):
        if since_ts:
            since_dt = parse_ts(since_ts)
            if since_dt is None:
                raise ValueError("Invalid since_ts")
            return since_dt + delta
        return end_bound - timedelta(hours=self.config.default_history_hours)

    def _fetch_chunk(self, symbol: str, exchange_symbol: str, timeframe: str, start_dt, end_dt) -> list[list]:
        params = {
            "symbol": exchange_symbol,
            "interval": timeframe,
            "startTime": int(start_dt.timestamp() * 1000),
            "endTime": int(end_dt.timestamp() * 1000) - 1,
            "limit": 1000,
        }
        try:
            response = self.session.get(
                f"{self.config.binance_base_url}/api/v3/klines",
                params=params,
                timeout=self.config.request_timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, list):
                raise RuntimeError(f"Unexpected Binance payload: {payload}")
            return payload
        except requests.HTTPError as exc:
            status_code = getattr(exc.response, "status_code", None)
            if status_code not in {418, 429, 451}:
                raise
            return self._fetch_kraken_chunk(symbol, timeframe, start_dt)
        except requests.RequestException:
            return self._fetch_kraken_chunk(symbol, timeframe, start_dt)

    def _fetch_kraken_chunk(self, symbol: str, timeframe: str, start_dt) -> list[list]:
        pair = self.config.kraken_pairs[symbol]
        interval = 60 if timeframe == "1h" else 240
        response = self.session.get(
            f"{self.config.kraken_base_url}/0/public/OHLC",
            params={
                "pair": pair,
                "interval": interval,
                "since": int(start_dt.timestamp()),
            },
            timeout=self.config.request_timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("error"):
            raise RuntimeError(f"Kraken error: {payload['error']}")
        rows = []
        for key, value in payload.get("result", {}).items():
            if key == "last":
                continue
            rows = value
            break
        return [
            [
                int(row[0]) * 1000,
                row[1],
                row[2],
                row[3],
                row[4],
                row[6],
                int((int(row[0]) + int(timeframe[:-1]) * 3600) * 1000) - 1,
            ]
            for row in rows
        ]

    def _parse_klines(
        self, symbol: str, timeframe: str, payload: Iterable[list]
    ) -> Iterable[Candle]:
        closed_before = latest_closed_bar(timeframe=timeframe)
        for row in payload:
            open_ts = parse_ts(int(row[0]) / 1000)
            close_ts = parse_ts((int(row[6]) + 1) / 1000)
            if open_ts is None or close_ts is None:
                continue
            if close_ts > closed_before:
                continue
            yield Candle(
                symbol=symbol,
                timeframe=timeframe,
                ts_open=to_iso(open_ts),
                ts_close=to_iso(close_ts),
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=float(row[5]),
                source="market.ohlc",
            )
