"""
Fourth pass: Use Binance BTC-pair data to extend history for older coins
AND use the full Binance klines pagination properly (since=0 from 2017).
Also fetch HYPE from Bybit/OKX/Gate.io APIs.
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
            "quote_volume": float(k[7]),
            "trade_count": int(k[8]),
        })

    df = pd.DataFrame(rows)
    df = df.drop_duplicates(subset=["date"], keep="last")
    df = df.sort_values("date").reset_index(drop=True)
    return df


def fetch_binance_btc_pair_and_convert(symbol, btc_pair, start_str="2017-01-01"):
    """
    Fetch data for a coin's BTC pair, then convert to USD using BTC/USDT prices.
    This gives us history from before USDT pairs existed.
    """
    log(f"  Fetching {btc_pair} from Binance...")
    btc_df = fetch_binance_klines(btc_pair, start_str=start_str)
    if btc_df is None or len(btc_df) == 0:
        return None

    log(f"  -> Got {len(btc_df)} records from {btc_pair}")

    # Get BTC/USDT prices for the same period
    btcusdt_path = os.path.join(DATA_DIR, "BTC_full_history.csv")
    if os.path.exists(btcusdt_path):
        btc_prices = pd.read_csv(btcusdt_path)[["date", "close"]].rename(columns={"close": "btc_usd_price"})
    else:
        log(f"  Fetching BTCUSDT for conversion...")
        btc_usd = fetch_binance_klines("BTCUSDT", start_str="2017-01-01")
        if btc_usd is None:
            return None
        btc_prices = btc_usd[["date", "close"]].rename(columns={"close": "btc_usd_price"})

    # Merge and convert BTC prices to USD
    merged = pd.merge(btc_df, btc_prices, on="date", how="inner")
    merged["open"] = merged["open"] * merged["btc_usd_price"]
    merged["high"] = merged["high"] * merged["btc_usd_price"]
    merged["low"] = merged["low"] * merged["btc_usd_price"]
    merged["close"] = merged["close"] * merged["btc_usd_price"]
    # Volume in quote (BTC) * BTC price = USD volume
    merged["quote_volume_usd"] = merged["quote_volume"] * merged["btc_usd_price"]
    merged = merged.drop(columns=["btc_usd_price"])

    return merged


def fetch_bybit_klines(symbol, interval="D", start_str="2020-01-01"):
    """Fetch klines from Bybit API."""
    base_url = "https://api.bybit.com/v5/market/kline"
    all_rows = []
    end_ts = int(datetime.now(timezone.utc).timestamp() * 1000)
    start_ts = int(datetime.strptime(start_str, "%Y-%m-%d").replace(
        tzinfo=timezone.utc).timestamp() * 1000)

    current_end = end_ts
    while current_end > start_ts:
        params = {
            "category": "spot",
            "symbol": symbol,
            "interval": interval,
            "end": current_end,
            "limit": 200,
        }
        try:
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
                    "quote_volume": float(k[6]) if len(k) > 6 else 0,
                })

            oldest_ts = int(result[-1][0])
            if oldest_ts >= current_end:
                break
            current_end = oldest_ts - 1

            time.sleep(0.5)
        except Exception as e:
            log(f"  Bybit error: {e}")
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


def merge_and_save(symbol, early_df):
    filepath = os.path.join(DATA_DIR, f"{symbol}_full_history.csv")
    if os.path.exists(filepath):
        existing_df = pd.read_csv(filepath)
        existing_start = existing_df["date"].min()
        early_df = early_df[early_df["date"] < existing_start]
        if len(early_df) == 0:
            log(f"  No new earlier data for {symbol}")
            return
        log(f"  Prepending {len(early_df)} earlier records to {len(existing_df)} existing")
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
    log("EXTENDING DATA WITH BTC-PAIR CONVERSIONS + BYBIT")
    log("=" * 70)

    # Coins with BTC pairs on Binance that predate their USDT pairs
    btc_pair_coins = [
        {"symbol": "ETH", "btc_pair": "ETHBTC", "start": "2017-07-14"},
        {"symbol": "XRP", "btc_pair": "XRPBTC", "start": "2017-05-01"},
        {"symbol": "BNB", "btc_pair": "BNBBTC", "start": "2017-07-14"},
        {"symbol": "ADA", "btc_pair": "ADABTC", "start": "2017-09-01"},
        {"symbol": "TRX", "btc_pair": "TRXBTC", "start": "2017-08-01"},
        {"symbol": "XLM", "btc_pair": "XLMBTC", "start": "2017-09-01"},
        {"symbol": "LINK", "btc_pair": "LINKBTC", "start": "2018-01-01"},
        {"symbol": "LTC", "btc_pair": "LTCBTC", "start": "2017-07-14"},
        {"symbol": "BCH", "btc_pair": "BCHBTC", "start": "2017-08-01"},
        {"symbol": "ZEC", "btc_pair": "ZECBTC", "start": "2017-11-01"},
        {"symbol": "DOGE", "btc_pair": "DOGEBTC", "start": "2019-01-01"},
    ]

    for coin in btc_pair_coins:
        symbol = coin["symbol"]
        filepath = os.path.join(DATA_DIR, f"{symbol}_full_history.csv")

        if os.path.exists(filepath):
            existing_df = pd.read_csv(filepath)
            existing_start = existing_df["date"].min()
            log(f"\n--- {symbol}: Current start={existing_start} ---")
        else:
            log(f"\n--- {symbol}: No existing file ---")
            existing_start = "9999-99-99"

        if coin["start"] >= existing_start:
            log(f"  BTC pair start ({coin['start']}) not earlier, skipping")
            continue

        early_df = fetch_binance_btc_pair_and_convert(symbol, coin["btc_pair"], coin["start"])
        if early_df is not None and len(early_df) > 0:
            merge_and_save(symbol, early_df)
        else:
            log(f"  No BTC-pair data available")

        time.sleep(1)

    # Now handle HYPE from Bybit
    log(f"\n--- HYPE: Fetching from Bybit ---")
    hype_df = fetch_bybit_klines("HYPEUSDT", interval="D", start_str="2024-11-01")
    if hype_df is not None and len(hype_df) > 0:
        log(f"  Got {len(hype_df)} records from Bybit")
        hype_df = add_trading_features(hype_df)
        hype_path = os.path.join(DATA_DIR, "HYPE_full_history.csv")
        hype_df.to_csv(hype_path, index=False)
        file_size_mb = os.path.getsize(hype_path) / (1024 * 1024)
        log(f"  SAVED: HYPE_full_history.csv ({len(hype_df)} rows, {file_size_mb:.2f} MB)")
    else:
        log(f"  No Bybit HYPE data")

    # Also extend XMR from Kraken (paginated properly)
    log(f"\n--- XMR: Fetching full history from Kraken with pagination ---")
    xmr_path = os.path.join(DATA_DIR, "XMR_full_history.csv")
    try:
        # Use Kraken with proper since=0 for full history
        kraken_url = "https://api.kraken.com/0/public/OHLC"
        all_rows = []
        current_since = 0

        for batch in range(20):  # max 20 batches = 14400 candles
            params = {"pair": "XXMRZUSD", "interval": 1440, "since": current_since}
            resp = requests.get(kraken_url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            if data.get("error"):
                log(f"  Kraken error: {data['error']}")
                break

            result = data.get("result", {})
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
                    "volume": float(c[6]),
                    "trade_count": int(c[7]),
                })

            last_ts = result.get("last", 0)
            if last_ts <= current_since:
                break
            current_since = last_ts

            log(f"  Kraken batch {batch+1}: {len(candles)} candles, latest: {all_rows[-1]['date']}")

            if len(candles) < 720:
                break
            time.sleep(2)

        if all_rows:
            xmr_df = pd.DataFrame(all_rows)
            xmr_df = xmr_df.drop_duplicates(subset=["date"], keep="last")
            xmr_df = xmr_df.sort_values("date").reset_index(drop=True)
            log(f"  Total XMR from Kraken: {len(xmr_df)} records ({xmr_df['date'].iloc[0]} to {xmr_df['date'].iloc[-1]})")

            xmr_df = add_trading_features(xmr_df)
            xmr_df.to_csv(xmr_path, index=False)
            file_size_mb = os.path.getsize(xmr_path) / (1024 * 1024)
            log(f"  SAVED: XMR_full_history.csv ({len(xmr_df)} rows, {file_size_mb:.2f} MB)")

    except Exception as e:
        log(f"  Kraken XMR error: {e}")

    # Final summary
    log("\n" + "=" * 70)
    log("FINAL SUMMARY AFTER ALL EXTENSIONS")
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


if __name__ == "__main__":
    main()
