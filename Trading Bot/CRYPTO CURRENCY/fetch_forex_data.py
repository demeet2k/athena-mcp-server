"""
Comprehensive Currency Exchange Rate Historical Data Downloader
================================================================
Fetches 30 years of daily exchange rates for 20 major world currencies.

Data Sources:
  1. ECB (European Central Bank) - EUR-based rates from 1999 to present
  2. US Federal Reserve (FRED) - Historical USD-based rates
  3. BIS (Bank for International Settlements) - Broad coverage
  4. Fallback: ExchangeRate.host / Open APIs

Currencies covered (20 major currencies):
  USD, EUR, GBP, JPY, CHF, CAD, AUD, NZD, CNY, HKD,
  SGD, SEK, NOK, DKK, KRW, INR, BRL, MXN, ZAR, TRY

Output: CSV files with daily rates, analysis metrics, and summary.
"""

import requests
import pandas as pd
import numpy as np
import time
import os
import sys
from datetime import datetime, timezone, timedelta
from io import StringIO

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(OUTPUT_DIR, "forex_data")
os.makedirs(DATA_DIR, exist_ok=True)


def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    try:
        print(f"[{timestamp}] {msg}")
    except UnicodeEncodeError:
        print(f"[{timestamp}] {msg.encode('ascii', 'replace').decode()}")
    sys.stdout.flush()


# ── 20 Major Currencies ───────────────────────────────────────────────────────

CURRENCIES = {
    "USD": "US Dollar",
    "EUR": "Euro",
    "GBP": "British Pound",
    "JPY": "Japanese Yen",
    "CHF": "Swiss Franc",
    "CAD": "Canadian Dollar",
    "AUD": "Australian Dollar",
    "NZD": "New Zealand Dollar",
    "CNY": "Chinese Yuan",
    "HKD": "Hong Kong Dollar",
    "SGD": "Singapore Dollar",
    "SEK": "Swedish Krona",
    "NOK": "Norwegian Krone",
    "DKK": "Danish Krone",
    "KRW": "South Korean Won",
    "INR": "Indian Rupee",
    "BRL": "Brazilian Real",
    "MXN": "Mexican Peso",
    "ZAR": "South African Rand",
    "TRY": "Turkish Lira",
}


# ── ECB Data (EUR-based, 1999-present) ────────────────────────────────────────

def fetch_ecb_rates():
    """
    Fetch daily EUR-based exchange rates from ECB SDMX REST API.
    Returns a DataFrame with date index and columns for each currency vs EUR.
    """
    log("Fetching EUR-based rates from ECB (1999-present)...")

    # ECB currency codes (some differ from ISO)
    ecb_codes = {
        "USD": "USD", "GBP": "GBP", "JPY": "JPY", "CHF": "CHF",
        "CAD": "CAD", "AUD": "AUD", "NZD": "NZD", "CNY": "CNY",
        "HKD": "HKD", "SGD": "SGD", "SEK": "SEK", "NOK": "NOK",
        "DKK": "DKK", "KRW": "KRW", "INR": "INR", "BRL": "BRL",
        "MXN": "MXN", "ZAR": "ZAR", "TRY": "TRY",
    }

    all_dfs = []

    for iso_code, ecb_code in ecb_codes.items():
        log(f"  Fetching EUR/{iso_code}...")
        url = (
            f"https://data-api.ecb.europa.eu/service/data/EXR/"
            f"D.{ecb_code}.EUR.SP00.A"
            f"?startPeriod=1994-01-01&endPeriod=2026-12-31"
            f"&format=csvdata"
        )

        try:
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()

            df = pd.read_csv(StringIO(resp.text))

            # ECB CSV has columns: KEY, FREQ, CURRENCY, ..., TIME_PERIOD, OBS_VALUE, ...
            if "TIME_PERIOD" in df.columns and "OBS_VALUE" in df.columns:
                rate_df = df[["TIME_PERIOD", "OBS_VALUE"]].copy()
                rate_df.columns = ["date", f"EUR_{iso_code}"]
                rate_df[f"EUR_{iso_code}"] = pd.to_numeric(rate_df[f"EUR_{iso_code}"], errors="coerce")
                rate_df = rate_df.dropna()
                all_dfs.append(rate_df)
                log(f"    -> {len(rate_df)} records ({rate_df['date'].iloc[0]} to {rate_df['date'].iloc[-1]})")
            else:
                log(f"    -> Unexpected format: {list(df.columns)[:5]}")

        except Exception as e:
            log(f"    -> Error: {e}")

        time.sleep(0.5)

    if not all_dfs:
        return None

    # Merge all into one DataFrame
    merged = all_dfs[0]
    for df in all_dfs[1:]:
        merged = pd.merge(merged, df, on="date", how="outer")

    merged = merged.sort_values("date").reset_index(drop=True)
    # Add EUR_EUR = 1
    merged["EUR_EUR"] = 1.0

    log(f"  ECB total: {len(merged)} trading days, {len(merged.columns)-1} pairs")
    return merged


