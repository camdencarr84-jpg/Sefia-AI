import subprocess
import re
import time
from ollama import Client



def term_run():
    #Variables, replace the YOUR_X_HERE with your actual X, Y
    user_os = "YOUR_OS_HERE"

    password = "YOUR_PASSWORD_HERE"
    failed = ""
    attempts = 0


    cont = input("Continue? [Y/n] ").lower()
    if cont == "y" or cont == "":
        print("Connecting to terminal...")
        cmd = input(" What do you want Sefia Terminal to complete?\n >>> ")
    else:
        print("Exiting the program...")
        time.sleep(.5)
        exit()
    




    prompt_text = (
        f"What {user_os} terminal command would accomplish this task: {cmd}? "
        "Do not include any thinking process, internal reasoning, or <think> tags. "
        f"Provide only the raw executable command as plain text with no markdown formatting. these commands were flagged as dangerous when you tried before: {failed} DO NOT USE THESE AGIAN!"
    )
    command = ["ollama", "run", "gpt-oss:20b-cloud", "--hidethinking", prompt_text]
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
                    "SAFE: sudo, apt, install, vim, apt install python3-full, ls, cat, file, mkdir dir, cd, dir, systemctl status, pip, dpkg, .sh, ./, curl, ls, python3, pip3 \n"
                    "UNSAFE: rm -rf /, dd, mkfs, format, chmod 777, visudo, >>/dev/sda, dd \n"
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
            print("\033[1;31m[GUARDRAIL BLOCKED]\033[0m Retrying with new command...")
            failed.append(suggested_command)
            if attempts == 10:
                print("Maximum attempts reached, exiting the program...")
                quit()
            else:
                attempts += 1
                user_os = "YOUR_OS_HERE"

                password = "YOUR_PASSWORD_HERE"

                prompt_text = (
                    f"What {user_os} terminal command wou5842ld accomplish this task: {cmd}? "
                    "Do not include any thinking process, internal reasoning, or <think> tags. "
                    f"Provide only the raw executable command as plain text with no markdown formatting. these commands were flagged as dangerous when you tried before: {failed} DO NOT USE THESE AGIAN!"
                )
                command = ["ollama", "run", "deepseek-v4-pro", "--hidethinking", prompt_text]
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
                                "SAFE: sudo, apt, install, vim, apt install python3-full, ls, cat, file, mkdir dir, cd, dir, systemctl status, pip, dpkg, .sh, ./, curl, ls, python3, pip3 \n"
                                "UNSAFE: rm -rf /, dd, mkfs, format, chmod 777, visudo, >>/dev/sda, dd \n"
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
                    print("\033[1;31m[GUARDRAIL BLOCKED]\033[0m Retrying with new command...")
                    failed.append(suggested_command)
                    if attempts == 10:
                        print("Maximum attempts reached, exiting the program...")
                        quit()
                    else:
                        attempts += 1
