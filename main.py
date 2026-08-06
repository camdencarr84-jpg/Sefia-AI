from sefiaterm import term_run
from sefiachat import chat
from sefiahost import self_host
from sefiapod import make_podcast
from sefiatoken import analyze
import time

# telemetry = ""  
# if telemetry == "":
#     telemetry = input("Allow anyonomous telemetry? Before consenting, please review telemetry.py, it contains all the available data collected (Yes/No)") 
#     if 'y' in telemetry:
#         telemetry = 'on'
#     else:
#         telemetry = 'off'
# ANSI Escape Codes for Colors
GREEN = "\033[1;32m"
RESET = "\033[0m"
RED = "\033[1;31m"


def print_octopus():
    print(GREEN + r"""
          _[_[ [ [ [_
         /-----------\
        /-------------\
       /| {}    {}    | \
     / /|             | \ \
    / / | #  (<>)  #  |  \ \               WELCOME TO SEFIA
   ( )  |             |   ( )             2.4 * Bug fixes
           | | | | | |
          ()()()()()()
""" + RESET)
if telemetry == 'on':
    from telemetry import collect_telemetry
    collect_telemetry() 
def main():
    print_octopus()

    while True:
        # ----------------------------------------------------------------------------------------#
        print("Choose one:\n 1. Chat \n 3. Terminal \n 4. Self-host an Ollama Server to the web. \n 5. Generate an AI podcast\n 6. Exit the program. ")
        oc = input(": ")

        if oc == "1":
            chat()
        # ----------------------------------------------------------------------------------------#
        if oc == "3":
            term_run()
        #---------------------------------------------------------------------------------------#
        elif oc == "4":
            self_host()
        #----------------------------------------------------------------------------------------#
        elif oc == "5":
            make_podcast()
      
        # -----------------------------------------------------------------------------------------#
        elif oc == "6":
            print("Exiting! Have a nice day!")
            time.sleep(2)
            exit()
        elif oc == "Credits":
            return "Sefia is a CD Carr project, find his work at: https://github.com/camdencarr84-jpg"


if __name__ == '__main__':
    main()
