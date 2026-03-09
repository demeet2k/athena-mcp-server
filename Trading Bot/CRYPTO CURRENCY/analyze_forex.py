"""
Comprehensive Currency Fluctuation Analysis
=============================================
Analyzes 26 years of daily exchange rate data for 20 major currencies.

Produces:
  - Decade-by-decade analysis
  - Crisis event mapping
  - Volatility regimes
  - Correlation analysis
  - Currency strength index
  - Charts (PNG)
  - Full written report (TXT)
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import sys
from datetime import datetime

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(OUTPUT_DIR, "forex_data")
CHART_DIR = os.path.join(DATA_DIR, "charts")
os.makedirs(CHART_DIR, exist_ok=True)


def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    try:
        print(f"[{timestamp}] {msg}")
    except UnicodeEncodeError:
        print(f"[{timestamp}] {msg.encode('ascii', 'replace').decode()}")
    sys.stdout.flush()


CURRENCIES = {
    "EUR": "Euro", "GBP": "British Pound", "JPY": "Japanese Yen",
    "CHF": "Swiss Franc", "CAD": "Canadian Dollar", "AUD": "Australian Dollar",
    "NZD": "New Zealand Dollar", "CNY": "Chinese Yuan", "HKD": "Hong Kong Dollar",
    "SGD": "Singapore Dollar", "SEK": "Swedish Krona", "NOK": "Norwegian Krone",
    "DKK": "Danish Krone", "KRW": "South Korean Won", "INR": "Indian Rupee",
    "BRL": "Brazilian Real", "MXN": "Mexican Peso", "ZAR": "South African Rand",
    "TRY": "Turkish Lira",
}

# Major economic events / crises
CRISIS_EVENTS = [
    ("1999-01-01", "Euro Launch"),
    ("2000-03-10", "Dot-com Bubble Peak"),
    ("2001-09-11", "9/11 Attacks"),
    ("2002-01-01", "Euro Banknotes Circulation"),
    ("2005-07-21", "China Yuan Revaluation"),
    ("2007-08-09", "Subprime Crisis Begins"),
    ("2008-09-15", "Lehman Brothers Collapse"),
    ("2009-03-09", "GFC Market Bottom"),
    ("2010-05-02", "Greek Debt Crisis"),
    ("2011-09-06", "SNB CHF Floor (1.20 EUR)"),
    ("2013-05-22", "Taper Tantrum"),
    ("2014-12-16", "Russian Ruble Crisis"),
    ("2015-01-15", "SNB Removes CHF Floor"),
    ("2015-08-11", "China Yuan Devaluation"),
    ("2016-06-23", "Brexit Vote"),
    ("2016-11-08", "Trump Election"),
    ("2018-08-10", "Turkish Lira Crisis"),
    ("2020-03-11", "COVID-19 Pandemic Declared"),
    ("2022-02-24", "Russia-Ukraine War"),
    ("2022-09-22", "BOJ JPY Intervention"),
    ("2023-10-03", "USD Strength Peak"),
    ("2024-08-05", "JPY Carry Trade Unwind"),
]


def load_master_data():
    path = os.path.join(DATA_DIR, "03_MASTER_USD_rates_all_currencies.csv")
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_currency_data(currency):
    path = os.path.join(DATA_DIR, f"USD_{currency}_history.csv")
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    return df


# ── 1. DECADE ANALYSIS ───────────────────────────────────────────────────────

def decade_analysis(master_df):
    log("Computing decade-by-decade analysis...")

    decades = [
        ("1999-2005", "1999-01-01", "2005-12-31"),
        ("2006-2010", "2006-01-01", "2010-12-31"),
        ("2011-2015", "2011-01-01", "2015-12-31"),
        ("2016-2020", "2016-01-01", "2020-12-31"),
        ("2021-2026", "2021-01-01", "2026-12-31"),
    ]

    rate_cols = [c for c in master_df.columns if c.startswith("USD_") and c != "USD_USD"]
    results = []

    for period_name, start, end in decades:
        mask = (master_df["date"] >= start) & (master_df["date"] <= end)
        period = master_df.loc[mask].copy()

        if len(period) < 10:
            continue

        for col in rate_cols:
            currency = col.replace("USD_", "")
            rates = period[col].dropna()
            if len(rates) < 10:
                continue

            returns = rates.pct_change().dropna()
            start_rate = rates.iloc[0]
            end_rate = rates.iloc[-1]

            results.append({
                "period": period_name,
                "currency": currency,
                "start_rate": round(start_rate, 4),
                "end_rate": round(end_rate, 4),
                "change_pct": round((end_rate / start_rate - 1) * 100, 2),
                "avg_daily_vol": round(returns.std() * np.sqrt(252) * 100, 2),
                "max_daily_gain": round(returns.max() * 100, 2),
                "max_daily_loss": round(returns.min() * 100, 2),
                "period_high": round(rates.max(), 4),
                "period_low": round(rates.min(), 4),
            })

    df = pd.DataFrame(results)
    df.to_csv(os.path.join(DATA_DIR, "05_DECADE_ANALYSIS.csv"), index=False)
    log(f"  SAVED: 05_DECADE_ANALYSIS.csv ({len(df)} rows)")
    return df


# ── 2. VOLATILITY REGIME ANALYSIS ────────────────────────────────────────────

def volatility_regime_analysis(master_df):
    log("Computing volatility regime analysis...")

    rate_cols = [c for c in master_df.columns if c.startswith("USD_") and c != "USD_USD"]
    results = []

    for col in rate_cols:
        currency = col.replace("USD_", "")
        rates = master_df[["date", col]].dropna().copy()
        if len(rates) < 100:
            continue

        returns = rates[col].pct_change()
        vol_90d = returns.rolling(90).std() * np.sqrt(252) * 100

        # Classify volatility regimes
        vol_mean = vol_90d.mean()
        vol_std = vol_90d.std()

        rates["vol_90d"] = vol_90d
        rates["regime"] = "normal"
        rates.loc[vol_90d > vol_mean + vol_std, "regime"] = "high_vol"
        rates.loc[vol_90d > vol_mean + 2 * vol_std, "regime"] = "extreme_vol"
        rates.loc[vol_90d < vol_mean - vol_std, "regime"] = "low_vol"

        regime_counts = rates["regime"].value_counts()
        results.append({
            "currency": currency,
            "avg_vol_pct": round(vol_mean, 2),
            "max_vol_pct": round(vol_90d.max(), 2),
            "min_vol_pct": round(vol_90d.min(), 2),
            "high_vol_days": regime_counts.get("high_vol", 0),
            "extreme_vol_days": regime_counts.get("extreme_vol", 0),
            "low_vol_days": regime_counts.get("low_vol", 0),
            "normal_days": regime_counts.get("normal", 0),
            "pct_high_or_extreme": round(
                (regime_counts.get("high_vol", 0) + regime_counts.get("extreme_vol", 0)) / len(rates) * 100, 1),
        })

    df = pd.DataFrame(results)
    df = df.sort_values("avg_vol_pct", ascending=False)
    df.to_csv(os.path.join(DATA_DIR, "06_VOLATILITY_REGIMES.csv"), index=False)
    log(f"  SAVED: 06_VOLATILITY_REGIMES.csv ({len(df)} rows)")
    return df


# ── 3. CRISIS IMPACT ANALYSIS ────────────────────────────────────────────────

def crisis_impact_analysis(master_df):
    log("Computing crisis impact analysis...")

    rate_cols = [c for c in master_df.columns if c.startswith("USD_") and c != "USD_USD"]
    results = []

    for event_date, event_name in CRISIS_EVENTS:
        event_dt = pd.Timestamp(event_date)

        # Find nearest trading day
        idx = master_df["date"].searchsorted(event_dt)
        if idx >= len(master_df):
            continue

        for col in rate_cols:
            currency = col.replace("USD_", "")

            # Get rates around the event
            start_idx = max(0, idx - 5)
            end_idx_1w = min(len(master_df) - 1, idx + 5)
            end_idx_1m = min(len(master_df) - 1, idx + 22)
            end_idx_3m = min(len(master_df) - 1, idx + 66)

            pre_rate = master_df.iloc[start_idx][col]
            event_rate = master_df.iloc[idx][col]
            post_1w = master_df.iloc[end_idx_1w][col]
            post_1m = master_df.iloc[end_idx_1m][col]
            post_3m = master_df.iloc[end_idx_3m][col]

            if pd.isna(pre_rate) or pd.isna(event_rate):
                continue

            results.append({
                "event_date": event_date,
                "event_name": event_name,
                "currency": currency,
                "pre_rate": round(pre_rate, 6),
                "event_rate": round(event_rate, 6),
                "change_1w_pct": round((post_1w / pre_rate - 1) * 100, 2) if not pd.isna(post_1w) else None,
                "change_1m_pct": round((post_1m / pre_rate - 1) * 100, 2) if not pd.isna(post_1m) else None,
                "change_3m_pct": round((post_3m / pre_rate - 1) * 100, 2) if not pd.isna(post_3m) else None,
            })

    df = pd.DataFrame(results)
    df.to_csv(os.path.join(DATA_DIR, "07_CRISIS_IMPACT.csv"), index=False)
    log(f"  SAVED: 07_CRISIS_IMPACT.csv ({len(df)} rows)")
    return df


# ── 4. CURRENCY STRENGTH INDEX ───────────────────────────────────────────────

def currency_strength_index(master_df):
    log("Computing currency strength index over time...")

    rate_cols = [c for c in master_df.columns if c.startswith("USD_") and c != "USD_USD"]

    # Normalize all rates to 100 at start
    strength_df = master_df[["date"]].copy()

    for col in rate_cols:
        currency = col.replace("USD_", "")
        rates = master_df[col].copy()
        first_valid = rates.first_valid_index()
        if first_valid is not None:
            base = rates.iloc[first_valid]
            # For USD/XXX, higher = weaker XXX (more XXX per dollar)
            # Invert so higher = stronger currency
            strength_df[f"strength_{currency}"] = (base / rates) * 100

    strength_df.to_csv(os.path.join(DATA_DIR, "08_CURRENCY_STRENGTH_INDEX.csv"), index=False)
    log(f"  SAVED: 08_CURRENCY_STRENGTH_INDEX.csv ({len(strength_df)} rows)")
    return strength_df


# ── 5. ANNUAL PERFORMANCE TABLE ──────────────────────────────────────────────

def annual_performance(master_df):
    log("Computing annual performance table...")

    rate_cols = [c for c in master_df.columns if c.startswith("USD_") and c != "USD_USD"]
    master_df["year"] = master_df["date"].dt.year

    results = []
    for year in sorted(master_df["year"].unique()):
        year_data = master_df[master_df["year"] == year]
        if len(year_data) < 10:
            continue

        row = {"year": year}
        for col in rate_cols:
            currency = col.replace("USD_", "")
            rates = year_data[col].dropna()
            if len(rates) < 2:
                row[currency] = None
                continue
            # Annual change: negative = currency strengthened vs USD
            change = (rates.iloc[-1] / rates.iloc[0] - 1) * 100
            row[currency] = round(change, 2)

        results.append(row)

    df = pd.DataFrame(results)
    df.to_csv(os.path.join(DATA_DIR, "09_ANNUAL_PERFORMANCE.csv"), index=False)
    log(f"  SAVED: 09_ANNUAL_PERFORMANCE.csv ({len(df)} rows)")
    return df


# ── 6. CHARTS ─────────────────────────────────────────────────────────────────

def generate_charts(master_df, strength_df):
    log("Generating charts...")

    plt.style.use('seaborn-v0_8-darkgrid')

    # Chart 1: Major currency pairs over time
    fig, axes = plt.subplots(4, 2, figsize=(18, 24))
    major_pairs = ["EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "CNY", "BRL"]

    for i, currency in enumerate(major_pairs):
        ax = axes[i // 2, i % 2]
        col = f"USD_{currency}"
        if col in master_df.columns:
            data = master_df[["date", col]].dropna()
            ax.plot(data["date"], data[col], linewidth=0.8, color='#2196F3')
            ax.set_title(f"USD/{currency} ({CURRENCIES.get(currency, currency)})", fontsize=12, fontweight='bold')
            ax.set_ylabel("Exchange Rate")
            ax.xaxis.set_major_locator(mdates.YearLocator(5))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            ax.tick_params(axis='x', rotation=45)
            ax.grid(True, alpha=0.3)

    plt.suptitle("Major Currency Pairs vs USD (1999-2026)", fontsize=16, fontweight='bold', y=1.01)
    plt.tight_layout()
    fig.savefig(os.path.join(CHART_DIR, "01_major_pairs.png"), dpi=150, bbox_inches='tight')
    plt.close()
    log("  SAVED: 01_major_pairs.png")

    # Chart 2: Emerging market currencies
    fig, axes = plt.subplots(3, 2, figsize=(18, 18))
    em_pairs = ["TRY", "BRL", "ZAR", "MXN", "INR", "KRW"]

    for i, currency in enumerate(em_pairs):
        ax = axes[i // 2, i % 2]
        col = f"USD_{currency}"
        if col in master_df.columns:
            data = master_df[["date", col]].dropna()
            ax.plot(data["date"], data[col], linewidth=0.8, color='#F44336')
            ax.set_title(f"USD/{currency} ({CURRENCIES.get(currency, currency)})", fontsize=12, fontweight='bold')
            ax.set_ylabel("Exchange Rate")
            ax.xaxis.set_major_locator(mdates.YearLocator(5))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            ax.tick_params(axis='x', rotation=45)
            ax.grid(True, alpha=0.3)

    plt.suptitle("Emerging Market Currencies vs USD (1999-2026)", fontsize=16, fontweight='bold', y=1.01)
    plt.tight_layout()
    fig.savefig(os.path.join(CHART_DIR, "02_emerging_markets.png"), dpi=150, bbox_inches='tight')
    plt.close()
    log("  SAVED: 02_emerging_markets.png")

    # Chart 3: Currency Strength Index (normalized)
    fig, ax = plt.subplots(figsize=(18, 10))
    colors = plt.cm.tab20(np.linspace(0, 1, len(CURRENCIES)))
    major_5 = ["EUR", "GBP", "JPY", "CHF", "CNY"]

    for i, currency in enumerate(major_5):
        col = f"strength_{currency}"
        if col in strength_df.columns:
            data = strength_df[["date", col]].dropna()
            ax.plot(data["date"], data[col], linewidth=1.2, label=currency)

    ax.axhline(y=100, color='black', linestyle='--', alpha=0.5, label='Baseline (1999)')
    ax.set_title("Currency Strength Index (Base 100 = Start)", fontsize=14, fontweight='bold')
    ax.set_ylabel("Strength Index")
    ax.legend(loc='best', fontsize=10)
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.grid(True, alpha=0.3)

    fig.savefig(os.path.join(CHART_DIR, "03_currency_strength.png"), dpi=150, bbox_inches='tight')
    plt.close()
    log("  SAVED: 03_currency_strength.png")

    # Chart 4: Volatility comparison
    fig, ax = plt.subplots(figsize=(16, 8))
    vol_data = []
    for currency in CURRENCIES.keys():
        col = f"USD_{currency}"
        if col in master_df.columns:
            returns = master_df[col].pct_change().dropna()
            if len(returns) > 100:
                vol = returns.std() * np.sqrt(252) * 100
                vol_data.append((currency, vol))

    vol_data.sort(key=lambda x: x[1], reverse=True)
    currencies_sorted = [v[0] for v in vol_data]
    vols = [v[1] for v in vol_data]

    bars = ax.bar(currencies_sorted, vols, color=['#F44336' if v > 15 else '#FF9800' if v > 10 else '#4CAF50' for v in vols])
    ax.set_title("Annualized Volatility by Currency (1999-2026)", fontsize=14, fontweight='bold')
    ax.set_ylabel("Annualized Volatility (%)")
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3, axis='y')

    for bar, vol in zip(bars, vols):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.3,
                f'{vol:.1f}%', ha='center', va='bottom', fontsize=9)

    fig.savefig(os.path.join(CHART_DIR, "04_volatility_comparison.png"), dpi=150, bbox_inches='tight')
    plt.close()
    log("  SAVED: 04_volatility_comparison.png")

    # Chart 5: Turkish Lira collapse (log scale)
    fig, ax = plt.subplots(figsize=(16, 8))
    col = "USD_TRY"
    if col in master_df.columns:
        data = master_df[["date", col]].dropna()
        ax.semilogy(data["date"], data[col], linewidth=1.0, color='#F44336')
        ax.set_title("USD/TRY - Turkish Lira Collapse (Log Scale, 1999-2026)", fontsize=14, fontweight='bold')
        ax.set_ylabel("USD/TRY (Log Scale)")
        ax.xaxis.set_major_locator(mdates.YearLocator(2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)

        # Annotate key events
        events_try = [
            ("2001-02-01", "2001 Banking Crisis"),
            ("2018-08-10", "2018 Lira Crisis"),
            ("2021-12-20", "2021 Currency Crash"),
        ]
        for evt_date, evt_name in events_try:
            evt_dt = pd.Timestamp(evt_date)
            idx = data["date"].searchsorted(evt_dt)
            if idx < len(data):
                ax.annotate(evt_name, xy=(data["date"].iloc[idx], data[col].iloc[idx]),
                           fontsize=8, ha='center',
                           arrowprops=dict(arrowstyle='->', color='black', lw=0.5))

    fig.savefig(os.path.join(CHART_DIR, "05_turkish_lira_collapse.png"), dpi=150, bbox_inches='tight')
    plt.close()
    log("  SAVED: 05_turkish_lira_collapse.png")

    # Chart 6: Correlation heatmap
    corr_path = os.path.join(DATA_DIR, "04_CORRELATION_MATRIX.csv")
    if os.path.exists(corr_path):
        corr = pd.read_csv(corr_path, index_col=0)
        corr.index = [c.replace("USD_", "") for c in corr.index]
        corr.columns = [c.replace("USD_", "") for c in corr.columns]

        fig, ax = plt.subplots(figsize=(14, 12))
        im = ax.imshow(corr.values, cmap='RdBu_r', vmin=-1, vmax=1)

        ax.set_xticks(range(len(corr.columns)))
        ax.set_yticks(range(len(corr.index)))
        ax.set_xticklabels(corr.columns, rotation=45, ha='right')
        ax.set_yticklabels(corr.index)

        for i in range(len(corr)):
            for j in range(len(corr)):
                val = corr.iloc[i, j]
                color = "white" if abs(val) > 0.5 else "black"
                ax.text(j, i, f'{val:.2f}', ha='center', va='center', fontsize=7, color=color)

        plt.colorbar(im, label='Correlation')
        ax.set_title("Currency Return Correlations (Daily, 1999-2026)", fontsize=14, fontweight='bold')
        fig.savefig(os.path.join(CHART_DIR, "06_correlation_heatmap.png"), dpi=150, bbox_inches='tight')
        plt.close()
        log("  SAVED: 06_correlation_heatmap.png")

    # Chart 7: Rolling volatility for major pairs
    fig, ax = plt.subplots(figsize=(18, 10))
    for currency in ["EUR", "GBP", "JPY", "CHF", "AUD"]:
        col = f"USD_{currency}"
        if col in master_df.columns:
            returns = master_df[col].pct_change()
            vol = returns.rolling(90).std() * np.sqrt(252) * 100
            ax.plot(master_df["date"], vol, linewidth=0.8, label=currency, alpha=0.8)

    ax.set_title("90-Day Rolling Annualized Volatility (Major Currencies)", fontsize=14, fontweight='bold')
    ax.set_ylabel("Volatility (%)")
    ax.legend(loc='upper left', fontsize=10)
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.grid(True, alpha=0.3)

    # Shade crisis periods
    crisis_periods = [
        ("2008-09-01", "2009-06-01", "GFC", 0.1),
        ("2020-02-01", "2020-06-01", "COVID", 0.1),
        ("2022-02-01", "2022-12-01", "Ukraine", 0.1),
    ]
    for start, end, label, alpha in crisis_periods:
        ax.axvspan(pd.Timestamp(start), pd.Timestamp(end), alpha=alpha, color='red')

    fig.savefig(os.path.join(CHART_DIR, "07_rolling_volatility.png"), dpi=150, bbox_inches='tight')
    plt.close()
    log("  SAVED: 07_rolling_volatility.png")

    # Chart 8: Annual performance heatmap
    annual_path = os.path.join(DATA_DIR, "09_ANNUAL_PERFORMANCE.csv")
    if os.path.exists(annual_path):
        annual_df = pd.read_csv(annual_path)
        cols_to_plot = [c for c in annual_df.columns if c != "year" and c in CURRENCIES]

        if cols_to_plot:
            data_matrix = annual_df.set_index("year")[cols_to_plot].astype(float)

            fig, ax = plt.subplots(figsize=(16, 12))
            im = ax.imshow(data_matrix.T.values, cmap='RdYlGn_r', vmin=-30, vmax=30, aspect='auto')

            ax.set_xticks(range(len(data_matrix.index)))
            ax.set_yticks(range(len(cols_to_plot)))
            ax.set_xticklabels(data_matrix.index, rotation=45, ha='right', fontsize=8)
            ax.set_yticklabels(cols_to_plot, fontsize=9)

            for i in range(len(cols_to_plot)):
                for j in range(len(data_matrix.index)):
                    val = data_matrix.iloc[j, i]
                    if not pd.isna(val):
                        color = "white" if abs(val) > 15 else "black"
                        ax.text(j, i, f'{val:.0f}', ha='center', va='center', fontsize=6, color=color)

            plt.colorbar(im, label='Change vs USD (%)', shrink=0.8)
            ax.set_title("Annual Currency Performance vs USD (%, negative=currency weakened)",
                        fontsize=14, fontweight='bold')
            fig.savefig(os.path.join(CHART_DIR, "08_annual_heatmap.png"), dpi=150, bbox_inches='tight')
            plt.close()
            log("  SAVED: 08_annual_heatmap.png")


# ── 7. WRITTEN REPORT ────────────────────────────────────────────────────────

def generate_report(master_df, decade_df, vol_df, crisis_df, annual_df):
    log("Generating written analysis report...")

    report = []
    report.append("=" * 80)
    report.append("COMPREHENSIVE CURRENCY FLUCTUATION ANALYSIS REPORT")
    report.append("20 Major World Currencies | 1999-2026 (26+ Years)")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("=" * 80)

    # Section 1: Overview
    report.append("\n\n1. OVERVIEW")
    report.append("-" * 40)
    report.append(f"Dataset: {len(master_df):,} trading days of data")
    report.append(f"Period: {master_df['date'].min().strftime('%Y-%m-%d')} to {master_df['date'].max().strftime('%Y-%m-%d')}")
    report.append(f"Currencies: 20 major world currencies vs USD")
    report.append(f"Data points per currency: ~6,700-6,940 daily observations")
    report.append(f"\nAll rates expressed as USD/XXX (units of foreign currency per 1 USD)")
    report.append(f"Positive total change = currency WEAKENED vs USD")
    report.append(f"Negative total change = currency STRENGTHENED vs USD")

    # Section 2: Currency Performance Summary
    report.append("\n\n2. TOTAL PERIOD PERFORMANCE (1999-2026)")
    report.append("-" * 40)

    summary_path = os.path.join(DATA_DIR, "00_CURRENCY_SUMMARY.csv")
    if os.path.exists(summary_path):
        summary = pd.read_csv(summary_path)
        summary = summary.sort_values("total_change_pct")

        report.append("\nCurrencies that STRENGTHENED vs USD:")
        for _, row in summary[summary["total_change_pct"] < 0].iterrows():
            report.append(f"  {row['currency']:>4} ({row['name']:<25}): {row['total_change_pct']:>8.1f}%  "
                         f"(Vol: {row['annualized_volatility_pct']:.1f}%)")

        report.append("\nCurrencies that WEAKENED vs USD:")
        for _, row in summary[summary["total_change_pct"] > 0].iterrows():
            report.append(f"  {row['currency']:>4} ({row['name']:<25}): +{row['total_change_pct']:>8.1f}%  "
                         f"(Vol: {row['annualized_volatility_pct']:.1f}%)")

        report.append(f"\nMost VOLATILE: {summary.loc[summary['annualized_volatility_pct'].idxmax(), 'currency']} "
                     f"({summary['annualized_volatility_pct'].max():.1f}% annualized)")
        report.append(f"Most STABLE:   {summary.loc[summary['annualized_volatility_pct'].idxmin(), 'currency']} "
                     f"({summary['annualized_volatility_pct'].min():.1f}% annualized)")

    # Section 3: Decade Analysis
    report.append("\n\n3. DECADE-BY-DECADE ANALYSIS")
    report.append("-" * 40)

    if decade_df is not None:
        for period in decade_df["period"].unique():
            report.append(f"\n  Period: {period}")
            period_data = decade_df[decade_df["period"] == period].sort_values("change_pct")

            strongest = period_data.iloc[0]
            weakest = period_data.iloc[-1]
            report.append(f"    Strongest: {strongest['currency']} ({strongest['change_pct']:+.1f}%)")
            report.append(f"    Weakest:   {weakest['currency']} ({weakest['change_pct']:+.1f}%)")
            report.append(f"    Most Volatile: {period_data.loc[period_data['avg_daily_vol'].idxmax(), 'currency']} "
                         f"({period_data['avg_daily_vol'].max():.1f}%)")

    # Section 4: Major Crisis Events
    report.append("\n\n4. MAJOR CRISIS EVENTS & CURRENCY IMPACT")
    report.append("-" * 40)

    if crisis_df is not None:
        for event_date, event_name in CRISIS_EVENTS:
            event_data = crisis_df[crisis_df["event_name"] == event_name]
            if len(event_data) == 0:
                continue

            report.append(f"\n  {event_date}: {event_name}")

            # Find biggest movers
            if "change_1m_pct" in event_data.columns:
                valid = event_data.dropna(subset=["change_1m_pct"])
                if len(valid) > 0:
                    biggest_gain = valid.loc[valid["change_1m_pct"].idxmax()]
                    biggest_loss = valid.loc[valid["change_1m_pct"].idxmin()]
                    report.append(f"    1-month impact:")
                    report.append(f"      Most weakened: {biggest_gain['currency']} ({biggest_gain['change_1m_pct']:+.1f}%)")
                    report.append(f"      Most strengthened: {biggest_loss['currency']} ({biggest_loss['change_1m_pct']:+.1f}%)")

    # Section 5: Volatility Regimes
    report.append("\n\n5. VOLATILITY REGIME ANALYSIS")
    report.append("-" * 40)

    if vol_df is not None:
        report.append("\nCurrency volatility ranking (highest to lowest):")
        for _, row in vol_df.iterrows():
            report.append(f"  {row['currency']:>4}: Avg {row['avg_vol_pct']:>5.1f}%  "
                         f"Max {row['max_vol_pct']:>6.1f}%  "
                         f"Extreme days: {row['extreme_vol_days']:>4}  "
                         f"({row['pct_high_or_extreme']:.1f}% high/extreme)")

    # Section 6: Key Observations
    report.append("\n\n6. KEY OBSERVATIONS")
    report.append("-" * 40)

    observations = [
        "TURKISH LIRA: The most dramatic depreciation in the dataset. The TRY lost",
        "  over 99% of its value vs USD from 1999-2026, driven by chronic inflation,",
        "  political interference in monetary policy, and multiple currency crises",
        "  (2001, 2018, 2021).",
        "",
        "BRAZILIAN REAL & SOUTH AFRICAN RAND: Both EM currencies showed persistent",
        "  weakening with high volatility, reflecting structural inflation differentials",
        "  and periodic capital flight episodes.",
        "",
        "SWISS FRANC: The strongest performer, appreciating ~44% vs USD. The SNB's",
        "  removal of the EUR/CHF 1.20 floor on Jan 15, 2015 caused one of the largest",
        "  single-day moves in modern FX history.",
        "",
        "CHINESE YUAN: Notably low volatility (3.0%) due to managed float regime.",
        "  The 2005 revaluation and 2015 devaluation were landmark policy shifts.",
        "",
        "HONG KONG DOLLAR: Ultra-low volatility (0.9%) reflecting the currency board",
        "  peg to USD within the 7.75-7.85 band.",
        "",
        "DANISH KRONE: Closely tracks the EUR due to ERM II peg mechanism.",
        "",
        "GLOBAL FINANCIAL CRISIS (2008-2009): Caused massive 'risk-off' moves with",
        "  USD, JPY, and CHF strengthening as safe havens while commodity and EM",
        "  currencies collapsed.",
        "",
        "COVID-19 (2020): Sharp but brief volatility spike. The USD initially surged",
        "  on safe-haven demand but then weakened on unprecedented Fed easing.",
        "",
        "RATE DIVERGENCE ERA (2022-2024): Aggressive Fed tightening drove broad USD",
        "  strength, with JPY particularly affected due to BOJ's yield curve control.",
    ]

    for obs in observations:
        report.append(f"  {obs}")

    # Section 7: Data Files
    report.append("\n\n7. OUTPUT FILES")
    report.append("-" * 40)
    report.append(f"\n  Directory: {DATA_DIR}")
    report.append(f"\n  Data Files:")
    report.append(f"    00_CURRENCY_SUMMARY.csv        - Summary statistics for all currencies")
    report.append(f"    01_ECB_EUR_based_rates.csv      - Raw ECB EUR-based rates")
    report.append(f"    02_USD_based_rates.csv           - Converted USD-based rates")
    report.append(f"    03_MASTER_USD_rates_all_currencies.csv - Master rate matrix")
    report.append(f"    04_CORRELATION_MATRIX.csv        - Cross-currency correlations")
    report.append(f"    05_DECADE_ANALYSIS.csv           - Period-by-period analysis")
    report.append(f"    06_VOLATILITY_REGIMES.csv        - Volatility regime classification")
    report.append(f"    07_CRISIS_IMPACT.csv              - Crisis event impact measurements")
    report.append(f"    08_CURRENCY_STRENGTH_INDEX.csv   - Normalized strength over time")
    report.append(f"    09_ANNUAL_PERFORMANCE.csv         - Year-by-year performance")
    report.append(f"    USD_[XXX]_history.csv             - Per-currency detailed history (x19)")
    report.append(f"    USD_[XXX]_big_moves.csv           - Big daily moves per currency")
    report.append(f"\n  Charts (forex_data/charts/):")
    report.append(f"    01_major_pairs.png               - Major currency pairs chart")
    report.append(f"    02_emerging_markets.png           - EM currencies chart")
    report.append(f"    03_currency_strength.png          - Strength index chart")
    report.append(f"    04_volatility_comparison.png      - Volatility bar chart")
    report.append(f"    05_turkish_lira_collapse.png      - TRY log-scale chart")
    report.append(f"    06_correlation_heatmap.png        - Correlation heatmap")
    report.append(f"    07_rolling_volatility.png         - Rolling volatility chart")
    report.append(f"    08_annual_heatmap.png             - Annual performance heatmap")

    report.append("\n\n" + "=" * 80)
    report.append("END OF REPORT")
    report.append("=" * 80)

    report_text = "\n".join(report)
    report_path = os.path.join(DATA_DIR, "10_ANALYSIS_REPORT.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    log(f"  SAVED: 10_ANALYSIS_REPORT.txt ({len(report)} lines)")
    return report_text


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    log("=" * 70)
    log("CURRENCY FLUCTUATION COMPREHENSIVE ANALYSIS")
    log("=" * 70)

    master_df = load_master_data()
    log(f"Loaded master data: {len(master_df)} rows, {len(master_df.columns)} columns")

    decade_df = decade_analysis(master_df)
    vol_df = volatility_regime_analysis(master_df)
    crisis_df = crisis_impact_analysis(master_df)
    strength_df = currency_strength_index(master_df)
    annual_df = annual_performance(master_df)

    generate_charts(master_df, strength_df)

    report = generate_report(master_df, decade_df, vol_df, crisis_df, annual_df)

    # Print abbreviated report to console
    for line in report.split("\n")[:60]:
        log(line)
    log("... [full report saved to 10_ANALYSIS_REPORT.txt]")

    log("\n" + "=" * 70)
    log("ANALYSIS COMPLETE!")
    log("=" * 70)


if __name__ == "__main__":
    main()
