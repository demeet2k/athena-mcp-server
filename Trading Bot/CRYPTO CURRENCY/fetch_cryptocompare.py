"""
Final pass: Use CryptoCompare (min-api.cryptocompare.com) for pre-2017 data.
CryptoCompare is free (no key needed for basic endpoints) and has data
dating back to the earliest exchange listings.
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


def fetch_cryptocompare_daily(fsym, tsym="USD", limit=2000, toTs=None):
    """
    Fetch daily OHLCV from CryptoCompare.
    Max 2000 data points per request. Paginate backwards using toTs.
    """
    url = "https://min-api.cryptocompare.com/data/v2/histoday"
    all_rows = []
    current_toTs = toTs or int(datetime.now(timezone.utc).timestamp())
    seen_dates = set()

    for batch in range(20):  # Max 20 batches = 40000 days
        params = {
            "fsym": fsym,
            "tsym": tsym,
            "limit": limit,
            "toTs": current_toTs,
        }

        try:
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            if data.get("Response") == "Error":
                log(f"  CryptoCompare error: {data.get('Message', 'Unknown')}")
                break

            candles = data.get("Data", {}).get("Data", [])
            if not candles:
                break

            new_count = 0
            for c in candles:
                # Skip candles with 0 volume (no trading)
                if c.get("volumeto", 0) == 0 and c.get("close", 0) == 0:
                    continue

                dt = datetime.fromtimestamp(c["time"], tz=timezone.utc).strftime("%Y-%m-%d")
                if dt in seen_dates:
                    continue
                seen_dates.add(dt)
                new_count += 1

                all_rows.append({
                    "date": dt,
                    "open": float(c.get("open", 0)),
                    "high": float(c.get("high", 0)),
                    "low": float(c.get("low", 0)),
                    "close": float(c.get("close", 0)),
                    "volume": float(c.get("volumefrom", 0)),
                    "total_volume_usd": float(c.get("volumeto", 0)),
                })

            if new_count == 0:
                break

            # Move backwards
            earliest = min(c["time"] for c in candles)
            if earliest >= current_toTs:
                break
            current_toTs = earliest - 1

            log(f"  Batch {batch+1}: {new_count} new records, earliest: {datetime.fromtimestamp(earliest, tz=timezone.utc).strftime('%Y-%m-%d')}")

            time.sleep(1)

        except Exception as e:
            log(f"  CryptoCompare error: {e}")
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
        early_before = early_df[early_df["date"] < existing_start]
        if len(early_before) == 0:
            log(f"  No new earlier data for {symbol}")
            return
        log(f"  Prepending {len(early_before)} records (before {existing_start}) to {len(existing_df)} existing")
        merged = pd.concat([early_before, existing_df], ignore_index=True)
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
    log("FETCHING FULL HISTORY FROM CRYPTOCOMPARE")
    log("=" * 70)

    # All coins we want to extend
    coins = [
        {"symbol": "BTC", "cc_symbol": "BTC"},   # Data from ~2010
        {"symbol": "ETH", "cc_symbol": "ETH"},   # Data from ~2015
        {"symbol": "LTC", "cc_symbol": "LTC"},   # Data from ~2013
        {"symbol": "XRP", "cc_symbol": "XRP"},   # Data from ~2013
        {"symbol": "DOGE", "cc_symbol": "DOGE"}, # Data from ~2013
        {"symbol": "XLM", "cc_symbol": "XLM"},   # Data from ~2014
        {"symbol": "XMR", "cc_symbol": "XMR"},   # Data from ~2014
        {"symbol": "ZEC", "cc_symbol": "ZEC"},   # Data from ~2016
        {"symbol": "BCH", "cc_symbol": "BCH"},   # Data from ~2017
        {"symbol": "ADA", "cc_symbol": "ADA"},   # Data from ~2017
        {"symbol": "BNB", "cc_symbol": "BNB"},   # Data from ~2017
        {"symbol": "TRX", "cc_symbol": "TRX"},   # Data from ~2017
        {"symbol": "LINK", "cc_symbol": "LINK"}, # Data from ~2017
        {"symbol": "SOL", "cc_symbol": "SOL"},   # Data from ~2020
    ]

    for coin in coins:
        symbol = coin["symbol"]
        filepath = os.path.join(DATA_DIR, f"{symbol}_full_history.csv")

        if os.path.exists(filepath):
            existing_df = pd.read_csv(filepath)
            existing_start = existing_df["date"].min()
            log(f"\n--- {symbol}: Current start={existing_start} ---")
        else:
            log(f"\n--- {symbol}: No file yet ---")
            existing_start = "9999"

        log(f"  Fetching from CryptoCompare ({coin['cc_symbol']})...")
        cc_df = fetch_cryptocompare_daily(coin["cc_symbol"])

        if cc_df is not None and len(cc_df) > 0:
            log(f"  -> Total: {len(cc_df)} records: {cc_df['date'].iloc[0]} to {cc_df['date'].iloc[-1]}")
            merge_early_data(symbol, cc_df)
        else:
            log(f"  -> No CryptoCompare data")

        time.sleep(2)

    # Update the master summary
    log("\n" + "=" * 70)
    log("FINAL SUMMARY - ALL COINS")
    log("=" * 70)

    import glob as gl
    files = gl.glob(os.path.join(DATA_DIR, "*_full_history.csv"))
    total_rows = 0
    total_size = 0

    summary_rows = []
    log(f"\n{'Symbol':<8} {'Start':<12} {'End':<12} {'Days':>6} {'Cols':>5} {'MB':>6}")
    log(f"{'-' * 55}")

    for filepath in sorted(files):
        filename = os.path.basename(filepath)
        symbol = filename.replace("_full_history.csv", "")
        df = pd.read_csv(filepath)
        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        total_rows += len(df)
        total_size += file_size_mb
        start = df['date'].iloc[0]
        end = df['date'].iloc[-1]
        log(f"{symbol:<8} {start:<12} {end:<12} {len(df):>6} {len(df.columns):>5} {file_size_mb:>6.2f}")

        summary_rows.append({
            "symbol": symbol,
            "data_start": start,
            "data_end": end,
            "total_days": len(df),
            "columns": len(df.columns),
            "has_ohlcv": "open" in df.columns,
            "file": filename,
            "file_size_mb": round(file_size_mb, 2),
        })

    log(f"{'-' * 55}")
    log(f"TOTAL: {total_rows} data points, {total_size:.2f} MB across {len(files)} coins")

    # Save updated summary
    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(os.path.join(DATA_DIR, "00_DATA_SUMMARY.csv"), index=False)
    log(f"\nSummary saved to 00_DATA_SUMMARY.csv")
    log("DONE!")


if __name__ == "__main__":
    main()
