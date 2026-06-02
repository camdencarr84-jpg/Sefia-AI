# Sefia-AI
A MIT licensed personal AI agent that hooks Ollama to use *local* and *cloud* models to run. 

**What is it**
Sefia is an AI agent inspired by a certain city (https://thebrokenrealm.net) in a *certain* book. 
The software is MIT licensed, meaning, any content Sefia generates is yours to keep **even for commercial use** 

**How to use**
first, download the *main.py* file and run it in a python interpreter. You will be prompted to enter your choice: Local or Cloud. local will download your selected model out of a list of twenty (commits welcome for  all willing to expand this!)
Cloud will run cogito-2.1:671b-cloud by default, line 21.    subprocess.run(["ollama", "run", "cogito-2.1:671b-cloud"]) to run any other model.
Note:
you must be signed in to use Cloud use (ollama.com) to sign in/up *its free* 

Final note:
This is in active devolopment please feel free to contribute to v.1.1 (the GUI update!) As Sefia is currently a command-line interface.

-Cam

