from transformers import pipeline

_rubert_pipe = None

def get_rubert_pipeline():
    global _rubert_pipe
    if _rubert_pipe is None:
        _rubert_pipe = pipeline(
            "text-classification",
            model="blanchefort/rubert-base-cased-sentiment-rusentiment",
            return_all_scores=True
        )
    return _rubert_pipe