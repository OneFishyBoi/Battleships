#changes format from python to json
import json
#modeles to host and manage local server
from flask import Flask, render_template, request, jsonify, redirect, url_for
#module for generating random number
from random import randint
#contains module to help board setup
import components

#creating flask app
app = Flask(__name__)

#global boards
ai_board = list()
board = [[None for i in range(10)] for j in range(10)]

#global list of coordinates that the player has attacked and hit a ship
prev_hit = list()

#global variables for targeting system
last_hit = [False, None]
SINK_MISSION = False
HIT_CENTER = None
available_directions = ["up", "down", "left", "right"]
ai_prev_attacked = list()
HIT_STREAK = 0
potential_centers = list()
AI_SUNK = False
LAST_SHIP_HIT = None

#length coordinate maps
two_map = list()
three_map = list()
four_map = list()
five_map = list()

#global DIFFICULTY tracker
DIFFICULTY = None

#global ships dictionarys
ships = {"Aircraft_Carrier":5,
        "Battleship":4,
        "Cruiser":3,
        "Submarine":3,
        "Destroyer":2}

ai_ships = {"Aircraft_Carrier":5,
        "Battleship":4,
        "Cruiser":3,
        "Submarine":3,
        "Destroyer":2}

@app.route("/", methods=["GET"])
def root():
#creates a random board for the ai and renders the main page for play
    global ai_board

    if DIFFICULTY == "Hard":
        create_maps()

    #creating ai board with random placement
    ai_board = components.place_battleships([[None for i in range(10)] for j in range(10)], ships, "random")
    return render_template("main.html", player_board=board)

@app.route("/select", methods=["GET", "POST"])
def difficulty_select():
#DIFFICULTY select screen
    global DIFFICULTY

    if request.method == "GET":
        return render_template("difficulty.html")

    if request.method == "POST":
        DIFFICULTY = request.form["difficulty"]
        return redirect(url_for("placement_interface"))

@app.route("/attack", methods=["GET"])
def attack():
#processes attacks and current game stage
    global last_hit, AI_SUNK, prev_hit, ai_prev_attacked
    
    if request.args:
        x = int(request.args.get("x"))
        y = int(request.args.get("y"))
        attack_hit = False

        #checking if attack hit
        if ai_board[y][x] is not None:
            attack_hit = True
            prev_hit.append([x,y])

        #checking if the player has already destroyed a ship on that square
        #stops a bug where attacking a red square(previously hit ship)
        #turns it blue(not previously hit)
        if [x,y] in prev_hit:
            attack_hit = True

        #checking if the player will sink a ship
        player_sunk = False
        if attack_hit:
            player_sunk = player_ship_sunk(x, y)

        #processing attack on ai board
        ai_board[y][x] = None

        #generating ai move
        coord = generate_ai_attack()

        #checking if the ai attack will hit a ship
        if board[coord[1]][coord[0]] is not None:
            last_hit = [True, coord]
            #decrementing ship dictionary of player
            ai_ship_sunk(coord[0], coord[1])
        else:
            last_hit = [False, coord]
            AI_SUNK = False

        ai_prev_attacked.append(coord)

        #processing attack on player board
        board[coord[1]][coord[0]] = None

        #checking if the game is finished
        outcome = is_finish()

        #returning values
        #checking if a ship has been sunk
        if player_sunk:
            try:
                #checking if game has ended
                if outcome[0]:
                    return jsonify({"hit":attack_hit, "AI_Turn":coord,
                                "sunk":player_sunk, "finished":outcome[1]})
            except:
                return jsonify({"hit":attack_hit, "AI_Turn":coord, "sunk":player_sunk})
        else:
            try:
                if outcome[0]:
                    return jsonify({"hit":attack_hit, "AI_Turn":coord, "finished":outcome[1]})
            except:
                return jsonify({"hit":attack_hit, "AI_Turn":coord})

