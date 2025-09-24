from langchain_core.tools import tool
from pydantic import BaseModel
from typing import List, Dict, Any
from langchain.tools import tool
import json, re
import joblib
from typing import Any

clf = joblib.load('external_utils\logreg_sentiment.pkl')
vect = joblib.load('external_utils\Tfidf_vectorizer2.pkl')

def safe_json_loads(text: str, fallback: Any = None) -> Any:
    if fallback is None:
        fallback = {}
    try:
        return json.loads(text)
    except Exception:
        return fallback
    

@tool("sentiment_analysis", return_direct=False)
def sentiment_analysis(input: dict) -> dict:
    """
    Sentiment agent using Logistic Regression.
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

    # Get all titles
    titles = [item.get("title","") for item in news + reddit]
    X_vec = vect.transform(titles)
    preds = clf.predict(X_vec)
    pred_proba = clf.predict_proba(X_vec)

    # Map classes
    class_idx = {c: i for i, c in enumerate(clf.classes_)}
    pos_key = next(k for k in class_idx if 'positive' in k.lower())
    neg_key = next(k for k in class_idx if 'negative' in k.lower())

    # Compute overall score using probabilities
    all_probs = []
    for prob in pred_proba:
        pos_prob = prob[class_idx[pos_key]]
        neg_prob = prob[class_idx[neg_key]]
        all_probs.append(pos_prob - neg_prob)  # +1 = fully positive, -1 = fully negative
    overall_score = sum(all_probs) / max(len(all_probs), 1)



    if overall_score > 0.2:
        overall_sentiment = "Positive"
        recommendation = "INVEST"
    elif overall_score < -0.2:
        overall_sentiment = "Negative"
        recommendation = "AVOID"
    else:
        overall_sentiment = "Neutral"
        recommendation = "HOLD"


    # Breakdown
    breakdown = []
    for t, p, prob in zip(titles, preds, pred_proba):
        breakdown.append({
            "title": t,
            "label": p,
            "prob_pos": float(prob[class_idx[pos_key]]),
            "prob_neg": float(prob[class_idx[neg_key]]),

        })

    return {
        "ticker": ticker,
        "overall_score": overall_score,
        "overall_sentiment": overall_sentiment,
        "recommendation": recommendation,
        "breakdown": breakdown,
        "summary": f"Overall sentiment for {ticker} is {overall_sentiment} (score {overall_score:.2f})."
    }



# # Simple sentiment lexicons (you can expand these later)
# POSITIVE_WORDS = {"gain", "positive", "growth", "bull", "buy", "beat", "strong", "up", "profit", "win"}
# NEGATIVE_WORDS = {"loss", "negative", "down", "bear", "sell", "miss", "weak", "risk", "drop", "fear"}

# def score_text(text: str) -> int:
#     """Very simple scoring: +1 for positive word, -1 for negative word."""
#     text_lower = text.lower()
#     score = 0
#     for word in POSITIVE_WORDS:
#         if word in text_lower:
#             score += 1
#     for word in NEGATIVE_WORDS:
#         if word in text_lower:
#             score -= 1
#     return score



# def safe_json_loads(text: str, fallback: Any = None) -> Any:
#     if fallback is None:
#         fallback = {}
#     try:
#         return json.loads(text)
#     except Exception:
#         m = re.search(r"\{.*\}|\[.*\]", text, re.S)
#         if m:
#             try:
#                 return json.loads(m.group())
#             except Exception:
#                 return fallback
#         return fallback
    

# @tool("sentiment_analysis", return_direct=False)
# def sentiment_analysis(input: dict) -> dict:
#     """
    
#     Deterministic sentiment analysis (no LLM).
#     Accepts either a SentimentInput object or a dict/JSON-like object.
#     Returns JSON with overall score, breakdown, summary.
#     """
 
#     if isinstance(input, str):
#         payload = safe_json_loads(input)
#     elif isinstance(input, dict):
#         payload = input
#     else:
#         return {"error": "input must be dict or JSON string"}

#     ticker = payload.get("ticker", "UNKNOWN")
#     # Corrected: Access 'news' and 'reddit' directly from the payload
#     news = payload.get("news", [])
#     reddit = payload.get("reddit", [])

#     # Score each item
#     news_scores = [score_text(item.get("title", "")) for item in news]
#     reddit_scores = [score_text(item.get("title", "")) for item in reddit]

#     all_scores = news_scores + reddit_scores
#     overall_score = sum(all_scores) / max(len(all_scores), 1)

#     # Determine sentiment & recommendation
#     if overall_score > 0.3:
#         sentiment = "Positive"
#         recommendation = "INVEST"
#     elif overall_score < -0.3:
#         sentiment = "Negative"
#         recommendation = "AVOID"
#     else:
#         sentiment = "Neutral"
#         recommendation = "HOLD"

#     return {
#         "ticker": ticker,
#         "overall_score": overall_score,
#         "overall_sentiment": sentiment,
#         "recommendation": recommendation,
#         "breakdown": {
#             "news": news_scores,
#             "reddit": reddit_scores,
#         },
#         "summary": f"Overall sentiment for {ticker} is {sentiment} (score {overall_score:.2f})."
#     }



# SENTIMENT_PROMPT = """
# You are a concise sentiment analysis assistant. 
# The following input is JSON describing a ticker and sources of text.
# Analyze sentiment and return a JSON with overall score, breakdown per item, and a short summary.
# Do not output anything except valid JSON.
# Input: {input_json}
# """

# @tool("sentiment_analysis", return_direct=False)
# def sentiment_analysis(input_json: str) -> Any:
#     """
#     input_json: either a JSON string or Python-dumpable object describing sources.
#     Example:
#     {
#       "ticker": "AAPL",
#       "sources": {
#          "news": [{"title":"Apple beats...", "snippet":"..."}],
#          "reddit": [{"title":"AAPL moon", "body":"...","score": 120}]
#       }
#     }
#     Returns structured JSON with overall score, breakdown, summary.
#     """
#     try:
#         if isinstance(input_json, str):
#             payload = json.loads(input_json)
#         else:
#             payload = input_json
#     except Exception:
#         return {"error": "invalid input_json"}

#     # Build prompt and call LLM
#     input_text = json.dumps(payload)
#     prompt = ChatPromptTemplate.from_template(SENTIMENT_PROMPT)
#     messages = prompt.format_messages(input_json=input_text)
#     # call LLM
#     resp = llm.invoke(messages)
#     content = getattr(resp, "content", None) or getattr(resp, "text", "")
#     result = safe_json_loads(content, fallback={"error": "could not parse llm output", "raw": content})
#     return result