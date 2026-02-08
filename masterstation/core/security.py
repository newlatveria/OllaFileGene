from config import DANGEROUS_TOKENS

def is_safe(code: str) -> bool:
    return not any(token in code for token in DANGEROUS_TOKENS)