@app.route("/placement", methods=["GET", "POST"])
def placement_interface():
#allows user to place ships and send back placed board
    board_size = 10

    if request.method == "GET":
        #rendering the placement template given using the ship dictionary and board size
        return render_template("placement.html", ships=ships, board_size=board_size)

    #checking if the user has submit
    if request.method == 'POST':
        #getting the data the user submitf
        data = request.get_json()

        place_input(data)

        #returning message after button is pressed to trigger redirect
        return jsonify({"yippee":"message recieved"}), 200

def place_input(data):
#procedure which takes placement data and edits global player board
    #declaring lists of placement data
    places_x = [None for i in range(5)]
    places_y = [None for i in range(5)]
    directions = [None for i in range(5)]
    count = 0

    #assiging placement data from file into lists
    for item in data:
        places_x[count] = (data[item])[0]
        places_y[count] = (data[item])[1]
        directions[count] = (data[item])[2]
        count += 1

    #converting all values to int values
    for i in range(0, len(places_x)):
        places_y[i] = int(places_y[i])
        places_x[i] = int(places_x[i])

    ship_count = 0

    #looping through placing each ship
    for ship in ships:
        #checking which direction the ship is being placed
        #horizontal placement (east)
        if directions[ship_count] == "h":
            #placing the ship
            for i in range(ships[ship]):
                board[places_y[ship_count]][places_x[ship_count]+i] = ship

            ship_count+=1

        #vertical placement (south)
        elif directions[ship_count] == "v":
            #placing the ship
            for i in range(ships[ship]):
                board[places_y[ship_count]+i][places_x[ship_count]] = ship

            ship_count+=1

def generate_ai_attack():
#function to create AI attack
    global SINK_MISSION, HIT_CENTER, HIT_STREAK, AI_SUNK

    #random attacks (easy mode)
    if DIFFICULTY == "Easy":
        return random_move()
    #all other difficulties (they all use the same targeting system)
    else:
        if DIFFICULTY == "Hard":
            create_maps()

        #removing potential center if last ship was sunk
        if AI_SUNK:
            reset_targeting()
            potential_centers.pop(0)

        #resetting AI_SUNK when there is not more potential centers
        if len(potential_centers) == 0:
            AI_SUNK = False

        #checking if the last shot hit and if hit was part of a sink mission
        if (last_hit[0] and not SINK_MISSION) or (len(potential_centers) != 0 and AI_SUNK):
            SINK_MISSION = True
            HIT_STREAK+=1

        #targeting the rest of a hit ship
        if SINK_MISSION:
            #checking if there is already a hit center
            if HIT_CENTER is None:
                if len(potential_centers)>0 and AI_SUNK:
                    HIT_CENTER = potential_centers[0]
                    AI_SUNK = False
                else:
                    #assigning hit center
                    HIT_CENTER = last_hit[1]

                #calculating available directions
                #checking if square on edge of board
                #hit left or right
                if HIT_CENTER[0] == 0:
                    available_directions.remove("left")
                elif HIT_CENTER[0] == len(board)-1:
                    available_directions.remove("right")
                #hit top or bottom
                if HIT_CENTER[1] == 0:
                    available_directions.remove("up")
                elif HIT_CENTER[1] == len(board)-1:
                    available_directions.remove("down")

                #checking if square adjacent to previously hit square
                #up
                if (HIT_CENTER[0], HIT_CENTER[1]-1) in ai_prev_attacked:
                    available_directions.remove("up")
                #down
                if (HIT_CENTER[0], HIT_CENTER[1]+1) in ai_prev_attacked:
                    available_directions.remove("down")
                #left
                if (HIT_CENTER[0]-1, HIT_CENTER[1]) in ai_prev_attacked:
                    available_directions.remove("left")
                #right
                if (HIT_CENTER[0]+1, HIT_CENTER[1]) in ai_prev_attacked:
                    available_directions.remove("right")

                #checking if there are any directions left
                if len(available_directions) == 0:
                    reset_targeting()
                    return difficulty_move()

                #attack closest available direction
                return closest_available_output()
            else:
                #check if last move after finding center hit
                if not last_hit[0]:
                    #remove last used direction
                    del available_directions[0]
                    HIT_STREAK = 1

                    #return a random move if there is no more directions
                    if len(available_directions) == 0:
                        reset_targeting()
                        return difficulty_move()

                    return closest_available_output()
                elif last_hit[0]:
                    #incrementing hit streak
                    HIT_STREAK+=1

                    if len(available_directions) == 0:
                        reset_targeting()
                        return difficulty_move()

                    #checking if next square in same direction can be hit
                    #checking if next square is over the edge of the board
                    if available_directions[0] == "up":
                        if HIT_CENTER[1]-HIT_STREAK < 0:
                            del available_directions[0]
                            HIT_STREAK = 1
                    elif available_directions[0] == "down":
                        if HIT_CENTER[1]+HIT_STREAK > len(board)-1:
                            del available_directions[0]
                            HIT_STREAK = 1
                    elif available_directions[0] == "left":
                        if HIT_CENTER[0]-HIT_STREAK < 0:
                            del available_directions[0]
                            HIT_STREAK = 1
                    elif available_directions[0] == "right":
                        if HIT_CENTER[0]+HIT_STREAK > len(board)-1:
                            del available_directions[0]
                            HIT_STREAK = 1

                    #checking if available directions is empty
                    if len(available_directions) == 0:
                        reset_targeting()
                        return difficulty_move()

                    #checking if next square has already been hit
                    if available_directions[0] == "up":
                        if (HIT_CENTER[0], HIT_CENTER[1]-HIT_STREAK) in ai_prev_attacked:
                            del available_directions[0]
                            HIT_STREAK = 1
                    elif available_directions[0] == "down":
                        if (HIT_CENTER[0], HIT_CENTER[1]+HIT_STREAK) in ai_prev_attacked:
                            del available_directions[0]
                            HIT_STREAK = 1
                    elif available_directions[0] == "left":
                        if (HIT_CENTER[0]-HIT_STREAK, HIT_CENTER[1]) in ai_prev_attacked:
                            del available_directions[0]
                            HIT_STREAK = 1
                    elif available_directions[0] == "right":
                        if (HIT_CENTER[0]+HIT_STREAK, HIT_CENTER[1]) in ai_prev_attacked:
                            del available_directions[0]
                            HIT_STREAK = 1

                    #checking if available directions is empty
                    if len(available_directions) == 0:
                        reset_targeting()
                        return difficulty_move()

                    return closest_available_output()
        else:
            return difficulty_move()

