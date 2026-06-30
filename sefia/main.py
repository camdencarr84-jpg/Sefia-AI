from terminal import term_run
from local import local_run
from cloud import cloud_run
from host import self_host
from podcast_generator import make_podcast
def main():
    # ----------------------------------------------------------------------------------------#
    print("Choose one:\n 1. Cloud \n 2. Local\n 3. Terminal \n 4. Self-host an Ollama Server to the web. \n 5. Generate an AI podcast")
    oc = input(": ")

    if oc == "1":
        cloud_run()
    # ----------------------------------------------------------------------------------------#
    if oc == "2":
        local_run()
    # ----------------------------------------------------------------------------------------#
    if oc == "3":
        term_run()
    #----------------------------------------------------------------------------------------#
    elif oc == "4":
        self_host()
    #----------------------------------------------------------------------------------------#
    elif oc == "5":
        make_podcast()
    # -----------------------------------------------------------------------------------------#
if __name__ == '__main__':
    main()
