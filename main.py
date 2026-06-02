#Source
import subprocess
import sys
import time

# Importing Ollama here... (ollama.ai)
try:
    import ollama
except Exception as e:
    print(
        "Ollama Python library not installed. Please run 'pip install ollama' and rerun this script."
    )
    time.sleep(4)
    sys.exit(1)

print("Choose one:\n 1. Cloud \n 2. Local")
oc = input(": ").strip()

if oc == "1":
    try:
        print("\nConnecting to cloud model...")
        subprocess.run(["ollama", "run", "cogito-2.1:671b-cloud"])
    except FileNotFoundError:
        print(
            "\nError: Ollama CLI is not installed on this system. Please download it from ollama.ai."
        )

elif oc == "2":
    print(
        "\nChoose a model to download (each B requires roughly 1 GB of VRAM/RAM): \n"
    )

    # Fully audited, official Ollama registry strings (Guaranteed to pull locally)
    models = [
        # --- General Purpose All-Rounders ---
        "llama3.3",  # Meta's 70B frontier leader (defaults to 70b)
        "llama3.1:8b",  # Highly versatile general-purpose 8B model
        "llama3.2",  # Meta's lightweight 3B general assistant
        "qwen3:32b",  # Top-tier balanced 32B all-rounder
        "qwen3:14b",  # Highly efficient mid-range multilingual model
        "qwen3:8b",  # Compact 8B general assistant
        "mistral",  # The classic fast, lightweight standard 7B
        # --- Reasoning / Chain-of-Thought ---
        "deepseek-r1:70b",  # Heavy-duty high-tier local reasoning
        "deepseek-r1:32b",  # Advanced math, logic, and deep thinking
        "deepseek-r1:14b",  # Mid-range step-by-step reasoning engine
        "deepseek-r1:8b",  # Popular lightweight reasoning engine
        "phi4",  # Microsoft's 14B high-logic model (FIXED)
        "phi4-mini",  # Microsoft's 3.8B compact reasoning model
        # --- Coding Specialists ---
        "qwen2.5-coder:32b",  # Leading local model for full software repos
        "qwen2.5-coder:14b",  # Perfect resource-to-performance ratio for coding
        "qwen2.5-coder:7b",  # Ultra-fast coding assistant for smaller GPUs
        "deepseek-coder-v2:16b",  # Reliable Mixture-of-Experts coding champion
        # --- Multimodal & Lightweight ---
        "llama3.2-vision",  # Meta's accessible local image-analysis model
        "gemma2:9b",  # Google's highly efficient 9B text model
        "gemma2:2b",  # Google's ultra-fast 2B text model
    ]

    # Display the menu
    for index, model in enumerate(models, start=1):
        print(f"[{index}] {model}")

    # Capture the user's choice
    try:
        choice = int(
            input("\nEnter the number of the model you want to download: ")
        )
        if 1 <= choice <= len(models):
            selected_model = models[choice - 1]
            print(f"\nSelected: {selected_model}")
            print(
                f"Downloading/Updating '{selected_model}' via Ollama... Please wait."
            )

            # This will now stream the true download progress seamlessly
            subprocess.run(["ollama", "pull", selected_model], check=True)

            print(f"\nSuccess! {selected_model} is ready to use.")
        else:
            print(
                "Invalid selection. Please run the script again and choose a number from the list."
            )
    except ValueError:
        print("Please enter a valid number.")
    except subprocess.CalledProcessError:
        print(
            "\nError: Failed to download the model. Make sure your Ollama service is running in the background."
        )
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")

else:
    print("Invalid choice. Please select 1 or 2.")
