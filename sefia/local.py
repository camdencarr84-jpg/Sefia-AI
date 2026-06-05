def local_run():
    import time
    import subprocess
    print("Type the model ID of the model which you want to use. Each B in the name means it uses that much Vram or Ram in GB. Press enter for default.")
    lc = input("Type Model ID Here: ")
    if lc == "":
        print("Defaulting to Gemma3:1b...")
        time.sleep(.5)
        lc = "gemma3:1b"
    print("Connecting to Ollama...")
    subprocess.run(["ollama", "run", lc])