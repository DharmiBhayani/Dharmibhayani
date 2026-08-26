
def count_tokens(text):
    """Fallback token estimate when the provider does not return usage.

    Provider-reported tokens are preferred. This is only an estimate:
    approximately 1 token per 4 characters.
    """
    if not text:
        return 0
    return max(1, len(text) // 4)