# ── Convert EUR-based to USD-based ────────────────────────────────────────────

def convert_to_usd_base(ecb_df):
    """Convert EUR-based rates to USD-based rates."""
    log("Converting to USD-based rates...")

    if ecb_df is None or "EUR_USD" not in ecb_df.columns:
        return None

    usd_df = ecb_df[["date"]].copy()

    # EUR/USD rate (how many USD per 1 EUR)
    eur_usd = ecb_df["EUR_USD"]

    for col in ecb_df.columns:
        if col == "date":
            continue

        currency = col.replace("EUR_", "")

        if currency == "USD":
            # USD/USD = 1
            usd_df["USD_USD"] = 1.0
        elif currency == "EUR":
            # USD/EUR = 1 / (EUR/USD)
            usd_df["USD_EUR"] = 1.0 / eur_usd
        else:
            # EUR/XXX rate (how many XXX per 1 EUR)
            eur_xxx = ecb_df[col]
            # USD/XXX = EUR/XXX / EUR/USD = (XXX per EUR) / (USD per EUR)
            usd_df[f"USD_{currency}"] = eur_xxx / eur_usd

    log(f"  Converted {len(usd_df.columns)-1} USD-based pairs")
    return usd_df


# ── Supplement with CryptoCompare Forex (for pre-1999) ────────────────────────

def fetch_cryptocompare_forex(from_sym, to_sym="USD"):
    """
    Fetch historical forex data from CryptoCompare.
    They have forex data going back further than ECB.
    """
    url = "https://min-api.cryptocompare.com/data/v2/histoday"
    all_rows = []
    toTs = int(datetime.now(timezone.utc).timestamp())
    seen = set()

    for batch in range(20):
        params = {
            "fsym": from_sym,
            "tsym": to_sym,
            "limit": 2000,
            "toTs": toTs,
        }
        try:
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            if data.get("Response") == "Error":
                break

            candles = data.get("Data", {}).get("Data", [])
            if not candles:
                break

            new_count = 0
            for c in candles:
                if c.get("close", 0) == 0:
                    continue
                dt = datetime.fromtimestamp(c["time"], tz=timezone.utc).strftime("%Y-%m-%d")
                if dt in seen:
                    continue
                seen.add(dt)
                new_count += 1
                all_rows.append({
                    "date": dt,
                    "open": float(c["open"]),
                    "high": float(c["high"]),
                    "low": float(c["low"]),
                    "close": float(c["close"]),
                    "volume": float(c.get("volumefrom", 0)),
                })

            if new_count == 0:
                break

            earliest = min(c["time"] for c in candles)
            if earliest >= toTs:
                break
            toTs = earliest - 1
            time.sleep(1)

        except Exception as e:
            log(f"  CryptoCompare error for {from_sym}/{to_sym}: {e}")
            break

    if not all_rows:
        return None

    df = pd.DataFrame(all_rows)
    df = df.drop_duplicates(subset=["date"], keep="last")
    df = df.sort_values("date").reset_index(drop=True)
    return df


