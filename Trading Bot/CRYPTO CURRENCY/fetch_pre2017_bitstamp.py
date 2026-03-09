"""
Fifth pass: Get pre-2017 data from Bitstamp (oldest major exchange, public API).
Also extends BCH, DOGE, XMR using other Binance pairs.
Bitstamp has BTC data from 2011, ETH from 2017, LTC from 2013, XRP from 2014.
"""

import requests
import pandas as pd
import time
import os
import sys
from datetime import datetime, timezone

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(OUTPUT_DIR, "data")


def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    try:
        print(f"[{timestamp}] {msg}")
    except UnicodeEncodeError:
        print(f"[{timestamp}] {msg.encode('ascii', 'replace').decode()}")
    sys.stdout.flush()


def fetch_bitstamp_ohlcv(pair, step=86400, start_ts=0, limit=1000):
    """
    Fetch OHLCV from Bitstamp.
    step=86400 for daily candles.
    Returns max 1000 per request. Paginate by moving start.
    """
    base_url = f"https://www.bitstamp.net/api/v2/ohlc/{pair}/"
    all_rows = []
    current_start = start_ts
    end_ts = int(datetime.now(timezone.utc).timestamp())

    while current_start < end_ts:
        params = {
            "step": step,
            "start": current_start,
            "limit": limit,
        }
        try:
            resp = requests.get(base_url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            ohlc = data.get("data", {}).get("ohlc", [])

            if not ohlc:
                break

            for c in ohlc:
                ts = int(c["timestamp"])
                dt = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
                all_rows.append({
                    "date": dt,
                    "open": float(c["open"]),
                    "high": float(c["high"]),
                    "low": float(c["low"]),
                    "close": float(c["close"]),
                    "volume": float(c["volume"]),
                })

            # Move to after the last candle
            last_ts = int(ohlc[-1]["timestamp"])
            if last_ts <= current_start:
                break
            current_start = last_ts + step

            if len(ohlc) < limit:
                break

            time.sleep(1)

        except Exception as e:
            log(f"  Bitstamp error for {pair}: {e}")
            break

    if not all_rows:
        return None

    df = pd.DataFrame(all_rows)
    df = df.drop_duplicates(subset=["date"], keep="last")
    df = df.sort_values("date").reset_index(drop=True)
    return df


def add_trading_features(df):
    if "close" not in df.columns and "price_usd" in df.columns:
        df["close"] = df["price_usd"]
    if "close" not in df.columns:
        return df

    df["daily_return_pct"] = df["close"].pct_change() * 100
    for window in [7, 14, 21, 30, 50, 100, 200]:
        df[f"sma_{window}"] = df["close"].rolling(window=window).mean()
    for window in [12, 26, 50, 200]:
        df[f"ema_{window}"] = df["close"].ewm(span=window, adjust=False).mean()
    df["macd"] = df["ema_12"] - df["ema_26"]
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_histogram"] = df["macd"] - df["macd_signal"]
    df["bb_middle"] = df["close"].rolling(window=20).mean()
    bb_std = df["close"].rolling(window=20).std()
    df["bb_upper"] = df["bb_middle"] + (bb_std * 2)
    df["bb_lower"] = df["bb_middle"] - (bb_std * 2)
    df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_middle"]
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["rsi_14"] = 100 - (100 / (1 + rs))
    df["volatility_7d"] = df["daily_return_pct"].rolling(window=7).std()
    df["volatility_30d"] = df["daily_return_pct"].rolling(window=30).std()
    df["rolling_ath"] = df["close"].cummax()
    df["drawdown_from_ath_pct"] = ((df["close"] - df["rolling_ath"]) / df["rolling_ath"]) * 100
    vol_col = "total_volume_usd" if "total_volume_usd" in df.columns else "volume" if "volume" in df.columns else None
    if vol_col:
        df["volume_sma_20"] = df[vol_col].rolling(window=20).mean()
        df["volume_ratio"] = df[vol_col] / df["volume_sma_20"]
    return df


def merge_early_data(symbol, early_df):
    filepath = os.path.join(DATA_DIR, f"{symbol}_full_history.csv")
    if os.path.exists(filepath):
        existing_df = pd.read_csv(filepath)
        existing_start = existing_df["date"].min()
        early_df = early_df[early_df["date"] < existing_start]
        if len(early_df) == 0:
            log(f"  No new earlier data for {symbol}")
            return
        log(f"  Prepending {len(early_df)} records (before {existing_start}) to {len(existing_df)} existing")
        merged = pd.concat([early_df, existing_df], ignore_index=True)
        merged = merged.drop_duplicates(subset=["date"], keep="last")
        merged = merged.sort_values("date").reset_index(drop=True)
    else:
        merged = early_df

    merged = add_trading_features(merged)
    merged.to_csv(filepath, index=False)
    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
    log(f"  SAVED: {symbol}_full_history.csv ({len(merged)} rows, {file_size_mb:.2f} MB)")
    log(f"  History: {merged['date'].iloc[0]} to {merged['date'].iloc[-1]}")


def main():
    log("=" * 70)
    log("FETCHING PRE-2017 DATA FROM BITSTAMP")
    log("=" * 70)

    # Bitstamp pairs and their earliest available dates
    bitstamp_coins = [
        {"symbol": "BTC", "pair": "btcusd", "start_ts": 1315180800},   # ~Sep 2011
        {"symbol": "ETH", "pair": "ethusd", "start_ts": 1484265600},   # ~Jan 2017
        {"symbol": "LTC", "pair": "ltcusd", "start_ts": 1377993600},   # ~Sep 2013
        {"symbol": "XRP", "pair": "xrpusd", "start_ts": 1396310400},   # ~Apr 2014
        {"symbol": "BCH", "pair": "bchusd", "start_ts": 1501027200},   # ~Jul 2017
        {"symbol": "LINK", "pair": "linkusd", "start_ts": 1546300800}, # ~Jan 2019
        {"symbol": "XLM", "pair": "xlmusd", "start_ts": 1525132800},   # ~May 2018
        {"symbol": "DOGE", "pair": "dogeusd", "start_ts": 1609459200}, # ~Jan 2021
        {"symbol": "ADA", "pair": "adausd", "start_ts": 1609459200},   # ~Jan 2021
        {"symbol": "SOL", "pair": "solusd", "start_ts": 1609459200},   # ~Jan 2021
        {"symbol": "ZEC", "pair": "zecusd", "start_ts": 1609459200},   # ~Jan 2021
    ]

    for coin in bitstamp_coins:
        symbol = coin["symbol"]
        filepath = os.path.join(DATA_DIR, f"{symbol}_full_history.csv")

        if os.path.exists(filepath):
            existing_df = pd.read_csv(filepath)
            existing_start = existing_df["date"].min()
            log(f"\n--- {symbol}: Current start={existing_start} ---")
        else:
            log(f"\n--- {symbol}: No file yet ---")
            existing_start = "9999-99-99"

        log(f"  Fetching from Bitstamp ({coin['pair']})...")
        try:
            bitstamp_df = fetch_bitstamp_ohlcv(coin["pair"], start_ts=coin["start_ts"])
            if bitstamp_df is not None and len(bitstamp_df) > 0:
                bitstamp_start = bitstamp_df["date"].iloc[0]
                bitstamp_end = bitstamp_df["date"].iloc[-1]
                log(f"  -> Got {len(bitstamp_df)} records: {bitstamp_start} to {bitstamp_end}")
                merge_early_data(symbol, bitstamp_df)
            else:
                log(f"  -> No Bitstamp data")
        except Exception as e:
            log(f"  -> Error: {e}")

        time.sleep(2)

    # Also try XMR from Bitstamp (not listed, but try)
    # And use Bybit for more XMR history
    log(f"\n--- XMR: Trying Bybit for extended history ---")
    try:
        base_url = "https://api.bybit.com/v5/market/kline"
        all_rows = []
        end_ts = int(datetime.now(timezone.utc).timestamp() * 1000)

        current_end = end_ts
        for batch in range(50):
            params = {
                "category": "spot",
                "symbol": "XMRUSDT",
                "interval": "D",
                "end": current_end,
                "limit": 200,
            }
            resp = requests.get(base_url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            result = data.get("result", {}).get("list", [])
            if not result:
                break

            for k in result:
                ts = int(k[0])
                dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
                all_rows.append({
                    "date": dt,
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "volume": float(k[5]),
                })

            oldest_ts = int(result[-1][0])
            if oldest_ts >= current_end:
                break
            current_end = oldest_ts - 1

            if len(result) < 200:
                break
            time.sleep(0.5)

        if all_rows:
            xmr_df = pd.DataFrame(all_rows)
            xmr_df = xmr_df.drop_duplicates(subset=["date"], keep="last")
            xmr_df = xmr_df.sort_values("date").reset_index(drop=True)
            log(f"  Bybit XMR: {len(xmr_df)} records ({xmr_df['date'].iloc[0]} to {xmr_df['date'].iloc[-1]})")
            merge_early_data("XMR", xmr_df)
    except Exception as e:
        log(f"  XMR Bybit error: {e}")

    # Final summary
    log("\n" + "=" * 70)
    log("FINAL SUMMARY")
    log("=" * 70)

    import glob as gl
    files = gl.glob(os.path.join(DATA_DIR, "*_full_history.csv"))
    total_rows = 0
    total_size = 0

    log(f"\n{'Symbol':<8} {'Start':<12} {'End':<12} {'Days':>6} {'Cols':>5} {'MB':>6}")
    log(f"{'-' * 55}")

    for filepath in sorted(files):
        filename = os.path.basename(filepath)
        symbol = filename.replace("_full_history.csv", "")
        df = pd.read_csv(filepath)
        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        total_rows += len(df)
        total_size += file_size_mb
        log(f"{symbol:<8} {df['date'].iloc[0]:<12} {df['date'].iloc[-1]:<12} {len(df):>6} {len(df.columns):>5} {file_size_mb:>6.2f}")

    log(f"{'-' * 55}")
    log(f"TOTAL: {total_rows} data points, {total_size:.2f} MB across {len(files)} coins")
    log("\nDONE!")


if __name__ == "__main__":
    main()
