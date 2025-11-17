from flask import Blueprint, render_template, request, flash, get_flashed_messages, jsonify, redirect, url_for
from flask_jwt_extended import jwt_required
from model.ollama import OllamaClient, DEFAULT_OLLAMA_HOST, DEFAULT_OLLAMA_MODEL
from servises.analyze import analyze_sentiment
from servises.generate import generate_full_reasoning, generate_ai_comment_with_ollama, generate_sentiment_explanation
from servises.resize import resize
from schema.db_main import User
import bleach
import os

bp = Blueprint('main', __name__)
ollama = OllamaClient(DEFAULT_OLLAMA_HOST, DEFAULT_OLLAMA_MODEL)

@bp.route("/", methods=["GET", "POST"])
def index():
    # Перенаправляем на dashboard
    return redirect(url_for('main.dashboard'))
    result = None
    analysis_type = "objective"
    if request.method == "POST":
        post_text = request.form.get("post", "").strip()
        analysis_type = request.form.get("analysis_type", "objective")
        use_llm = (analysis_type == "subjective")

        if not post_text:
            flash("Пожалуйста, введите текст для анализа.", "error")
        elif len(post_text) > 1000:
            flash("Текст слишком длинный. Максимум 1000 символов.", "error")
        else:
            post_text = bleach.clean(post_text, tags=[], attributes={}, strip=True)
            post_text = ' '.join(post_text.split())

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

                comment = generate_ai_comment_with_ollama(post_text, ollama)
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

                resize_sentiment = request.form.get("resize_sentiment")
                resize_length = request.form.get("resize_length")
                if resize_sentiment and resize_length:
                    try:
                        length_int = int(resize_length)
                        if 1 <= length_int <= 100:
                            resized_text = resize(resize_sentiment, post_text, str(length_int), ollama)
                            result["resized_text"] = resized_text
                        else:
                            flash("Длина должна быть от 1 до 100 слов.", "error")
                    except ValueError:
                        flash("Неверная длина.", "error")

    return render_template("index.html", result=result, analysis_type=analysis_type, messages=get_flashed_messages(with_categories=True), current_user=current_user)

@bp.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    # Проверяем авторизацию
    from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        current_user = User.query.get(int(current_user_id)) if current_user_id else None
        is_authenticated = current_user is not None
    except:
        current_user = None
        is_authenticated = False

    # Основная логика анализа текста
    result = None
    analysis_type = "objective"
    if request.method == "POST":
        post_text = request.form.get("post", "").strip()

        # Функционал загрузки файлов только для авторизованных пользователей
        if is_authenticated:
            file = request.files.get("file")

            # Если загружен файл, читаем текст из него
            if file and file.filename:
                if not file.filename.endswith('.txt'):
                    flash("Пожалуйста, загрузите файл в формате .txt.", "error")
                elif file.content_length and file.content_length > 1024 * 1024:  # 1MB limit
                    flash("Файл слишком большой. Максимальный размер 1MB.", "error")
                else:
                    try:
                        post_text = file.read().decode('utf-8').strip()
                    except UnicodeDecodeError:
                        flash("Ошибка чтения файла. Убедитесь, что файл в кодировке UTF-8.", "error")
                        post_text = ""

        analysis_type = request.form.get("analysis_type", "objective")
        use_llm = (analysis_type == "subjective")

        if not post_text:
            flash("Пожалуйста, введите текст для анализа.", "error")
        elif len(post_text) > 1000:
            flash("Текст слишком длинный. Максимум 1000 символов.", "error")
        else:
            post_text = bleach.clean(post_text, tags=[], attributes={}, strip=True)
            post_text = ' '.join(post_text.split())

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

                # Расширенный функционал только для авторизованных пользователей
                if is_authenticated:
                    comment = generate_ai_comment_with_ollama(post_text, ollama)
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

                    resize_sentiment = request.form.get("resize_sentiment")
                    resize_length = request.form.get("resize_length")
                    if resize_sentiment and resize_length:
                        try:
                            length_int = int(resize_length)
                            if 1 <= length_int <= 100:
                                resized_text = resize(resize_sentiment, post_text, str(length_int), ollama)
                                result["resized_text"] = resized_text
                            else:
                                flash("Длина должна быть от 1 до 100 слов.", "error")
                        except ValueError:
                            flash("Неверная длина.", "error")
                else:
                    # Ограниченный функционал для неавторизованных пользователей
                    result = {
                        "post": post_text,
                        "sentiment": sentiment,
                        "sentiment_text": sentiment_text,
                        "analysis_type": analysis_type,
                        "emotion_data": scores
                    }

    return render_template("index.html", result=result, analysis_type=analysis_type, messages=get_flashed_messages(with_categories=True), current_user=current_user)

@bp.route("/login")
def login():
   return render_template("login.html")

@bp.route("/register")
def register():
   return render_template("register.html")