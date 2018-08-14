import server_helpers
import techniques
import os

#korra 22ra el server.in mn hena w 5od el line el commented w eb3t el port number

in_portNumber = 0
in_seedValue = 0
in_windowSize = 0
in_probability = 0.0

def readInputFile():
    global in_portNumber, in_seedValue, in_windowSize, in_probability
    inputFile = input("Enter input file name: ")
    if os.path.isfile(inputFile):
        print("File found.")
        with open (inputFile) as f:
            content = f.readlines()
            content = [x.strip() for x in content]
            in_portNumber = int(content[0])
            in_windowSize = int(content[1])
            in_seedValue = int(content[2])
            in_probability = float(content [3])
    else:
        print("File not found")
        raise OSError

serverSocket = server_helpers.init_server()
#serverSocket = server_helpers.init_server(port)

def Main():
    global in_seedValue, in_probability
    while True:
        choice=int(input("Please select a technique:\n"
                     "1-GBN\n"
                     "2-Selecticlive Reapeat\n"
                     "3-stop & wait\n"))
        if choice == 1:
            #w hena eb3t f talet variable el seedvalue w f rabe3 wa7ed el prob
            techniques.s_GBN(serverSocket, in_seedValue, in_probability) # seedvalue and prob
        elif choice == 2 :
            #your code goes here ya sa7by sheel pass deh w 7ot function ttnada mn techniques
            print(serverSocket)
            techniques.s_SR(serverSocket, in_windowSize, in_seedValue, in_probability)
        elif choice == 3:
            techniques.s_stopandwait(serverSocket, in_seedValue, in_probability) # seedvalue and prob


if __name__ == "__main__":
    try:
        readInputFile()

    except OSError:
        exit(-1)

    Main()