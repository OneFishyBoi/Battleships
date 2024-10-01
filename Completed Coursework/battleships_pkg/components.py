import random
import json

#crates list of list representing board based on input size
def initialise_board(size=10):
    #creating 2D list based on input size
    board_list = [[None]*size for i in range(size)]
    return board_list

#creates a dictionary representing the battleships based on a file 
def create_battleships(filename="battleships.txt"):
    #defining dictionary
    battleships = dict()

    #setting the lines of the file to a variable
    lines = open(filename, "r").readlines()

    #looping through all ship items
    for line in lines:
        #splitting the current line into name and value
        current_line = line.split(":")
        
        #removing the next line character
        current_line[1] = current_line[1].replace("\n", "")

        #placing into dictionary
        battleships[current_line[0]] = current_line[1]

    return battleships

#places the battle ships on the board using varying methods
def place_battleships(board, ships, placement="simple"):

    if placement == "simple":
        count = 0
        #looping through the ships
        for item in ships:
            #looping through the blocks of the ships
            for j in range(int(ships[item])):
                #placing blocks
                board[count][j] = item
            count+= 1
    
    elif placement == "random":
    
        #looping through items in ships to place each ship
        for ship in ships:
            placed = False

            #looping until current ship is placed
            while not placed:
                #creating a variable to keep track of valid block placements
                blocks_valid = 0

                #deciding if ship will be placed horizontally or vertically
                direction = random.randint(0, 1)

                #horizontal placement
                if direction == 0:
                    #generating x and y placement values
                    y_place = random.randint(0, len(board)-1)
                    x_place = random.randint(0, (len(board)-int(ships[ship])-1))

                    #check if placement hits another ship
                    for i in range(0, int(ships[ship])):
                        #checking if current block placement is valid
                        if board[y_place][x_place + i] == None:
                            #incrementing value if valid
                            blocks_valid += 1

                    #checking if overall ship placement was valid
                    if blocks_valid == int(ships[ship]):
                        placed = True

                        #placing the ship
                        for i in range(0, int(ships[ship])):
                            board[y_place][x_place + i] = ship

                #vertical placement
                else:
                    #repeating everything done in horizontal with slight tweaks for change in direction
                    #generating x and y placement values
                    y_place = random.randint(0, (len(board)-int(ships[ship])-1))
                    x_place = random.randint(0, len(board)-1)

                    #check if placement hits another ship
                    for i in range(0, int(ships[ship])):
                        #checking if current block placement is valid
                        if board[y_place + i][x_place] == None:
                            #incrementing value if valid
                            blocks_valid += 1

                    #checking if overall ship placement was valid
                    if blocks_valid == int(ships[ship]):
                        placed = True
                    
                        #placing the ship
                        for i in range(0, int(ships[ship])):
                            board[y_place + i][x_place] = ship
    
    elif placement == "custom":
        #getting placement data from file
        with open("placement.json", "r") as file:
            place_data = json.load(file)
        
        #declaring lists of placement data
        places_x = [None for i in range(5)]
        places_y = [None for i in range(5)]
        directions = [None for i in range(5)]
        count = 0

        #assiging placement data from file into lists
        for item in place_data:
            places_y[count] = (place_data[item])[0]
            places_x[count] = (place_data[item])[1]
            directions[count] = (place_data[item])[2]
            count += 1

        #converting all values to int values
        for i in range(0, len(places_x)):
            places_y[i] = int(places_y[i])
            places_x[i] = int(places_x[i])

        count = 0

        #looping through placing each ship
        for ship in ships:
            blocks_valid = 0

            #checking which direction the ship is being placed
            #horizontal placement (east)
            if directions[count] == "h":
                #assinging x and y placement values
                y_place = places_y[count]
                x_place = places_x[count]
                board_index = len(board) - 1

                #checking to see if placement is within the board
                if x_place + int(ships[ship]) > board_index and x_place > board_index and y_place > board_index:
                    return "placement not valid, ship hits border"

                #checking if placement hits another ship
                for i in range(0, int(ships[ship])):
                    #checking if current block placement is valid
                    if board[y_place][x_place + i] == None:
                        #incrementing value if valid
                        blocks_valid += 1

                #checking if overall ship placement was valid
                if blocks_valid == int(ships[ship]):
                    #placing the ship
                    for i in range(0, int(ships[ship])):
                        board[y_place][x_place + i] = ship
                    count+=1
                else:
                    return "placement not valid, ship hits other ship"
            
            #vertical placement (south)
            elif directions[count] == "v":
                #assinging x and y placement values
                y_place = places_y[count]
                x_place = places_x[count]
                board_index = len(board)-1

                #checking to see if placement is within the board
                if y_place + int(ships[ship]) > board_index and x_place > board_index and y_place > board_index:
                    return "placement not valid, ship hits border"

                #checking if placement hits another ship
                for i in range(0, int(ships[ship])):
                    #checking if current block placement is valid
                    if board[y_place + i][x_place] == None:
                        #incrementing value if valid
                        blocks_valid += 1

                #checking if overall ship placement was valid
                if blocks_valid == int(ships[ship]):
                    #placing the ship
                    for i in range(0, int(ships[ship])):
                        board[y_place + i][x_place] = ship
                    count+=1
                else:
                    return "placement not valid, ship hits other ship"
            
    return board

