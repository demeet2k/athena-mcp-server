"""
Third pass: Extend history for older coins using:
1. CoinGecko /coins/{id}/history endpoint (date-by-date, works on free tier)
2. Kraken API for early BTC/ETH/LTC/XRP/XLM/ZEC/XMR data
3. Also fetch HYPE data from CoinGecko date-by-date
"""

import requests
import pandas as pd
import time
import os
import sys
from datetime import datetime, timezone, timedelta

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(OUTPUT_DIR, "data")


def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    try:
        print(f"[{timestamp}] {msg}")
    except UnicodeEncodeError:
        print(f"[{timestamp}] {msg.encode('ascii', 'replace').decode()}")
    sys.stdout.flush()


# ── Kraken OHLCV ──────────────────────────────────────────────────────────────

def fetch_kraken_ohlcv(pair, interval=1440, since=0):
    """
    Fetch OHLCV from Kraken. interval=1440 for daily.
    Kraken returns max 720 candles per request.
    """
    base_url = "https://api.kraken.com/0/public/OHLC"
    all_rows = []
    current_since = since

    while True:
        params = {
            "pair": pair,
            "interval": interval,
            "since": current_since,
        }
        try:
            resp = requests.get(base_url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            if data.get("error") and len(data["error"]) > 0:
                log(f"  Kraken error: {data['error']}")
                break

            result = data.get("result", {})
            # The key varies by pair name
            pair_key = [k for k in result.keys() if k != "last"]
            if not pair_key:
                break

            candles = result[pair_key[0]]
            if not candles:
                break

            for c in candles:
                dt = datetime.fromtimestamp(c[0], tz=timezone.utc).strftime("%Y-%m-%d")
                all_rows.append({
                    "date": dt,
                    "open": float(c[1]),
                    "high": float(c[2]),
                    "low": float(c[3]),
                    "close": float(c[4]),
                    "volume": float(c[6]),  # c[5] is vwap, c[6] is volume
                    "trade_count": int(c[7]),
                })

            last_ts = result.get("last", 0)
            if last_ts <= current_since or len(candles) < 720:
                break
            current_since = last_ts

            time.sleep(1)

        except Exception as e:
            log(f"  Kraken error: {e}")
            break

    if not all_rows:
        return None

    df = pd.DataFrame(all_rows)
    df = df.drop_duplicates(subset=["date"], keep="last")
    df = df.sort_values("date").reset_index(drop=True)
    return df


# ── CoinGecko /history endpoint (single date) ────────────────────────────────

def fetch_coingecko_date_range(coin_id, start_date, end_date, step_days=7):
    """
    Fetch price data from CoinGecko using the /coins/{id}/history endpoint.
    This works on the free tier but only returns one day at a time.
    We sample every step_days to stay under rate limits.
    """
    url_template = f"https://api.coingecko.com/api/v3/coins/{coin_id}/history"
    rows = []

    current = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    request_count = 0
    while current <= end:
        date_str = current.strftime("%d-%m-%Y")  # CoinGecko wants dd-mm-yyyy

        try:
            params = {"date": date_str, "localization": "false"}
            resp = requests.get(url_template, params=params, timeout=30)

            if resp.status_code == 429:
                log(f"  Rate limited at {current.strftime('%Y-%m-%d')}. Waiting 60s...")
                time.sleep(60)
                continue

            resp.raise_for_status()
            data = resp.json()

            md = data.get("market_data", {})
            if md:
                rows.append({
                    "date": current.strftime("%Y-%m-%d"),
                    "price_usd": md.get("current_price", {}).get("usd"),
                    "market_cap_usd": md.get("market_cap", {}).get("usd"),
                    "total_volume_usd": md.get("total_volume", {}).get("usd"),
                })

            request_count += 1

            # Rate limiting: ~10/min on free tier
            if request_count % 8 == 0:
                time.sleep(12)
            else:
                time.sleep(7)

        except Exception as e:
            log(f"  Error for {current.strftime('%Y-%m-%d')}: {e}")
            time.sleep(10)

        current += timedelta(days=step_days)

    if not rows:
        return None

    df = pd.DataFrame(rows)
    df = df.dropna(subset=["price_usd"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


# ── Trading indicators ────────────────────────────────────────────────────────

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


def merge_and_save(symbol, early_df, filepath):
    """Merge early data with existing file and save."""
    if os.path.exists(filepath):
        existing_df = pd.read_csv(filepath)
        existing_start = existing_df["date"].min()

        # Only keep early data that's before existing data
        early_df = early_df[early_df["date"] < existing_start]

        if len(early_df) == 0:
            log(f"  No new earlier data to add for {symbol}")
            return

        log(f"  Adding {len(early_df)} earlier records to existing {len(existing_df)} records")

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


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    log("=" * 70)
    log("EXTENDING HISTORY WITH KRAKEN + COINGECKO DATE-BY-DATE")
    log("=" * 70)

    # Kraken pair mappings for major coins
    kraken_pairs = {
        "BTC": "XXBTZUSD",
        "ETH": "XETHZUSD",
        "LTC": "XLTCZUSD",
        "XRP": "XXRPZUSD",
        "XLM": "XXLMZUSD",
        "ZEC": "XZECZUSD",
        "XMR": "XXMRZUSD",
        "DOGE": "XDGUSD",
        "ADA": "ADAUSD",
        "LINK": "LINKUSD",
        "BCH": "BCHUSD",
        "TRX": "TRXUSD",
        "SOL": "SOLUSD",
        "BNB": "BNBUSD",  # May not exist on Kraken
    }

    # Process each coin with Kraken data
    for symbol, kraken_pair in kraken_pairs.items():
        filepath = os.path.join(DATA_DIR, f"{symbol}_full_history.csv")

        if not os.path.exists(filepath):
            log(f"\n--- {symbol}: No existing file, fetching full Kraken history ---")
        else:
            existing_df = pd.read_csv(filepath)
            existing_start = existing_df["date"].min()
            log(f"\n--- {symbol}: Current start={existing_start}, trying Kraken ({kraken_pair}) ---")

        try:
            kraken_df = fetch_kraken_ohlcv(kraken_pair, interval=1440, since=0)
            if kraken_df is not None and len(kraken_df) > 0:
                log(f"  Kraken returned {len(kraken_df)} records: {kraken_df['date'].iloc[0]} to {kraken_df['date'].iloc[-1]}")
                merge_and_save(symbol, kraken_df, filepath)
            else:
                log(f"  No Kraken data for {kraken_pair}")
        except Exception as e:
            log(f"  Kraken error: {e}")

        time.sleep(2)

    # Now handle HYPE using CoinGecko date-by-date
    log(f"\n--- HYPE: Fetching from CoinGecko date-by-date ---")
    hype_path = os.path.join(DATA_DIR, "HYPE_full_history.csv")
    try:
        # HYPE launched ~late 2024
        hype_df = fetch_coingecko_date_range("hyperliquid", "2024-11-01", "2026-02-09", step_days=1)
        if hype_df is not None and len(hype_df) > 0:
            log(f"  Got {len(hype_df)} records for HYPE")
            hype_df = add_trading_features(hype_df)
            hype_df.to_csv(hype_path, index=False)
            file_size_mb = os.path.getsize(hype_path) / (1024 * 1024)
            log(f"  SAVED: HYPE_full_history.csv ({len(hype_df)} rows, {file_size_mb:.2f} MB)")
        else:
            log(f"  No HYPE data obtained")
    except Exception as e:
        log(f"  Error: {e}")

    # Final summary
    log("\n" + "=" * 70)
    log("FINAL SUMMARY")
    log("=" * 70)

    import glob as gl
    files = gl.glob(os.path.join(DATA_DIR, "*_full_history.csv"))
    total_rows = 0
    total_size = 0

    log(f"\n{'Symbol':<8} {'Start':<12} {'End':<12} {'Days':>6} {'MB':>6}")
    log(f"{'-' * 50}")

    for filepath in sorted(files):
        filename = os.path.basename(filepath)
        symbol = filename.replace("_full_history.csv", "")
        df = pd.read_csv(filepath)
        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        total_rows += len(df)
        total_size += file_size_mb
        log(f"{symbol:<8} {df['date'].iloc[0]:<12} {df['date'].iloc[-1]:<12} {len(df):>6} {file_size_mb:>6.2f}")

    log(f"{'-' * 50}")
    log(f"TOTAL: {total_rows} data points, {total_size:.2f} MB across {len(files)} coins")


if __name__ == "__main__":
    main()
