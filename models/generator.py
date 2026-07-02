from transformers import pipeline

_generator = None

def get_generator():
    global _generator

    if _generator is None:
        _generator = pipeline(
            "text2text-generation",
            model="google/flan-t5-large"
        )

    return _generator