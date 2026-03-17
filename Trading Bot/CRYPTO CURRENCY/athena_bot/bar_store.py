from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd

from .config import AthenaBotConfig
from .market_data import MarketDataProvider
from .models import Candle
from .utils import latest_closed_bar, load_dataframe, parse_ts, save_dataframe, timeframe_delta


@dataclass(slots=True)
class DataHealth:
    symbol: str
    timeframe: str
    is_fresh: bool
    has_duplicates: bool
    freshest_close: str | None
    reason_codes: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


class BarStore:
    def __init__(
        self,
        config: AthenaBotConfig | None = None,
        provider: MarketDataProvider | None = None,
    ):
        self.config = config or AthenaBotConfig()
        self.provider = provider or MarketDataProvider(self.config)

    def load_bars(self, symbol: str, timeframe: str) -> pd.DataFrame:
        path = self.config.candle_path(symbol, timeframe)
        df = load_dataframe(path)
        if df.empty:
            return df
        for column in ("open", "high", "low", "close", "volume"):
            df[column] = pd.to_numeric(df[column], errors="coerce")
        return df.sort_values("ts_open").reset_index(drop=True)

    def refresh_symbol(self, symbol: str, since_ts: str | None = None) -> dict:
        existing_1h = self.load_bars(symbol, "1h")
        effective_since = since_ts
        if effective_since is None and not existing_1h.empty:
            effective_since = existing_1h["ts_open"].iloc[-1].isoformat()

        new_candles = self.provider.fetch(symbol, "1h", since_ts=effective_since)
        merged_1h = self.merge_bars(existing_1h, new_candles)
        save_dataframe(self.config.candle_path(symbol, "1h"), merged_1h)

        derived_4h = self.aggregate_to_4h(merged_1h, symbol)
        save_dataframe(self.config.candle_path(symbol, "4h"), derived_4h)

        freshest_close = None
        if not merged_1h.empty:
            freshest_close = merged_1h["ts_close"].iloc[-1].isoformat()
        return {
            "symbol": symbol,
            "new_1h_bars": len(new_candles),
            "total_1h_bars": len(merged_1h),
            "total_4h_bars": len(derived_4h),
            "freshest_close": freshest_close,
        }

    def refresh_all(
        self, symbols: list[str] | tuple[str, ...], since_ts: str | None = None
    ) -> list[dict]:
        return [self.refresh_symbol(symbol, since_ts=since_ts) for symbol in symbols]

    def merge_bars(self, existing_df: pd.DataFrame, new_candles: list[Candle]) -> pd.DataFrame:
        incoming = pd.DataFrame([candle.to_dict() for candle in new_candles])
        if incoming.empty and not existing_df.empty:
            return existing_df.sort_values("ts_open").drop_duplicates("ts_open").reset_index(drop=True)
        if incoming.empty:
            return incoming
        incoming["ts_open"] = pd.to_datetime(incoming["ts_open"], utc=True)
        incoming["ts_close"] = pd.to_datetime(incoming["ts_close"], utc=True)
        combined = pd.concat([existing_df, incoming], ignore_index=True)
        combined = combined.sort_values("ts_open").drop_duplicates("ts_open", keep="last")
        return combined.reset_index(drop=True)

    def aggregate_to_4h(self, df_1h: pd.DataFrame, symbol: str) -> pd.DataFrame:
        if df_1h.empty:
            return pd.DataFrame(
                columns=[
                    "symbol",
                    "timeframe",
                    "ts_open",
                    "ts_close",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "source",
                ]
            )

        frame = df_1h.copy().sort_values("ts_open")
        frame = frame.set_index("ts_open")
        aggregated = frame.resample("4h", label="left", closed="left").agg(
            open=("open", "first"),
            high=("high", "max"),
            low=("low", "min"),
            close=("close", "last"),
            volume=("volume", "sum"),
            symbol=("symbol", "last"),
            source=("source", "last"),
        )
        counts = frame["close"].resample("4h", label="left", closed="left").count()
        aggregated = aggregated[counts >= 4].dropna(subset=["open", "high", "low", "close"])
        aggregated = aggregated.reset_index()
        aggregated["ts_close"] = aggregated["ts_open"] + pd.Timedelta(hours=4)
        aggregated["symbol"] = symbol
        aggregated["timeframe"] = "4h"
        aggregated["source"] = "derived.1h"
        return aggregated[
            ["symbol", "timeframe", "ts_open", "ts_close", "open", "high", "low", "close", "volume", "source"]
        ].reset_index(drop=True)

    def data_health(self, symbol: str, timeframe: str, expected_close=None) -> DataHealth:
        df = self.load_bars(symbol, timeframe)
        return self.data_health_from_frame(symbol, timeframe, df, expected_close=expected_close)

    def data_health_from_frame(
        self,
        symbol: str,
        timeframe: str,
        df: pd.DataFrame,
        expected_close=None,
    ) -> DataHealth:
        reasons: list[str] = []
        if df.empty:
            return DataHealth(symbol, timeframe, False, False, None, ["no_bars"])

        has_duplicates = df["ts_open"].duplicated().any()
        if has_duplicates:
            reasons.append("duplicate_bars")

        freshest_close = pd.Timestamp(df["ts_close"].iloc[-1]).to_pydatetime()
        expected_close = expected_close or latest_closed_bar(timeframe=timeframe)
        is_fresh = freshest_close >= expected_close
        if not is_fresh:
            reasons.append("stale_bars")

        return DataHealth(
            symbol=symbol,
            timeframe=timeframe,
            is_fresh=is_fresh and not has_duplicates,
            has_duplicates=bool(has_duplicates),
            freshest_close=freshest_close.isoformat(),
            reason_codes=reasons,
        )

    def bars_for_window(
        self,
        symbol: str,
        start_ts: str | None = None,
        end_ts: str | None = None,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        bars_1h = self.load_bars(symbol, "1h")
        bars_4h = self.load_bars(symbol, "4h")
        if start_ts:
            start_dt = parse_ts(start_ts)
            bars_1h = bars_1h[bars_1h["ts_close"] >= start_dt]
            bars_4h = bars_4h[bars_4h["ts_close"] >= start_dt]
        if end_ts:
            end_dt = parse_ts(end_ts)
            bars_1h = bars_1h[bars_1h["ts_close"] <= end_dt]
            bars_4h = bars_4h[bars_4h["ts_close"] <= end_dt]
        return bars_1h.reset_index(drop=True), bars_4h.reset_index(drop=True)
