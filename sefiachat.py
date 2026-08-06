def chat():
    from ollama import Client
    import subprocess
    from sefiatoken import analyze

    old_logs =  ""
    with open ("history.txt", "a") as h:
        old_logs += str(h)
    subprocess.run(["ollama", "list"])

    cm = input("Enter the exact name of your cloud model of choice, press enter for default: ")
    if cm == "":
        cm = "gpt-oss:20b-cloud"
    print("\nConnecting to model...")
    print("Ask Anything... /bye to quit")
    while  1 == 1:
        chat = input(">>> ")
        client = Client()
        messages = [

            {
                'role': 'user',
                'content': (

                    f"The user's current input is {chat}  {old_logs} use these for context."
                )

            }
        ]
        raw_output = ''
        for part in client.chat(cm, messages=messages, stream=True):
            raw_output += part.message.content
        output = str(raw_output)
        print(output)
        old_logs += chat 
        old_logs += f"You replied to that with, {output}"
        if chat == "/bye":
            print('Exiting...')
            with open ("history.txt", "a") as h:
                h.write(old_logs)
            analyze(old_logs)
