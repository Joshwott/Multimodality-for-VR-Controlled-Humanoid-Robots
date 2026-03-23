# Main file responsible for initiating all the code.

from MetaQuest import vrtracking

#from NAORobot import naocamera, naocontrols, naotest

# Main method starts the Meta Quest 2 and NAO robot links
def main():
    vrtracking.startServer()

if __name__ == "__main__":
    main()