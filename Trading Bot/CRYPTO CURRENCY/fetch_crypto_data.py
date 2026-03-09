"""
Comprehensive Cryptocurrency Historical Data Downloader
========================================================
Fetches full historical data for the top 20 cryptocurrencies by market cap.
Uses CoinGecko API (free, no key required) for price/market/volume history,
and CryptoDataDownload for OHLCV candlestick data.

Data collected per coin:
  - Daily price (USD), market cap, total volume (full history)
  - OHLCV daily candlestick data (from CryptoDataDownload / Binance)
  - Key metadata (launch date, all-time high/low, etc.)

Output: CSV files per coin in the project folder, plus a master summary.
"""

import requests
import pandas as pd
import time
import json
import os
import sys
from datetime import datetime, timezone

# -- Configuration --------------------------------------------------------------

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(OUTPUT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Top 20 coins: CoinGecko IDs mapped to symbols and common Binance pairs
TOP_20_COINS = [
    {"id": "bitcoin",        "symbol": "BTC",  "binance": "BTCUSDT"},
    {"id": "ethereum",       "symbol": "ETH",  "binance": "ETHUSDT"},
    {"id": "tether",         "symbol": "USDT", "binance": None},  # stablecoin
    {"id": "ripple",         "symbol": "XRP",  "binance": "XRPUSDT"},
    {"id": "binancecoin",    "symbol": "BNB",  "binance": "BNBUSDT"},
    {"id": "solana",         "symbol": "SOL",  "binance": "SOLUSDT"},
    {"id": "usd-coin",       "symbol": "USDC", "binance": None},  # stablecoin
    {"id": "tron",           "symbol": "TRX",  "binance": "TRXUSDT"},
    {"id": "dogecoin",       "symbol": "DOGE", "binance": "DOGEUSDT"},
    {"id": "cardano",        "symbol": "ADA",  "binance": "ADAUSDT"},
    {"id": "whitebit",       "symbol": "WBT",  "binance": None},
    {"id": "hyperliquid",    "symbol": "HYPE", "binance": None},
    {"id": "bitcoin-cash",   "symbol": "BCH",  "binance": "BCHUSDT"},
    {"id": "chainlink",      "symbol": "LINK", "binance": "LINKUSDT"},
    {"id": "leo-token",      "symbol": "LEO",  "binance": None},
    {"id": "stellar",        "symbol": "XLM",  "binance": "XLMUSDT"},
    {"id": "zcash",          "symbol": "ZEC",  "binance": "ZECUSDT"},
    {"id": "monero",         "symbol": "XMR",  "binance": None},
    {"id": "ethena-usde",    "symbol": "USDE", "binance": None},
    {"id": "litecoin",       "symbol": "LTC",  "binance": "LTCUSDT"},
]

COINGECKO_BASE = "https://api.coingecko.com/api/v3"

# Rate limiting: CoinGecko free tier allows ~10-30 req/min
REQUEST_DELAY = 6  # seconds between requests to stay safe


def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    try:
        print(f"[{timestamp}] {msg}")
    except UnicodeEncodeError:
        print(f"[{timestamp}] {msg.encode('ascii', 'replace').decode()}")
    sys.stdout.flush()


# -- CoinGecko: Coin Metadata --------------------------------------------------

def fetch_coin_metadata(coin_id):
    """Fetch detailed metadata for a coin from CoinGecko."""
    url = f"{COINGECKO_BASE}/coins/{coin_id}"
    params = {
        "localization": "false",
        "tickers": "false",
        "market_data": "true",
        "community_data": "false",
        "developer_data": "false",
        "sparkline": "false",
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def extract_metadata(data):
    """Extract key metadata fields from CoinGecko coin data."""
    md = data.get("market_data", {})
    return {
        "id": data.get("id"),
        "symbol": data.get("symbol", "").upper(),
        "name": data.get("name"),
        "genesis_date": data.get("genesis_date"),
        "hashing_algorithm": data.get("hashing_algorithm"),
        "categories": ", ".join(data.get("categories", [])),
        "current_price_usd": md.get("current_price", {}).get("usd"),
        "market_cap_usd": md.get("market_cap", {}).get("usd"),
        "market_cap_rank": md.get("market_cap_rank"),
        "fully_diluted_valuation_usd": md.get("fully_diluted_valuation", {}).get("usd"),
        "total_volume_usd": md.get("total_volume", {}).get("usd"),
        "high_24h_usd": md.get("high_24h", {}).get("usd"),
        "low_24h_usd": md.get("low_24h", {}).get("usd"),
        "price_change_24h": md.get("price_change_24h"),
        "price_change_percentage_24h": md.get("price_change_percentage_24h"),
        "price_change_percentage_7d": md.get("price_change_percentage_7d"),
        "price_change_percentage_14d": md.get("price_change_percentage_14d"),
        "price_change_percentage_30d": md.get("price_change_percentage_30d"),
        "price_change_percentage_60d": md.get("price_change_percentage_60d"),
        "price_change_percentage_200d": md.get("price_change_percentage_200d"),
        "price_change_percentage_1y": md.get("price_change_percentage_1y"),
        "circulating_supply": md.get("circulating_supply"),
        "total_supply": md.get("total_supply"),
        "max_supply": md.get("max_supply"),
        "ath_usd": md.get("ath", {}).get("usd"),
        "ath_date_usd": md.get("ath_date", {}).get("usd"),
        "ath_change_percentage_usd": md.get("ath_change_percentage", {}).get("usd"),
        "atl_usd": md.get("atl", {}).get("usd"),
        "atl_date_usd": md.get("atl_date", {}).get("usd"),
        "atl_change_percentage_usd": md.get("atl_change_percentage", {}).get("usd"),
        "last_updated": data.get("last_updated"),
    }


# -- CoinGecko: Full Historical Market Data -------------------------------------

def fetch_full_history_coingecko(coin_id):
    """
    Fetch FULL price, market cap, and volume history from CoinGecko.
    Uses /coins/{id}/market_chart with days=max for complete history.
    Returns daily granularity data.
    """
    url = f"{COINGECKO_BASE}/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": "max",
        "interval": "daily",
    }
    resp = requests.get(url, params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    prices = data.get("prices", [])
    market_caps = data.get("market_caps", [])
    total_volumes = data.get("total_volumes", [])

    rows = []
    for i in range(len(prices)):
        ts = prices[i][0]
        dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
        row = {
            "date": dt,
            "timestamp_ms": ts,
            "price_usd": prices[i][1],
            "market_cap_usd": market_caps[i][1] if i < len(market_caps) else None,
            "total_volume_usd": total_volumes[i][1] if i < len(total_volumes) else None,
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    # Remove duplicate dates (keep last)
    df = df.drop_duplicates(subset=["date"], keep="last")
    df = df.sort_values("date").reset_index(drop=True)
    return df


# -- Binance: Full Historical OHLCV (Klines) -----------------------------------

def fetch_binance_klines(symbol, interval="1d", start_str="2017-01-01"):
    """
    Fetch ALL historical klines (OHLCV) from Binance API.
    Binance returns max 1000 candles per request, so we paginate.
    """
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
        # Move start to after the last candle's close time
        current_start = klines[-1][6] + 1

        if len(klines) < 1000:
            break

        time.sleep(0.5)  # Binance rate limiting

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


# -- CryptoDataDownload: OHLCV CSV ---------------------------------------------

def fetch_cryptodatadownload_ohlcv(symbol):
    """
    Try to fetch daily OHLCV from CryptoDataDownload (Binance data).
    Falls back gracefully if not available.
    """
    pair = f"{symbol}USDT"
    url = f"https://www.cryptodatadownload.com/cdd/Binance_{pair}_d.csv"

    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code != 200:
            return None

        lines = resp.text.strip().split("\n")
        # CryptoDataDownload CSVs often have a header comment line
        if lines and not lines[0].startswith("unix") and not lines[0].startswith("date") and not lines[0].startswith("Date"):
            lines = lines[1:]  # skip comment line

        if not lines:
            return None

        from io import StringIO
        df = pd.read_csv(StringIO("\n".join(lines)))

        # Normalize column names
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

        return df
    except Exception as e:
        log(f"  CryptoDataDownload error for {symbol}: {e}")
        return None


# -- Derived Features for Trading Bot ------------------------------------------

def add_trading_features(df):
    """Add derived technical features useful for trading bots."""
    if "close" not in df.columns and "price_usd" in df.columns:
        df["close"] = df["price_usd"]

    if "close" not in df.columns:
        return df

    # Daily returns
    df["daily_return_pct"] = df["close"].pct_change() * 100

    # Moving averages
    for window in [7, 14, 21, 30, 50, 100, 200]:
        df[f"sma_{window}"] = df["close"].rolling(window=window).mean()

    # Exponential moving averages
    for window in [12, 26, 50, 200]:
        df[f"ema_{window}"] = df["close"].ewm(span=window, adjust=False).mean()

    # MACD
    df["macd"] = df["ema_12"] - df["ema_26"]
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_histogram"] = df["macd"] - df["macd_signal"]

    # Bollinger Bands (20-day)
    df["bb_middle"] = df["close"].rolling(window=20).mean()
    bb_std = df["close"].rolling(window=20).std()
    df["bb_upper"] = df["bb_middle"] + (bb_std * 2)
    df["bb_lower"] = df["bb_middle"] - (bb_std * 2)
    df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_middle"]

    # RSI (14-day)
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["rsi_14"] = 100 - (100 / (1 + rs))

    # Volatility
    df["volatility_7d"] = df["daily_return_pct"].rolling(window=7).std()
    df["volatility_30d"] = df["daily_return_pct"].rolling(window=30).std()

    # Price relative to ATH (rolling)
    df["rolling_ath"] = df["close"].cummax()
    df["drawdown_from_ath_pct"] = ((df["close"] - df["rolling_ath"]) / df["rolling_ath"]) * 100

    if "total_volume_usd" in df.columns:
        df["volume_sma_20"] = df["total_volume_usd"].rolling(window=20).mean()
        df["volume_ratio"] = df["total_volume_usd"] / df["volume_sma_20"]

    return df


# -- Main Pipeline --------------------------------------------------------------

def main():
    log("=" * 70)
    log("CRYPTOCURRENCY HISTORICAL DATA DOWNLOADER")
    log(f"Fetching data for {len(TOP_20_COINS)} coins")
    log(f"Output directory: {DATA_DIR}")
    log("=" * 70)

    all_metadata = []
    summary_rows = []

    for i, coin in enumerate(TOP_20_COINS):
        coin_id = coin["id"]
        symbol = coin["symbol"]
        binance_pair = coin["binance"]

        log(f"\n{'-' * 60}")
        log(f"[{i+1}/{len(TOP_20_COINS)}] Processing {symbol} ({coin_id})")
        log(f"{'-' * 60}")

        # -- Step 1: Metadata --
        log(f"  Fetching metadata from CoinGecko...")
        try:
            raw_meta = fetch_coin_metadata(coin_id)
            meta = extract_metadata(raw_meta)
            all_metadata.append(meta)
            log(f"  -> Name: {meta['name']}, Rank: {meta['market_cap_rank']}")
            log(f"  -> ATH: ${meta['ath_usd']}, ATL: ${meta['atl_usd']}")
            log(f"  -> Genesis date: {meta['genesis_date']}")
        except Exception as e:
            log(f"  ERROR fetching metadata: {e}")
            meta = {"id": coin_id, "symbol": symbol, "name": coin_id}
            all_metadata.append(meta)

        time.sleep(REQUEST_DELAY)

        # -- Step 2: Full price/volume/mcap history from CoinGecko --
        log(f"  Fetching full price history from CoinGecko (days=max)...")
        coingecko_df = None
        try:
            coingecko_df = fetch_full_history_coingecko(coin_id)
            if coingecko_df is not None and len(coingecko_df) > 0:
                first_date = coingecko_df["date"].iloc[0]
                last_date = coingecko_df["date"].iloc[-1]
                log(f"  -> {len(coingecko_df)} daily records: {first_date} to {last_date}")
            else:
                log(f"  -> No data returned")
        except Exception as e:
            log(f"  ERROR fetching CoinGecko history: {e}")

        time.sleep(REQUEST_DELAY)

        # -- Step 3: OHLCV from Binance (if available) --
        ohlcv_df = None
        if binance_pair:
            log(f"  Fetching OHLCV klines from Binance ({binance_pair})...")
            try:
                ohlcv_df = fetch_binance_klines(binance_pair, interval="1d")
                if ohlcv_df is not None and len(ohlcv_df) > 0:
                    log(f"  -> {len(ohlcv_df)} OHLCV records: {ohlcv_df['date'].iloc[0]} to {ohlcv_df['date'].iloc[-1]}")
                else:
                    log(f"  -> No Binance OHLCV data")
            except Exception as e:
                log(f"  ERROR fetching Binance klines: {e}")

        # -- Step 4: Merge data --
        if coingecko_df is not None and ohlcv_df is not None:
            log(f"  Merging CoinGecko + Binance data...")
            merged = pd.merge(coingecko_df, ohlcv_df, on="date", how="outer")
            merged = merged.sort_values("date").reset_index(drop=True)
            # Fill close from price_usd where missing
            if "close" in merged.columns and "price_usd" in merged.columns:
                merged["close"] = merged["close"].fillna(merged["price_usd"])
                merged["price_usd"] = merged["price_usd"].fillna(merged["close"])
        elif coingecko_df is not None:
            merged = coingecko_df.copy()
        elif ohlcv_df is not None:
            merged = ohlcv_df.copy()
        else:
            log(f"  WARNING: No data obtained for {symbol}!")
            continue

        # -- Step 5: Add trading features --
        log(f"  Computing trading indicators (SMA, EMA, RSI, MACD, Bollinger)...")
        merged = add_trading_features(merged)

        # -- Step 6: Save CSV --
        filename = f"{symbol}_full_history.csv"
        filepath = os.path.join(DATA_DIR, filename)
        merged.to_csv(filepath, index=False)
        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        log(f"  SAVED: {filename} ({len(merged)} rows, {file_size_mb:.2f} MB)")

        # Summary entry
        summary_rows.append({
            "rank": meta.get("market_cap_rank", "N/A"),
            "symbol": symbol,
            "name": meta.get("name", coin_id),
            "data_start": merged["date"].iloc[0] if len(merged) > 0 else "N/A",
            "data_end": merged["date"].iloc[-1] if len(merged) > 0 else "N/A",
            "total_days": len(merged),
            "has_ohlcv": ohlcv_df is not None and len(ohlcv_df) > 0,
            "has_price_history": coingecko_df is not None and len(coingecko_df) > 0,
            "file": filename,
            "file_size_mb": round(file_size_mb, 2),
        })

    # -- Save metadata summary --
    log(f"\n{'=' * 70}")
    log("Saving metadata and summary files...")

    meta_df = pd.DataFrame(all_metadata)
    meta_path = os.path.join(DATA_DIR, "00_ALL_COINS_METADATA.csv")
    meta_df.to_csv(meta_path, index=False)
    log(f"  SAVED: 00_ALL_COINS_METADATA.csv")

    summary_df = pd.DataFrame(summary_rows)
    summary_path = os.path.join(DATA_DIR, "00_DATA_SUMMARY.csv")
    summary_df.to_csv(summary_path, index=False)
    log(f"  SAVED: 00_DATA_SUMMARY.csv")

    # -- Print summary table --
    log(f"\n{'=' * 70}")
    log("DOWNLOAD SUMMARY")
    log(f"{'=' * 70}")
    log(f"{'Symbol':<8} {'Name':<15} {'Start':<12} {'End':<12} {'Days':>6} {'OHLCV':>6} {'MB':>6}")
    log(f"{'-' * 70}")

    total_rows = 0
    total_size = 0
    for row in summary_rows:
        log(f"{row['symbol']:<8} {row['name']:<15} {row['data_start']:<12} {row['data_end']:<12} {row['total_days']:>6} {'Yes' if row['has_ohlcv'] else 'No':>6} {row['file_size_mb']:>6.2f}")
        total_rows += row["total_days"]
        total_size += row["file_size_mb"]

    log(f"{'-' * 70}")
    log(f"TOTAL: {total_rows} data points, {total_size:.2f} MB across {len(summary_rows)} coins")
    log(f"\nAll files saved to: {DATA_DIR}")
    log("DONE!")


if __name__ == "__main__":
    main()