# ── Analysis Features ─────────────────────────────────────────────────────────

def compute_currency_analysis(df, rate_col):
    """Compute comprehensive analysis metrics for a currency pair."""
    rates = df[rate_col].copy()

    # Daily returns
    df[f"{rate_col}_daily_return_pct"] = rates.pct_change() * 100

    # Moving averages
    for w in [7, 30, 90, 200, 365]:
        df[f"{rate_col}_sma_{w}"] = rates.rolling(window=w).mean()

    # Volatility (rolling std of returns)
    returns = rates.pct_change()
    df[f"{rate_col}_vol_30d"] = returns.rolling(30).std() * np.sqrt(252) * 100
    df[f"{rate_col}_vol_90d"] = returns.rolling(90).std() * np.sqrt(252) * 100
    df[f"{rate_col}_vol_365d"] = returns.rolling(365).std() * np.sqrt(252) * 100

    # Year-over-year change
    df[f"{rate_col}_yoy_pct"] = rates.pct_change(periods=252) * 100

    # Distance from rolling high/low
    df[f"{rate_col}_52w_high"] = rates.rolling(252).max()
    df[f"{rate_col}_52w_low"] = rates.rolling(252).min()
    df[f"{rate_col}_pct_from_52w_high"] = (rates - df[f"{rate_col}_52w_high"]) / df[f"{rate_col}_52w_high"] * 100

    # Bollinger bands
    sma20 = rates.rolling(20).mean()
    std20 = rates.rolling(20).std()
    df[f"{rate_col}_bb_upper"] = sma20 + 2 * std20
    df[f"{rate_col}_bb_lower"] = sma20 - 2 * std20

    return df


# ── Major Crisis Detection ────────────────────────────────────────────────────

def detect_major_moves(df, rate_col, threshold_pct=2.0):
    """Detect days with unusually large moves (> threshold %)."""
    returns = df[rate_col].pct_change() * 100
    big_moves = df[abs(returns) > threshold_pct].copy()
    big_moves["move_pct"] = returns[abs(returns) > threshold_pct]
    big_moves["direction"] = big_moves["move_pct"].apply(lambda x: "SURGE" if x > 0 else "CRASH")
    return big_moves[["date", rate_col, "move_pct", "direction"]]


# ── Main Pipeline ─────────────────────────────────────────────────────────────