def is_finish():
#checks if the game is finished and returns a message relating to the winner
    player_win = True
    ai_win = True

    #looping through each row of the board
    for y in range(0, len(board)):
        #looping through each collumn of the boards
        for x in range(0, len(board)):
            #checking the see if currect square is empty
            if board[y][x] is not None:
                ai_win = False
            elif ai_board[y][x] is not None:
                player_win = False

    #returning result based on values
    if player_win is True and ai_win is True:
        return(True, "Draw")
    elif player_win is True:
        return(True, "You win! 🤑🤑🤑")
    elif ai_win is True:
        return(True, "You lose! 🤡🤡🤡")

    return False

def player_ship_sunk(x, y):
#function to check if the player sunk a ship
    #getting ship that is being attacked
    ship = ai_board[y][x]

    #decrementing ships dictionary
    ai_ships[ship]-=1

    if ship is not None:
        #check if current ship is sunk
        if ai_ships[ship] == 0:
            return True
        else:
            return False
    else:
        return False

def ai_ship_sunk(x, y):
#function to check if ai sunk a ship and update variables for targeting system
    global AI_SUNK, LAST_SHIP_HIT, HIT_STREAK
    #getting ship that is being attacked
    ship = board[y][x]

    #dicitonary containing all ships max lengths
    max_ships = {"Aircraft_Carrier":5,
        "Battleship":4,
        "Cruiser":3,
        "Submarine":3,
        "Destroyer":2}

    #checking if this ship has been hit before
    if ships[ship] == max_ships[ship]:
        potential_centers.append((x,y))
        #once new pot center is added, direction is change and hit streak is reset
        if SINK_MISSION:
            available_directions.remove(available_directions[0])
            HIT_STREAK = 0

    #decrementing ships dictionary
    ships[ship]-=1

    #checking if ai sunk ship on last attack
    if ships[ship] == 0:
        AI_SUNK = True

    LAST_SHIP_HIT = ship

    if ship is not None:
        #check if current ship is sunk
        if ai_ships[ship] == 0:
            return True
        else:
            return False
    else:
        return False

