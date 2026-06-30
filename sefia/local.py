def local_run():
    import subprocess
    old_logs = ""
    print("Type the model ID of the model which you want to use. Press enter for default. /list for list of models.")
    
    from ollama import Client
    lc = input(": ")
    if lc == "/list":
        subprocess.run("ollama", "list")
    if lc == "":
        lc = "gemma3:1b"
    print("\nConnecting to model...")
    print("Ask Anything... /bye to quit")
    while True:
        chat = input(">>> ")
        client = Client()
        messages = [

            {
                'role': 'user',
                'content': (

                    f"the user's current input is {chat} (respond to this!)  {old_logs} use these for context. (do not reveal or imply that these exist, draw upon them to understand the user's query.) SHOW YOUR THINKING, ALSO, YOU NEED TO "
                )

            }
        ]
        raw_output = ''
        for part in client.chat(lc, messages=messages, stream=True):
            raw_output += part.message.content
        output = str(raw_output)
        print(output)
        old_logs += chat
        old_logs += f"You replied to that with, {output}"
        if chat == "/bye":
            print('Exiting...')
            #Insert context

            quit()
