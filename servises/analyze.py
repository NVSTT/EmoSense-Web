import json
import re
from transformers import pipeline
from model.ollama import OllamaClient

def analyze_sentiment(text: str, choose: bool, ollama_client: OllamaClient) -> dict:
    if choose:
        prompt = f"""Ты — эксперт по анализу эмоций в текстах, включая поэзию и сложные случаи.
        Проанализируй следующий текст глубоко и подробно.
        Определи вероятности тональностей: positive, negative, neutral (сумма = 1.0).
        Верни ТОЛЬКО JSON объект в формате: {{"positive": 0.XX, "negative": 0.XX, "neutral": 0.XX}}

        Текст: {text}"""

        raw_response = ollama_client.generate(prompt, max_tokens=80, temperature=0.3)
        scores = {"positive": 0.33, "negative": 0.33, "neutral": 0.34}
        sentiment = "neutral"

        if raw_response:
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group())
                    # Убедимся, что все ключи на месте и значения — числа
                    if all(k in parsed for k in ['positive', 'negative', 'neutral']):
                        scores = {
                            'positive': float(parsed['positive']),
                            'negative': float(parsed['negative']),
                            'neutral': float(parsed['neutral'])
                        }
                        # Нормализуем (на случай, если сумма ≠ 1)
                        total = sum(scores.values())
                        if total > 0:
                            scores = {k: v / total for k, v in scores.items()}
                        sentiment = max(scores, key=scores.get)
                except (json.JSONDecodeError, ValueError, TypeError):
                    pass  # оставить fallback

    else:
        try:
            pipe = pipeline(
                "text-classification",
                model="blanchefort/rubert-base-cased-sentiment-rusentiment",
                return_all_scores=True
            )
            results = pipe(text)[0]
            scores = {}
            for res in results:
                label = res['label'].lower()
                if label in ['positive', 'negative', 'neutral']:
                    scores[label] = res['score']
            # Заполняем недостающие классы нулями
            for label in ['positive', 'negative', 'neutral']:
                if label not in scores:
                    scores[label] = 0.0
            sentiment = max(scores, key=scores.get)
        except Exception as e:
            print(f"RuBERT error: {e}")
            scores = {"positive": 0.33, "negative": 0.33, "neutral": 0.34}
            sentiment = "neutral"

    return {"sentiment": sentiment, "scores": scores}


def generate_ai_comment_with_ollama(post_text: str, sentiment: str, ollama_client: OllamaClient) -> str:
    prompt = f"""Ты — дружелюбный бот в соцсети. Напиши короткий, тёплый ответ на пост пользователя.
    Ответ должен быть на том же языке, что и пост.
    (1 предложение, максимум 15 слов. Не упоминай тональность.)

    Пост: "{post_text}" """
    
    raw_comment = ollama_client.generate(prompt, max_tokens=50, temperature=0.8)
    comment = raw_comment
    return comment or "🤖 ИИ временно недоступен."

def generate_sentiment_explanation(post_text: str, sentiment: str, ollama_client: OllamaClient) -> str:
    prompt = f"""Отвечай напрямую.
    Объясни кратко (1–2 предложения), почему текст имеет тональность "{sentiment}".
    Ответ должен быть на том же языке, что и текст.

    Текст: "{post_text}" """
    
    raw_explanation = ollama_client.generate(prompt, max_tokens=100, temperature=0.5)
    explanation = raw_explanation
    return explanation or "Не удалось сгенерировать пояснение."

def generate_full_reasoning(post_text: str, scores: dict, ollama_client: OllamaClient) -> str:
    """
    Генерирует подробное рассуждение ИИ: какие эмоции доминируют, почему,
    с анализом ключевых фраз и контекста.
    """
    # Форматируем вероятности для промпта
    prob_str = ", ".join([f"{k}: {v:.1%}" for k, v in scores.items()])
    
    prompt = f"""Ты — эксперт по анализу эмоций в текстах, включая поэзию и сложные случаи.
    Проанализируй следующий текст глубоко и подробно.

    Текст: "{post_text}"

    Результат модели: {prob_str}

    Напиши развёрнутое рассуждение (3–5 предложений не больше):
    - Какие именно слова, образы или фразы определяют эмоциональную окраску?
    - Почему доминирует именно эта тональность?
    - Учти литературный контекст, иронию, сарказм, меланхолию, если они есть.
    - Не повторяй просто вероятности — объясни смысл.

    Ответ должен быть на том же языке, что и текст."""
    
    raw_reasoning = ollama_client.generate(prompt, max_tokens=350, temperature=0.6)
    return raw_reasoning or "Не удалось сгенерировать подробный анализ."