def main():
    log("=" * 70)
    log("CURRENCY FLUCTUATION DATA DOWNLOADER & ANALYZER")
    log(f"Covering {len(CURRENCIES)} major currencies, 30 years of history")
    log(f"Output directory: {DATA_DIR}")
    log("=" * 70)

    # ── Phase 1: ECB Data ──
    ecb_df = fetch_ecb_rates()

    if ecb_df is not None:
        ecb_path = os.path.join(DATA_DIR, "01_ECB_EUR_based_rates.csv")
        ecb_df.to_csv(ecb_path, index=False)
        log(f"  SAVED: 01_ECB_EUR_based_rates.csv ({len(ecb_df)} rows)")

    # ── Phase 2: Convert to USD base ──
    usd_df = convert_to_usd_base(ecb_df)

    if usd_df is not None:
        usd_path = os.path.join(DATA_DIR, "02_USD_based_rates.csv")
        usd_df.to_csv(usd_path, index=False)
        log(f"  SAVED: 02_USD_based_rates.csv ({len(usd_df)} rows)")

    # ── Phase 3: Extend with CryptoCompare for pre-1999 data ──
    log("\n" + "=" * 70)
    log("PHASE 3: Extending history with CryptoCompare (pre-1999 data)")
    log("=" * 70)

    # Currencies to extend (those that existed before 1999)
    pre_euro_currencies = ["GBP", "JPY", "CHF", "CAD", "AUD", "NZD",
                           "SEK", "NOK", "DKK", "HKD", "SGD", "KRW",
                           "INR", "ZAR", "MXN", "BRL"]

    extended_pairs = {}

    for currency in pre_euro_currencies:
        log(f"\n  Fetching USD/{currency} from CryptoCompare...")
        cc_df = fetch_cryptocompare_forex(currency, "USD")
        if cc_df is not None and len(cc_df) > 0:
            # CryptoCompare returns how many USD per 1 unit of currency
            # We want USD/XXX = how many XXX per 1 USD, so invert
            cc_df["rate"] = 1.0 / cc_df["close"]
            cc_df = cc_df[["date", "rate"]].rename(columns={"rate": f"USD_{currency}"})

            log(f"    -> {len(cc_df)} records ({cc_df['date'].iloc[0]} to {cc_df['date'].iloc[-1]})")

            if usd_df is not None and f"USD_{currency}" in usd_df.columns:
                ecb_start = usd_df["date"].min()
                early = cc_df[cc_df["date"] < ecb_start]
                if len(early) > 0:
                    log(f"    -> {len(early)} pre-ECB records to prepend")
                    extended_pairs[currency] = early
            else:
                extended_pairs[currency] = cc_df

            time.sleep(1)
        else:
            log(f"    -> No data")

    # Also get USD/EUR from CryptoCompare (EUR didn't exist before 1999)
    log(f"\n  Fetching EUR/USD from CryptoCompare...")
    eur_cc = fetch_cryptocompare_forex("EUR", "USD")
    if eur_cc is not None:
        eur_cc["USD_EUR"] = 1.0 / eur_cc["close"]
        eur_cc = eur_cc[["date", "USD_EUR"]]
        log(f"    -> {len(eur_cc)} records")
        if usd_df is not None:
            ecb_start = usd_df["date"].min()
            early = eur_cc[eur_cc["date"] < ecb_start]
            if len(early) > 0:
                extended_pairs["EUR"] = early

    # ── Phase 4: Merge extended data with ECB data ──
    if usd_df is not None and extended_pairs:
        log("\nMerging pre-1999 data with ECB data...")
        for currency, early_df in extended_pairs.items():
            col = f"USD_{currency}"
            if col in usd_df.columns:
                # Create a temporary df with just date and the rate
                temp = early_df[["date", col]].copy()
                # Prepend early data
                existing = usd_df[["date", col]].dropna()
                merged = pd.concat([temp, existing], ignore_index=True)
                merged = merged.drop_duplicates(subset=["date"], keep="last")
                merged = merged.sort_values("date").reset_index(drop=True)
                # Update in main df
                usd_df = pd.merge(usd_df, merged.rename(columns={col: f"{col}_ext"}),
                                  on="date", how="outer")
                usd_df[col] = usd_df[col].fillna(usd_df[f"{col}_ext"])
                usd_df = usd_df.drop(columns=[f"{col}_ext"])

        usd_df = usd_df.sort_values("date").reset_index(drop=True)

    # ── Phase 5: Save individual currency pair files with analysis ──
    log("\n" + "=" * 70)
    log("PHASE 5: Computing analysis & saving per-currency files")
    log("=" * 70)

    summary_rows = []

    for currency, name in CURRENCIES.items():
        col = f"USD_{currency}"
        if usd_df is None or col not in usd_df.columns:
            log(f"  {currency}: No data available, skipping")
            continue

        # Extract this pair's data (non-null only)
        pair_df = usd_df[["date", col]].dropna().copy()
        pair_df = pair_df.reset_index(drop=True)

        if len(pair_df) == 0:
            continue

        log(f"\n  {currency} ({name}): {len(pair_df)} days, {pair_df['date'].iloc[0]} to {pair_df['date'].iloc[-1]}")

        # Compute analysis
        pair_df = compute_currency_analysis(pair_df, col)

        # Save
        filepath = os.path.join(DATA_DIR, f"USD_{currency}_history.csv")
        pair_df.to_csv(filepath, index=False)
        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        log(f"    SAVED: USD_{currency}_history.csv ({len(pair_df)} rows, {file_size_mb:.2f} MB)")

        # Detect big moves
        big_moves = detect_major_moves(pair_df, col)
        if len(big_moves) > 0:
            big_path = os.path.join(DATA_DIR, f"USD_{currency}_big_moves.csv")
            big_moves.to_csv(big_path, index=False)
            log(f"    {len(big_moves)} big moves (>2%) detected and saved")

        # Summary stats
        rates = pair_df[col]
        returns_pct = rates.pct_change() * 100
        summary_rows.append({
            "currency": currency,
            "name": name,
            "data_start": pair_df["date"].iloc[0],
            "data_end": pair_df["date"].iloc[-1],
            "total_days": len(pair_df),
            "current_rate": round(rates.iloc[-1], 6),
            "all_time_high": round(rates.max(), 6),
            "ath_date": pair_df.loc[rates.idxmax(), "date"],
            "all_time_low": round(rates.min(), 6),
            "atl_date": pair_df.loc[rates.idxmin(), "date"],
            "total_change_pct": round((rates.iloc[-1] / rates.iloc[0] - 1) * 100, 2),
            "avg_daily_return_pct": round(returns_pct.mean(), 4),
            "max_daily_gain_pct": round(returns_pct.max(), 2),
            "max_daily_loss_pct": round(returns_pct.min(), 2),
            "annualized_volatility_pct": round(returns_pct.std() * np.sqrt(252), 2),
            "big_moves_gt2pct": len(big_moves) if len(big_moves) > 0 else 0,
        })

    # ── Phase 6: Save master files ──
    log("\n" + "=" * 70)
    log("PHASE 6: Saving master files")
    log("=" * 70)

    # Save full USD-based matrix
    if usd_df is not None:
        master_path = os.path.join(DATA_DIR, "03_MASTER_USD_rates_all_currencies.csv")
        usd_df.to_csv(master_path, index=False)
        log(f"  SAVED: 03_MASTER_USD_rates_all_currencies.csv ({len(usd_df)} rows)")

    # Save summary
    summary_df = pd.DataFrame(summary_rows)
    summary_path = os.path.join(DATA_DIR, "00_CURRENCY_SUMMARY.csv")
    summary_df.to_csv(summary_path, index=False)
    log(f"  SAVED: 00_CURRENCY_SUMMARY.csv")

    # ── Phase 7: Cross-currency correlation matrix ──
    if usd_df is not None:
        log("\nComputing cross-currency correlation matrix...")
        rate_cols = [c for c in usd_df.columns if c.startswith("USD_") and c != "USD_USD"]
        returns_df = usd_df[rate_cols].pct_change()
        corr_matrix = returns_df.corr()
        corr_path = os.path.join(DATA_DIR, "04_CORRELATION_MATRIX.csv")
        corr_matrix.to_csv(corr_path)
        log(f"  SAVED: 04_CORRELATION_MATRIX.csv")

    # ── Print summary ──
    log("\n" + "=" * 70)
    log("DOWNLOAD & ANALYSIS COMPLETE")
    log("=" * 70)

    if summary_rows:
        log(f"\n{'Currency':<6} {'Name':<22} {'Start':<12} {'Days':>6} {'Chg%':>8} {'Vol%':>6} {'BigMoves':>8}")
        log("-" * 75)

        for row in summary_rows:
            log(f"{row['currency']:<6} {row['name']:<22} {row['data_start']:<12} "
                f"{row['total_days']:>6} {row['total_change_pct']:>8.1f} "
                f"{row['annualized_volatility_pct']:>6.1f} {row['big_moves_gt2pct']:>8}")

        total_files = len([f for f in os.listdir(DATA_DIR) if f.endswith('.csv')])
        total_size = sum(os.path.getsize(os.path.join(DATA_DIR, f))
                        for f in os.listdir(DATA_DIR) if f.endswith('.csv')) / (1024 * 1024)
        log(f"\nTotal: {total_files} CSV files, {total_size:.2f} MB")
        log(f"All files saved to: {DATA_DIR}")

    log("\nDONE!")


if __name__ == "__main__":
    main()