def random_move():
#function to create a random move based on the board size
    #giving a random move as not currently targeting
    need_move = True
    while need_move:
        #generate a tuple between 0 and the size of the board
        coord = (randint(0, len(board)-1),randint(0, len(board)-1))

        #check if coordinate generated has already been attacked
        if coord not in ai_prev_attacked:
            need_move = False
            ai_prev_attacked.append(coord)

    return coord

def closest_available_output():
#generates the attack for the targeting system based on the available directions
    #attack closest available direction
    if available_directions[0] == "up":
        return (HIT_CENTER[0], HIT_CENTER[1]-HIT_STREAK)
    elif available_directions[0] == "down":
        return (HIT_CENTER[0], HIT_CENTER[1]+HIT_STREAK)
    elif available_directions[0] == "left":
        return (HIT_CENTER[0]-HIT_STREAK, HIT_CENTER[1])
    elif available_directions[0] == "right":
        return (HIT_CENTER[0]+HIT_STREAK, HIT_CENTER[1])

def hard_move():
#return a random move from a hit map based on what length of ship is left
    global ai_prev_attacked

    #check if each ships is still alive, finding smallest ships length based on which are
    if ships["Destroyer"] != 0:
        min_ship_len = 2
    elif ships["Submarine"] != 0 or ships["Cruiser"] != 0:
        min_ship_len = 3
    elif ships["Battleship"] != 0:
        min_ship_len = 4
    else:
        min_ship_len = 5

    if min_ship_len == 2:
        #giving a random move as not currently targeting
        need_move = True
        while need_move:
            #generate a tuple between 0 and the size of the board
            coord = two_map[randint(0, len(two_map)-1)]

            #check if coordinate generated has already been attacked
            if coord not in ai_prev_attacked:
                need_move = False
                ai_prev_attacked.append(coord)

    if min_ship_len == 3:
        #giving a random move as not currently targeting
        need_move = True
        while need_move:
            #generate a tuple between 0 and the size of the board
            coord = three_map[randint(0, len(three_map)-1)]

            #check if coordinate generated has already been attacked
            if coord not in ai_prev_attacked:
                need_move = False
                ai_prev_attacked.append(coord)

    if min_ship_len == 4:
        #giving a random move as not currently targeting
        need_move = True
        while need_move:
            #generate a tuple between 0 and the size of the board
            coord = four_map[randint(0, len(four_map)-1)]

            #check if coordinate generated has already been attacked
            if coord not in ai_prev_attacked:
                need_move = False
                ai_prev_attacked.append(coord)

    if min_ship_len == 5:
        #giving a random move as not currently targeting
        need_move = True
        while need_move:
            #generate a tuple between 0 and the size of the board
            coord = five_map[randint(0, len(five_map)-1)]

            #check if coordinate generated has already been attacked
            if coord not in ai_prev_attacked:
                need_move = False
                ai_prev_attacked.append(coord)

    return coord

def reset_targeting():
#procedure to reset global variables of targeting system
    global last_hit, SINK_MISSION, HIT_CENTER, available_directions, HIT_STREAK

    if len(potential_centers) == 1:
        last_hit = [False, None]
        SINK_MISSION = False
        HIT_CENTER = None
        available_directions = ["up", "down", "left", "right"]
        HIT_STREAK = 0
    else:
        last_hit = [True, None]
        SINK_MISSION = True
        HIT_CENTER = None
        available_directions = ["up", "down", "left", "right"]
        HIT_STREAK = 0

