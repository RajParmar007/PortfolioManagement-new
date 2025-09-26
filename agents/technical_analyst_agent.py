from langchain.tools import tool
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import json, re
from typing import Any, Dict
from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


# Load environment variables
load_dotenv()

# API keys
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")




def _ensure_df(data: Any) -> pd.DataFrame:
    """
    Accepts:
    - pandas DataFrame with index = date and columns ['open','high','low','close','volume']
    - JSON string as produced by your get_stock_data (orient='index')
    - dict similar to DataFrame.to_dict('index')
    Returns DataFrame sorted ascending by date (old -> new)
    """
    if isinstance(data, pd.DataFrame):
        df = data.copy()
    elif isinstance(data, str):
        # try parse JSON
        try:
            obj = json.loads(data)
            df = pd.DataFrame.from_dict(obj, orient='index')
        except Exception:
            raise ValueError("String input not valid JSON for OHLC")
    elif isinstance(data, dict):
        df = pd.DataFrame.from_dict(data, orient='index')
    else:
        raise ValueError("Unsupported data type for OHLC")

    # standardize column names
    df = df.rename(columns=lambda c: c.strip().lower())
    # ensure required cols
    for col in ['open','high','low','close','volume']:
        if col not in df.columns:
            raise ValueError(f"Missing column '{col}' in OHLC data")
    # convert to numeric
    df[['open','high','low','close','volume']] = df[['open','high','low','close','volume']].astype(float)
    # index -> datetime and sort ascending
    df.index = pd.to_datetime(df.index)
    df = df.sort_index(ascending=True)
    return df


def _sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window, min_periods=1).mean()

def _ema(series: pd.Series, window: int) -> pd.Series:
    return series.ewm(span=window, adjust=False).mean()

def _rsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ma_up = up.ewm(alpha=1/window, adjust=False).mean()
    ma_down = down.ewm(alpha=1/window, adjust=False).mean()
    rs = ma_up / (ma_down + 1e-8)
    rsi = 100 - (100 / (1 + rs))
    return rsi

def _macd(series: pd.Series, fast=12, slow=26, signal=9):
    ema_fast = _ema(series, fast)
    ema_slow = _ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

@tool("technical_indicators", return_direct=False)
def technical_indicators(ohlc: Any, lookback:int = 30) -> Dict[str, Any]:
    """
    ohlc: DataFrame, JSON string or dict with last N daily bars (index=date)
    lookback: how many days to summarize (default 30)
    Returns dict with:
      - last_close
      - returns_lookback_pct
      - sma: {period: value}
      - ema: {period: value}
      - rsi: last value
      - macd: last values
      - simple_signal: 'buy'|'hold'|'sell' (naive heuristic)
    """
    try:
        df = _ensure_df(ohlc)
    except Exception as e:
        return {"error": str(e)}

    if len(df) < 2:
        return {"error": "not enough data points"}

    # focus on the last lookback rows
    df_lb = df.tail(lookback)
    close = df_lb['close']

    last_close = float(close.iloc[-1])
    returns_pct = ((close.iloc[-1] / close.iloc[0]) - 1) * 100.0

    sma_periods = [5, 10, 20, 50]
    ema_periods = [10, 20, 50]
    sma = {p: float(_sma(close, p).iloc[-1]) for p in sma_periods if len(close) >= p}
    ema = {p: float(_ema(close, p).iloc[-1]) for p in ema_periods if len(close) >= p}
    rsi_val = float(_rsi(close, 14).iloc[-1]) if len(close) >= 14 else None
    macd_line, signal_line, hist = _macd(close)
    macd = {
        "macd": float(macd_line.iloc[-1]),
        "signal": float(signal_line.iloc[-1]),
        "hist": float(hist.iloc[-1])
    }

    # Naive signal heuristic:
    # - if short-term SMA > long-term SMA and MACD hist positive => buy
    # - if short-term SMA < long-term SMA and MACD hist negative => sell
    simple_signal = "hold"
    try:
        if 5 in sma and 20 in sma:
            if sma[5] > sma[20] and macd["hist"] > 0:
                simple_signal = "buy"
            elif sma[5] < sma[20] and macd["hist"] < 0:
                simple_signal = "sell"
    except Exception:
        simple_signal = "hold"

    return {
        "last_close": last_close,
        "returns_lookback_pct": returns_pct,
        "sma": sma,
        "ema": ema,
        "rsi": rsi_val,
        "macd": macd,
        "simple_signal": simple_signal,
        "bars_returned": len(df_lb)
    }


def safe_json_loads(text: str, fallback: Any = None) -> Any:
    if fallback is None:
        fallback = {}
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}|\[.*\]", text, re.S)
        if m:
            try:
                return json.loads(m.group())
            except Exception:
                return fallback
        return fallback


