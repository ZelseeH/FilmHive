import backend.app.skrypt_nltk as skrypt_nltk
from nltk.tokenize import word_tokenize

# Test tokenizacji po polsku
text = "To jest test rekomendacji filmów po polsku."
try:
    tokens = word_tokenize(text, language="polish")
    print(
        "Tokeny:", tokens
    )  # Oczekiwany output: ['To', 'jest', 'test', 'rekomendacji', 'filmów', 'po', 'polsku', '.']
    print("Sukces: Polski jest wspierany!")
except Exception as e:
    print("Błąd:", str(e))
    import traceback

    traceback.print_exc()  # Pełny stack trace dla debugu