def create_maps():
#creating coord maps for hard DIFFICULTY
    global two_map, three_map, four_map, five_map
    #two
    for i in range(0, len(board)):
        if i%2 == 0:
            for j in range(0,4):
                two_map.append((i,j*2))
        else:
            for j in range(1, 11, 2):
                two_map.append((i,j))

    #three
    for i in range(0, len(board)):
        if  i%3 == 0:
            for j in range(0,12,3):
                three_map.append((i,j))
        elif i%3 == 1:
            for j in range(1,10,3):
                three_map.append((i,j))
        else:
            for j in range(2, 11, 3):
                three_map.append((i,j))
    
    #four
    for i in range(0, len(board)):
        if i%4 == 0:
            for j in range(0, 12, 4):
                four_map.append((i,j))
        elif i%4 == 1:
            for j in range(1, 13, 4):
                four_map.append((i,j))
        elif i%4 ==2:
            for j in range(2, 10, 4):
                four_map.append((i,j))
        else:
            for j in range(3, 11, 4):
                four_map.append((i,j))

    #five
    for i in range(0, len(board)):
        if i%5 == 0:
            for j in range(0, 10, 5):
                five_map.append((i,j))
        elif i%5 == 1:
            for j in range(1, 11, 5):
                five_map.append((i,j))
        elif i%5 == 2:
            for j in range(2, 12, 5):
                five_map.append((i,j))
        elif i%5 == 3:
            for j in range(3, 13, 5):
                five_map.append((i,j))
        else:
            for j in range(4, 14, 5):
                five_map.append((i,j))

def master_move():
#creates a matrix of all possible positions a ship can be placed; chooses most likely
    #creating a matrix representing the board
    board_matrix = [[0 for i in range(len(board))] for j in range(len(board))]

    perma_ships = {"Aircraft_Carrier":5,
        "Battleship":4,
        "Cruiser":3,
        "Submarine":3,
        "Destroyer":2}

    #dictionary of possible ships
    ships_length = [5, 4, 3, 3, 2]

    #removing all lengths that are no longer in play
    for ship in ships:
        if ships[ship] == 0:
            ships_length.remove(perma_ships[ship])

    #updating matrix to reflect current board position
    #looping through each row
    for row in range(0, len(board)):
        #looping through each collumn:
        for collumn in range(0, len(board)):
            #finding each position ships can be placed on the current square
            #checking if current square has already been shot
            if (collumn, row) not in ai_prev_attacked:
                #horizontal positions
                #looping through each ship
                for length in ships_length:
                    can_place = True

                    #checking if the entire current ship can be placed
                    #have one of the positions already been attacked
                    #looping through each block
                    for block in range(0, length):
                        if (collumn+block, row) in ai_prev_attacked:
                            can_place = False

                    #would the ship go off the edge of the board
                    if collumn+length-1 > len(board)-1:
                        can_place = False

                    #updating matrix values based on if the ship can be placed
                    if can_place:
                        for block in range(0, length):
                            board_matrix[row][collumn+block] += 1

                #vertical positions
                #looping through each ship
                for length in ships_length:
                    can_place = True

                    #checking if the entire current ship can be placed
                    #looping through each block
                    for block in range(0, length):
                        if (collumn, row+block) in ai_prev_attacked:
                            can_place = False

                    #would the ship go off the edge of the board
                    if row+length-1 > len(board)-1:
                        can_place = False

                    #updating matrix values based on if the ship can be placed
                    if can_place:
                        for block in range(0, length):
                            board_matrix[row+block][collumn] += 1

    coord_list = list()
    max_value = 0
    #calculating the max value in the matrix
    for row in range(0, len(board_matrix)):
        for collumn in range(0, len(board_matrix)):
            if board_matrix[row][collumn] > max_value:
                max_value = board_matrix[row][collumn]

    max_value = max_value
    #finding the max value in the matrix and its index
    for i, x in enumerate(board_matrix):
        if max_value in x:
            coord_list.append((x.index(max_value), i))

    return (coord_list[0][0], coord_list[0][1])

def difficulty_move():
#selects the move that is returned based on the difficulty
    if DIFFICULTY == "Medium":
        return random_move()
    if DIFFICULTY == "Hard":
        return hard_move()
    if DIFFICULTY == "Master":
        return master_move()

if __name__ == "__main__":
    app.template_folder = "templates"
    app.run()
    app.secret_key = "battleships"
