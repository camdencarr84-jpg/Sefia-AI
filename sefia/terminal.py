import subprocess
import re
import time
from ollama import Client
def term_run():
    password = "5842"
    print(
        "WARNING! This feature is experimental and could permanently damage your OS, if in doubt use a virtual machine.")
    time.sleep(4)
    cont = input("Continue? [Y/n] ").lower()
    if cont == "y" or cont == "":
        print("Connecting to terminal...")
        user_os = input("What is your operating system, EG Linux Mint or Ubuntu? ")
        cmd = input(" What do you want Sefia Terminal to complete?\n >> ")
        prompt_text = (
            f"What {user_os} terminal command would accomplish this task: {cmd}? "
            "Do not include any thinking process, internal reasoning, or <think> tags. "
            "Provide only the raw executable command as plain text with no markdown formatting."
        )
        command = ["ollama", "run", "cogito-2.1:671b-cloud", "--hidethinking", prompt_text]
        result = subprocess.run(command, capture_output=True, text=True)
        raw_output = result.stdout
        clean_output = re.sub(r'<think>.*?</think>', '', raw_output, flags=re.DOTALL)
        suggested_command = clean_output.replace("```bash", "").replace("```", "").strip()

        # Pre-check for obviously dangerous patterns
        dangerous_patterns = [
            r'rm\s+-rf\s+/',
            r'dd\s+if=',
            r'mkfs\.',
            r'format\s+',
            r'fdisk',
            r'parted',
            r'>\s*/dev/(sda|sdb|vda|vdb)',
            r'chmod\s+777',
            r'visudo',
        ]

        is_obviously_dangerous = any(re.search(pattern, suggested_command) for pattern in dangerous_patterns)

        if is_obviously_dangerous:
            verdict = "no"
        else:
            client = Client()
            messages = [

                {
                    'role': 'user',
                    'content': (
                        "You are a command safety checker. Reply with ONLY 'yes' or 'no', nothing else.\n"
                        "SAFE: sudo, apt, install, vim, apt install python3-full, ls, cat, file, mkdir dir, cd dir, systemctl status, pip\n"
                        "UNSAFE: rm -rf /, dd, mkfs, format, chmod 777, visudo, >>/dev/sda\n"
                        f"Check this command:\n{suggested_command}"
                    )
                }
            ]
            guardrail_response = ""
            for part in client.chat('gpt-oss:20b-cloud', messages=messages, stream=True):
                guardrail_response += part.message.content
            verdict = guardrail_response.strip().lower()

        if "yes" in verdict:
            print("\033[1;32m[GUARDRAIL PASSED]\033[0m Command verified as safe.")
            print(f"Executing: {suggested_command}\n")
            if "sudo" in suggested_command:
                full_sudo_command = f"echo '{password}' | sudo -S {suggested_command}"
                subprocess.run(full_sudo_command, shell=True)
            else:
                subprocess.run(suggested_command, shell=True)
        else:
            print("\033[1;31m[GUARDRAIL BLOCKED]\033[0m Execution canceled. This command was flagged as dangerous.")
    else:
        print("Exiting the program...")
        time.sleep(.5)
        exit()
