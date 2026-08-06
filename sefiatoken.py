def analyze(history: str):
    tokens = 0
    for char in history:
        tokens += .25
    print(f"This session used {tokens} tokens.")
