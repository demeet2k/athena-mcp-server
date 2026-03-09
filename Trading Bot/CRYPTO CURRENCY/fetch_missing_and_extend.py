"""
Second pass: Fetch missing coins and extend history for existing ones.
- Uses Binance alternative pairs (BTC pairs) for coins without USDT pairs
- Uses CoinGecko with aggressive retry/backoff for full history
- Uses CoinCap API as another free source
"""

import requests
import pandas as pd
import time
import json
import os
import sys
from datetime import datetime, timezone

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(OUTPUT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)


def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    try:
        print(f"[{timestamp}] {msg}")
    except UnicodeEncodeError:
        print(f"[{timestamp}] {msg.encode('ascii', 'replace').decode()}")
    sys.stdout.flush()


# ── Binance Klines (reusable) ──────────────────────────────────────────────────

def fetch_binance_klines(symbol, interval="1d", start_str="2017-01-01"):
    base_url = "https://api.binance.com/api/v3/klines"
    start_ts = int(datetime.strptime(start_str, "%Y-%m-%d").replace(
        tzinfo=timezone.utc).timestamp() * 1000)
    end_ts = int(datetime.now(timezone.utc).timestamp() * 1000)

    all_klines = []
    current_start = start_ts

    while current_start < end_ts:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": current_start,
            "endTime": end_ts,
            "limit": 1000,
        }
        try:
            resp = requests.get(base_url, params=params, timeout=30)
            resp.raise_for_status()
            klines = resp.json()
        except Exception as e:
            log(f"  Binance error for {symbol}: {e}")
            break

        if not klines:
            break

        all_klines.extend(klines)
        current_start = klines[-1][6] + 1

        if len(klines) < 1000:
            break

        time.sleep(0.3)

    if not all_klines:
        return None

    rows = []
    for k in all_klines:
        dt = datetime.fromtimestamp(k[0] / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
        rows.append({
            "date": dt,
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5]),
            "close_time": k[6],
            "quote_volume": float(k[7]),
            "trade_count": int(k[8]),
            "taker_buy_base_volume": float(k[9]),
            "taker_buy_quote_volume": float(k[10]),
        })

    df = pd.DataFrame(rows)
    df = df.drop_duplicates(subset=["date"], keep="last")
    df = df.sort_values("date").reset_index(drop=True)
    return df


# ── CoinGecko with aggressive retry ───────────────────────────────────────────

