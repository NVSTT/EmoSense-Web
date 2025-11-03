from model.ollama import OllamaClient

def resize(post_sentiment: str ,post_text: str, length: str, ollama_client:OllamaClient) -> str:
    
    prompt = f"""Преобразуй текст в тональность {post_sentiment}
    Текст: "{post_text}" 
    Текст на {length} слов.
    Ответ только перефразированный текст."""
    
    resized_text = ollama_client.generate( prompt,max_tokens=1000,temperature=0.3)
    return resized_text or "Не удалось сгенерировать"
 