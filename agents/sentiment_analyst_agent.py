import json
import joblib
import numpy as np
from langchain.tools import tool
from sentence_transformers import SentenceTransformer

# Load the FinBERT embedder and your trained Logistic Regression model
embedder = SentenceTransformer("yiyanghkust/finbert-tone")
clf = joblib.load("external_utils/logreg_sentiment2.pkl")

# --- JSON Safety Helper ---
def safe_json_loads(text: str, fallback=None):
    if fallback is None:
        fallback = {}
    try:
        return json.loads(text)
    except Exception:
        return fallback

# --- Sentiment Analysis Agent ---
@tool("sentiment_analysis", return_direct=False)
def sentiment_analysis(input: dict) -> dict:
    """
    Sentiment agent using FinBERT embeddings + Logistic Regression.
    Input JSON: { "ticker": "TSLA", "news": [{"title": "..."}], "reddit": [{"title": "..."}] }
    Output JSON: overall sentiment, score, breakdown.
    """
    if isinstance(input, str):
        payload = safe_json_loads(input)
    elif isinstance(input, dict):
        payload = input
    else:
        return {"error": "Input must be dict or JSON string"}

    ticker = payload.get("ticker", "UNKNOWN")
    news = payload.get("news", [])
    reddit = payload.get("reddit", [])

    # 1️⃣ Combine all text titles
    titles = [item.get("title", "") for item in news + reddit]
    if not titles:
        return {"error": "No titles found in input."}

    # 2️⃣ Encode with FinBERT embedder
    X_vec = embedder.encode(titles, batch_size=16, show_progress_bar=False)

    # 3️⃣ Predict using Logistic Regression
    preds = clf.predict(X_vec)
    pred_proba = clf.predict_proba(X_vec)

    # 4️⃣ Map class indices
    class_idx = {c: i for i, c in enumerate(clf.classes_)}
    pos_key = next((k for k in class_idx if "pos" in k.lower()), None)
    neg_key = next((k for k in class_idx if "neg" in k.lower()), None)

    if pos_key is None or neg_key is None:
        return {"error": f"Expected positive/negative classes in model, found {list(clf.classes_)}"}

    # 5️⃣ Compute overall sentiment score
    all_probs = []
    for prob in pred_proba:
        pos_prob = prob[class_idx[pos_key]]
        neg_prob = prob[class_idx[neg_key]]
        all_probs.append(pos_prob - neg_prob)

    overall_score = float(np.mean(all_probs)) if len(all_probs) > 0 else 0.0

    # 6️⃣ Label sentiment from score
    if overall_score > 0.2:
        overall_sentiment = "Positive"
        recommendation = "INVEST"
    elif overall_score < -0.2:
        overall_sentiment = "Negative"
        recommendation = "AVOID"
    else:
        overall_sentiment = "Neutral"
        recommendation = "HOLD"

    # 7️⃣ Breakdown
    breakdown = []
    for t, p, prob in zip(titles, preds, pred_proba):
        breakdown.append({
            "title": t,
            "label": p,
            "prob_pos": float(prob[class_idx[pos_key]]),
            "prob_neg": float(prob[class_idx[neg_key]]),
        })

    # 8️⃣ Final structured output
    return {
        "ticker": ticker,
        "overall_score": overall_score,
        "overall_sentiment": overall_sentiment,
        "recommendation": recommendation,
        "breakdown": breakdown,
        "summary": f"Overall sentiment for {ticker} is {overall_sentiment} (score {overall_score:.2f})."
    }