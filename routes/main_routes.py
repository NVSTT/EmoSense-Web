from flask import Blueprint, render_template, request
from model.ollama import OllamaClient, DEFAULT_OLLAMA_HOST, DEFAULT_OLLAMA_MODEL
from servises.analyze import analyze_sentiment,generate_full_reasoning, generate_ai_comment_with_ollama, generate_sentiment_explanation

bp = Blueprint('main', __name__)
ollama = OllamaClient(DEFAULT_OLLAMA_HOST, DEFAULT_OLLAMA_MODEL)

@bp.route("/", methods=["GET", "POST"])
def index():
    result = None
    analysis_type = "objective"
    if request.method == "POST":
        post_text = request.form["post"].strip()
        analysis_type = request.form.get("analysis_type", "objective")
        use_llm = (analysis_type == "subjective") 

        if post_text:
            sentiment_data = analyze_sentiment(post_text, use_llm, ollama)
            sentiment = sentiment_data['sentiment']
            scores = sentiment_data.get('scores', {"positive": 0.33, "negative": 0.33, "neutral": 0.34})

            if "positive" in sentiment.lower():
                sentiment_text = "😊 Positive"
            elif "negative" in sentiment.lower():
                sentiment_text = "😞 Negative"
            else:
                sentiment_text = "😐 Neutral"

            comment = generate_ai_comment_with_ollama(post_text, sentiment, ollama)
            explanation = generate_sentiment_explanation(post_text, sentiment, ollama)
            full_reasoning = generate_full_reasoning(post_text, scores, ollama) 

            result = {
                "post": post_text,
                "sentiment": sentiment,
                "sentiment_text": sentiment_text,
                "comment": comment,
                "explanation": explanation,
                "full_reasoning": full_reasoning,
                "analysis_type": analysis_type,  
                "emotion_data": scores
            }
    return render_template("index.html", result=result, analysis_type=analysis_type)