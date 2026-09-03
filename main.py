# Sefia-AI Chat simple, intuitive CLI 
import getpass
import pathlib
import threading
import os
from openai import OpenAI
class ChatConfiguration:
    def providers(prov:str):
        with open("./config/sefia/providers.txt", "a") as provs:
            provs.write(prov)
            
    """
    Anthropic API key setup.
    """
    def anth_setup():
                print("Running setup tool for Anthropic")
                print("Please enter your API key.")
                openai_api_key = getpass.getpass(">")
                with open (pathlib.Path("./config/sefia/anth_api_token", "a")) as openai_api_token:
                    openai_api_token.write(openai_api_key)
                print("Anthropic configured!")
    """
    OpenAI API key setup.
    """
    def openai_setup():
                print("Running setup tool for OpenAI")
                print("Please enter your API key.")
                openai_api_key = getpass.getpass(">")
                with open (pathlib.Path("./config/sefia/chatgpt_api_token", "a")) as openai_api_token:
                    openai_api_token.write(openai_api_key)
                print("ChatGPT configured!")
                providers("ChatGPT")
    """
    OpenAI Compatible Setup
    this is more tricky, as a few more params need to be configured. 
    """
    def openai_compatible_setup():
                print("Running setup tool for Open AI Compatible API")
                print("What is the name of the provider?")
                name = input("> ")
                if name.lower() == "ollama":
                    url = "http://localhost:11434"
                if name.lower() == "lm studio":
                    url = "http://localhost:7394"
                print(f"Is the server at: {url}? If not, please reply no. ")
                ans = input("Y/N")
                if ans.lower() == "y":
                    pass
                    
                print("Please enter your API key (or blank if no auth).")
                
                openai_api_key = getpass.getpass(">")
                with open (pathlib.Path(f"./config/sefia/{provider}_api_token", "a")) as openai_api_token:
                    openai_api_token.write(openai_api_key)
                with open (pathlib.Path(f"./config/sefia/{provider}_url_token", "a")) as openai_api_token:
                    openai_api_token.write(url)
                print(f"{provider} configured!")
                providers(name)
    def list_providers():
        with open("./config/sefia/providers.txt") as providers:
            pr = providers.read()
            print(f"Available providers:\n {pr} ")
class OpenAIChat:
    def message(content, model):
            response = client.responses.create(

            model= model,
            input=[
            {
                "role": "user",
                "content": [
                        {"type": "input_text", "text": content},
                    ],
            }
        ],
    )