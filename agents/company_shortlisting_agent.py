import os
import pandas as pd
import numpy as np
from yahooquery import Screener, Ticker
from datetime import datetime, timedelta
import json

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

CACHE_EXPIRY_HOURS = 24

SECTOR_SCREENER_MAP = {
    "ms_technology": "Technology",
    "ms_financial_services": "Financial Services",
    "ms_healthcare": "Healthcare",
    "ms_consumer_cyclical": "Consumer Cyclical",
    "ms_communication_services": "Communication Services",
    "ms_industrials": "Industrials",
    "ms_consumer_defensive": "Consumer Defensive",
    "ms_utilities": "Utilities",
    "ms_real_estate": "Real Estate",
    "ms_basic_materials": "Basic Materials",
    "ms_energy": "Energy",
}


# --------------------------
# PART 1: DATA FETCH & CACHE
# --------------------------
def fetch_sector_data(sector: str, count: int = 50):
    """Fetch and cache sector data (summary + stats + history)."""

    screener_id = None
    for k, v in SECTOR_SCREENER_MAP.items():
        if v.lower() == sector.lower():
            screener_id = k
            break
    if not screener_id:
        raise ValueError(f"Invalid sector. Choose from: {list(SECTOR_SCREENER_MAP.values())}")

    # Cache paths
    summary_path = os.path.join(DATA_DIR, f"{sector}_summary.csv")
    stats_path = os.path.join(DATA_DIR, f"{sector}_stats.csv")
    hist_path = os.path.join(DATA_DIR, f"{sector}_history.csv")

    # Skip if cache is fresh
    if all(os.path.exists(p) for p in [summary_path, stats_path, hist_path]):
        mtime = datetime.fromtimestamp(os.path.getmtime(summary_path))
        if datetime.now() - mtime < timedelta(hours=CACHE_EXPIRY_HOURS):
            print(f"✅ Using cached data for {sector}")
            return summary_path, stats_path, hist_path

    print(f"📡 Fetching fresh data for {sector}...")

    # Step 1: Get symbols + names from screener
    s = Screener()
    screen = s.get_screeners(screener_id, count=count)
    quotes = screen[screener_id].get("quotes", [])
    screener_df = pd.DataFrame(quotes)[["symbol", "shortName"]]  # ✅ keep names
    symbols = screener_df["symbol"].tolist()

    # Step 2: Pull data in bulk with Ticker
    t = Ticker(symbols, asynchronous=False)

    summary = pd.DataFrame(t.summary_detail).T.reset_index().rename(columns={"index": "symbol"})
    stats = pd.DataFrame(t.key_stats).T.reset_index().rename(columns={"index": "symbol"})
    history = t.history(period="6mo", interval="1d").reset_index()

    # ✅ Merge names into summary
    summary = summary.merge(screener_df, on="symbol", how="left")

    # Step 3: Save locally
    summary.to_csv(summary_path, index=False)
    stats.to_csv(stats_path, index=False)
    history.to_csv(hist_path, index=False)

    print(f"💾 Data cached for {sector}: {len(symbols)} symbols")

    return summary_path, stats_path, hist_path



# --------------------------
# PART 2: SHORTLISTING
# --------------------------
def shortlist_sector(sector: str, top_n: int = 15):
    """Load cached sector data and shortlist companies."""
    summary_path, stats_path, hist_path = fetch_sector_data(sector)

    # Load cached data
    summary = pd.read_csv(summary_path)
    stats = pd.read_csv(stats_path)
    history = pd.read_csv(hist_path)

    # Basic filters
    df = summary[["symbol", "shortName", "marketCap", "averageVolume", "trailingPE"]].copy()
    df = df.dropna(subset=["marketCap", "averageVolume"])
    df = df[df["averageVolume"] > 1e6]  # liquidity filter

    # Compute momentum from history
    history = history[["symbol", "date", "close"]]
    momentum = (
        history.groupby("symbol")["close"]
        .apply(lambda x: (x.iloc[-1] / x.iloc[0]) - 1 if len(x) > 1 else np.nan)
        .rename("momentum_6m")
    )

    # Compute volatility from history
    def calc_vol(x):
        r = x.pct_change().dropna()
        return np.std(r) * np.sqrt(252) if not r.empty else np.nan

    volatility = (
        history.groupby("symbol")["close"].apply(calc_vol).rename("volatility")
    )

    # Join back
    df = df.merge(momentum, on="symbol", how="left")
    df = df.merge(volatility, on="symbol", how="left")

    # Ranking
    df = df.dropna(subset=["momentum_6m", "volatility"])
    df = df.sort_values(
        by=["momentum_6m", "averageVolume", "volatility"],
        ascending=[False, False, True],
    )

    return df.head(top_n).to_dict(orient="records")


# --------------------------
# DEMO RUN
# --------------------------
if __name__ == "__main__":
    # First run fetches data, later runs use cache
    shortlist = shortlist_sector("Technology", top_n=15)
    print(json.dumps(shortlist, indent=2))
