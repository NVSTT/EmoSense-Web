import json
import re
from servises.chunk import chunk
from model.rubert import get_rubert_pipeline
from model.ollama import OllamaClient


def analyze_sentiment(text: str, choose: bool, ollama_client: OllamaClient = None) -> dict:
    if choose:
        if ollama_client is None:
            raise ValueError("OllamaClient required for LLM mode")
        return analyze_with_ollama(text, ollama_client)
    else:
        return analyze_with_rubert(text)

def analyze_with_rubert(text: str):
    pipe = get_rubert_pipeline()
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    all_scores = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
    total_chunks = 0

    for para in paragraphs:
        if len(para) <= 512:
            chunks_list = [para]
        else:
            chunks_list = chunk.chunk(para)  # ← вызов функции из модуля
        
        for text_chunk in chunks_list:  # ← переименовано
            result = pipe(text_chunk[:512])
            for label_score in result[0]:
                label = label_score['label'].lower()
                if label in all_scores:
                    all_scores[label] += label_score['score']
            total_chunks += 1
    
    if total_chunks > 0:
        all_scores = {k: v / total_chunks for k, v in all_scores.items()}
    
    sentiment = max(all_scores, key=all_scores.get)
    return {"sentiment": sentiment, "scores": all_scores}

def analyze_with_ollama(text:str, ollama_client: OllamaClient) -> dict:
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
                if all(k in parsed for k in ['positive', 'negative', 'neutral']):
                    scores = {
                        'positive': float(parsed['positive']),
                        'negative': float(parsed['negative']),
                        'neutral': float(parsed['neutral'])
                    }
                    total = sum(scores.values())
                    if total > 0:
                        scores = {k: v / total for k, v in scores.items()}
                    sentiment = max(scores, key=scores.get)
            except (json.JSONDecodeError, ValueError, TypeError):
                pass
    return {"sentiment": sentiment, "scores": scores}