def fetch_coingecko_history_retry(coin_id, max_retries=5, initial_delay=30):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": "max",
        "interval": "daily",
    }

    for attempt in range(max_retries):
        try:
            resp = requests.get(url, params=params, timeout=60)
            if resp.status_code == 429:
                wait = initial_delay * (2 ** attempt)
                log(f"  Rate limited (429). Waiting {wait}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait)
                continue
            elif resp.status_code == 401:
                log(f"  CoinGecko market_chart requires API key for days=max. Trying days=365...")
                # Try a smaller range
                params["days"] = "365"
                resp2 = requests.get(url, params=params, timeout=60)
                if resp2.status_code == 200:
                    return _parse_coingecko_response(resp2.json())
                else:
                    log(f"  Also failed with days=365: {resp2.status_code}")
                    return None

            resp.raise_for_status()
            return _parse_coingecko_response(resp.json())
        except requests.exceptions.HTTPError as e:
            log(f"  HTTP error: {e}")
            if attempt < max_retries - 1:
                wait = initial_delay * (2 ** attempt)
                log(f"  Waiting {wait}s before retry...")
                time.sleep(wait)
        except Exception as e:
            log(f"  Error: {e}")
            return None

    return None


def _parse_coingecko_response(data):
    prices = data.get("prices", [])
    market_caps = data.get("market_caps", [])
    total_volumes = data.get("total_volumes", [])

    rows = []
    for i in range(len(prices)):
        ts = prices[i][0]
        dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
        row = {
            "date": dt,
            "price_usd": prices[i][1],
            "market_cap_usd": market_caps[i][1] if i < len(market_caps) else None,
            "total_volume_usd": total_volumes[i][1] if i < len(total_volumes) else None,
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    df = df.drop_duplicates(subset=["date"], keep="last")
    df = df.sort_values("date").reset_index(drop=True)
    return df


# ── CoinCap API (free, no key) ────────────────────────────────────────────────

def fetch_coincap_history(asset_id, interval="d1"):
    """
    Fetch historical data from CoinCap API.
    interval: d1 (daily). Max 2000 data points per request.
    """
    base_url = f"https://api.coincap.io/v2/assets/{asset_id}/history"

    # CoinCap allows start/end in ms. Fetch in chunks.
    all_rows = []
    end_ts = int(datetime.now(timezone.utc).timestamp() * 1000)
    # Go back to 2010 for maximum history
    start_ts = int(datetime(2010, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)
    chunk_ms = 2000 * 86400 * 1000  # ~2000 days in ms

    current_start = start_ts
    while current_start < end_ts:
        current_end = min(current_start + chunk_ms, end_ts)
        params = {
            "interval": interval,
            "start": current_start,
            "end": current_end,
        }
        try:
            resp = requests.get(base_url, params=params, timeout=30)
            if resp.status_code == 429:
                log(f"  CoinCap rate limited. Waiting 10s...")
                time.sleep(10)
                continue
            resp.raise_for_status()
            data = resp.json().get("data", [])
            if not data:
                current_start = current_end
                continue

            for d in data:
                dt = datetime.fromtimestamp(d["time"] / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
                all_rows.append({
                    "date": dt,
                    "price_usd": float(d["priceUsd"]),
                    "total_volume_usd": float(d.get("volumeUsd24Hr", 0)) if d.get("volumeUsd24Hr") else None,
                })
            current_start = current_end
            time.sleep(1)
        except Exception as e:
            log(f"  CoinCap error: {e}")
            current_start = current_end
            time.sleep(2)

    if not all_rows:
        return None

    df = pd.DataFrame(all_rows)
    df = df.drop_duplicates(subset=["date"], keep="last")
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

    if "total_volume_usd" in df.columns:
        df["volume_sma_20"] = df["total_volume_usd"].rolling(window=20).mean()
        df["volume_ratio"] = df["total_volume_usd"] / df["volume_sma_20"]
    elif "volume" in df.columns:
        df["volume_sma_20"] = df["volume"].rolling(window=20).mean()
        df["volume_ratio"] = df["volume"] / df["volume_sma_20"]

    return df


# ── MISSING COINS ──────────────────────────────────────────────────────────────

MISSING_COINS = [
    # Stablecoins - fetch from CoinCap
    {"id": "tether", "symbol": "USDT", "coincap_id": "tether",
     "binance_pairs": ["USDTDAI"]},  # limited options
    {"id": "usd-coin", "symbol": "USDC", "coincap_id": "usd-coin",
     "binance_pairs": []},
    {"id": "ethena-usde", "symbol": "USDE", "coincap_id": None,
     "binance_pairs": ["USDEUSDT"]},

    # Coins not on Binance
    {"id": "whitebit", "symbol": "WBT", "coincap_id": None,
     "binance_pairs": []},
    {"id": "hyperliquid", "symbol": "HYPE", "coincap_id": None,
     "binance_pairs": ["HYPEUSDT"]},
    {"id": "leo-token", "symbol": "LEO", "coincap_id": "leo-token",
     "binance_pairs": []},
    {"id": "monero", "symbol": "XMR", "coincap_id": "monero",
     "binance_pairs": []},
]

# ── COINS TO EXTEND HISTORY ───────────────────────────────────────────────────
# These coins exist before their Binance USDT pair listing date

EXTEND_COINS = [
    {"symbol": "BTC", "coincap_id": "bitcoin", "binance_start": "2017-08-17",
     "actual_start": "2010-07-17"},
    {"symbol": "ETH", "coincap_id": "ethereum", "binance_start": "2017-08-17",
     "actual_start": "2015-08-07"},
    {"symbol": "XRP", "coincap_id": "xrp", "binance_start": "2018-05-04",
     "actual_start": "2013-08-04"},
    {"symbol": "DOGE", "coincap_id": "dogecoin", "binance_start": "2019-07-05",
     "actual_start": "2013-12-15"},
    {"symbol": "ADA", "coincap_id": "cardano", "binance_start": "2018-04-17",
     "actual_start": "2017-10-01"},
    {"symbol": "BCH", "coincap_id": "bitcoin-cash", "binance_start": "2019-11-28",
     "actual_start": "2017-07-23"},
    {"symbol": "LINK", "coincap_id": "chainlink", "binance_start": "2019-01-16",
     "actual_start": "2017-09-20"},
    {"symbol": "XLM", "coincap_id": "stellar", "binance_start": "2018-05-31",
     "actual_start": "2014-08-05"},
    {"symbol": "ZEC", "coincap_id": "zcash", "binance_start": "2019-03-21",
     "actual_start": "2016-10-29"},
    {"symbol": "LTC", "coincap_id": "litecoin", "binance_start": "2017-12-13",
     "actual_start": "2013-04-28"},
    {"symbol": "BNB", "coincap_id": "binance-coin", "binance_start": "2017-11-06",
     "actual_start": "2017-07-25"},
    {"symbol": "TRX", "coincap_id": "tron", "binance_start": "2018-06-11",
     "actual_start": "2017-09-13"},
    {"symbol": "SOL", "coincap_id": "solana", "binance_start": "2020-08-11",
     "actual_start": "2020-04-10"},
]


def process_missing_coins():
    log("=" * 70)
    log("PHASE 1: FETCHING MISSING COINS")
    log("=" * 70)

    for coin in MISSING_COINS:
        symbol = coin["symbol"]
        log(f"\n--- Processing {symbol} ---")

        df = None

        # Try Binance pairs
        for pair in coin.get("binance_pairs", []):
            log(f"  Trying Binance pair: {pair}...")
            try:
                df = fetch_binance_klines(pair)
                if df is not None and len(df) > 0:
                    log(f"  -> Got {len(df)} records from Binance ({pair})")
                    break
            except Exception as e:
                log(f"  -> Failed: {e}")

        # Try CoinCap
        if (df is None or len(df) == 0) and coin.get("coincap_id"):
            log(f"  Trying CoinCap API ({coin['coincap_id']})...")
            try:
                df = fetch_coincap_history(coin["coincap_id"])
                if df is not None and len(df) > 0:
                    log(f"  -> Got {len(df)} records from CoinCap")
            except Exception as e:
                log(f"  -> Failed: {e}")

        # Try CoinGecko as last resort
        if df is None or len(df) == 0:
            log(f"  Trying CoinGecko with retry ({coin['id']})...")
            try:
                df = fetch_coingecko_history_retry(coin["id"])
                if df is not None and len(df) > 0:
                    log(f"  -> Got {len(df)} records from CoinGecko")
            except Exception as e:
                log(f"  -> Failed: {e}")

        if df is not None and len(df) > 0:
            df = add_trading_features(df)
            filepath = os.path.join(DATA_DIR, f"{symbol}_full_history.csv")
            df.to_csv(filepath, index=False)
            file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
            log(f"  SAVED: {symbol}_full_history.csv ({len(df)} rows, {file_size_mb:.2f} MB)")
        else:
            log(f"  WARNING: Could not obtain data for {symbol}")

        time.sleep(2)


def extend_existing_coins():
    log("\n" + "=" * 70)
    log("PHASE 2: EXTENDING HISTORY FOR EXISTING COINS")
    log("=" * 70)

    for coin in EXTEND_COINS:
        symbol = coin["symbol"]
        coincap_id = coin["coincap_id"]
        binance_start = coin["binance_start"]
        actual_start = coin["actual_start"]

        filepath = os.path.join(DATA_DIR, f"{symbol}_full_history.csv")

        if not os.path.exists(filepath):
            log(f"\n--- {symbol}: File not found, skipping ---")
            continue

        existing_df = pd.read_csv(filepath)
        existing_start = existing_df["date"].min()

        if existing_start <= actual_start:
            log(f"\n--- {symbol}: Already has data from {existing_start}, no extension needed ---")
            continue

        log(f"\n--- {symbol}: Extending from {existing_start} back to {actual_start} ---")
        log(f"  Fetching pre-Binance history from CoinCap ({coincap_id})...")

        try:
            early_df = fetch_coincap_history(coincap_id)
            if early_df is not None and len(early_df) > 0:
                # Filter to before existing data starts
                early_df = early_df[early_df["date"] < existing_start]
                if len(early_df) > 0:
                    log(f"  -> Got {len(early_df)} earlier records ({early_df['date'].iloc[0]} to {early_df['date'].iloc[-1]})")

                    # Merge: early CoinCap data + existing Binance data
                    merged = pd.concat([early_df, existing_df], ignore_index=True)
                    merged = merged.drop_duplicates(subset=["date"], keep="last")
                    merged = merged.sort_values("date").reset_index(drop=True)

                    # Recompute indicators on full merged dataset
                    merged = add_trading_features(merged)

                    merged.to_csv(filepath, index=False)
                    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
                    log(f"  SAVED: {symbol}_full_history.csv ({len(merged)} rows, {file_size_mb:.2f} MB)")
                    log(f"  History now spans: {merged['date'].iloc[0]} to {merged['date'].iloc[-1]}")
                else:
                    log(f"  -> No earlier data found before {existing_start}")
            else:
                log(f"  -> CoinCap returned no data")
        except Exception as e:
            log(f"  -> Error: {e}")

        time.sleep(3)


def update_summary():
    log("\n" + "=" * 70)
    log("UPDATING SUMMARY")
    log("=" * 70)

    import glob
    files = glob.glob(os.path.join(DATA_DIR, "*_full_history.csv"))

    summary_rows = []
    for filepath in sorted(files):
        filename = os.path.basename(filepath)
        symbol = filename.replace("_full_history.csv", "")
        df = pd.read_csv(filepath)

        has_ohlcv = "open" in df.columns and "high" in df.columns
        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)

        summary_rows.append({
            "symbol": symbol,
            "data_start": df["date"].iloc[0],
            "data_end": df["date"].iloc[-1],
            "total_days": len(df),
            "has_ohlcv": has_ohlcv,
            "columns": len(df.columns),
            "file": filename,
            "file_size_mb": round(file_size_mb, 2),
        })

    summary_df = pd.DataFrame(summary_rows)
    summary_path = os.path.join(DATA_DIR, "00_DATA_SUMMARY.csv")
    summary_df.to_csv(summary_path, index=False)

    log(f"\n{'Symbol':<8} {'Start':<12} {'End':<12} {'Days':>6} {'OHLCV':>6} {'Cols':>5} {'MB':>6}")
    log(f"{'-' * 60}")

    total_rows = 0
    total_size = 0
    for row in summary_rows:
        log(f"{row['symbol']:<8} {row['data_start']:<12} {row['data_end']:<12} {row['total_days']:>6} {'Yes' if row['has_ohlcv'] else 'No':>6} {row['columns']:>5} {row['file_size_mb']:>6.2f}")
        total_rows += row["total_days"]
        total_size += row["file_size_mb"]

    log(f"{'-' * 60}")
    log(f"TOTAL: {total_rows} data points, {total_size:.2f} MB across {len(summary_rows)} coins")


if __name__ == "__main__":
    process_missing_coins()
    extend_existing_coins()
    update_summary()
    log("\nDONE!")
