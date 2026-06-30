
def self_host():
    import time
    print("Starting Ollama server...")
    import subprocess
    subprocess.run(["OLLAMA_HOST=0.0.0.0", "ollama", "serve"])
    print("Navigate to http://YOUR_IP_ADDRESS:11434")
    print("Then in an app like Chatbox point the Ollama server to it.")
    time.sleep(3)
