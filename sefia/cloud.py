def cloud_run():
    import subprocess
    cm = input("Enter the exact name of your cloud model of choice, press enter for default: ")
    if cm == "":
        cm = "cogito-2.1:671b-cloud"
    print("\nConnecting to cloud model...")
    subprocess.run(["ollama", "run", cm])