import components

#checks and clears attacked square while decrementing ship health
def attack(coordinates, board, battleships):
    #check if the coordinate entered has a ship
    if board[coordinates[1]][coordinates[0]] != None:
        #decrementing the value of the ship hit stored in the battleships dictionary
        ships = ("Aircraft_Carrier", "Battleship", "Cruiser", "Submarine", "Destroyer")
        for item in ships:
            if board[coordinates[1]][coordinates[0]] == item:
                #checking if ship has been sunk
                if battleships[item] == "1":
                    print(item + " sunk")
            
                #decrementing value
                battleships[item] = str(int(battleships[item])-1)
        
        #setting the position to none
        board[coordinates[1]][coordinates[0]] = None

        #"hit"
        return True
    #"miss"
    return False

#takes user coord input
def cli_coordinates_input():
    #defining variables 
    valid = False

    #looping until the user enters a valid input
    while not valid:
        #getting input
        move = input("please input a move in the form x,y e.g. 2,1 or 3,6 etc.: ")
        flag = True

        #checking if user entered string of wrong size
        if len(move) != 3:
            print("move invalid, wrong string size")
            flag = False
        #checking if they entered numbers
        try:
            temp = int(move[0])
            temp = int(move[2])
        except:
            print("move invalid, user entered non number")
            flag = False
        
        #checking to see if user entered in the correct format
        if move[1] != ",":
            flag = False
            print("move invalid, wrong format")
        
        #don't see a way to check if the user entered a move within the board if there are no arguments?
        #checking to see if move entered was valid if not looping
        if flag:
            valid = True

    #creating a tuple out of input
    final_move = (int(move[0]), int(move[2]))
    
    return final_move

def simple_game_loop():
    #welcoming user
    print("Hello and welcome to battleships :)")

    #setting up board and ships
    board = components.initialise_board()
    battleships = components.create_battleships()
    board = components.place_battleships(board, battleships)

    game_finished = False

    #gameplay loop
    while not game_finished:
        if attack(cli_coordinates_input(), board, battleships):
            print("hit")
        else: 
            print("miss")

        #checking if all ships have been sunk
        num_sunk = 0

        for ship in battleships:
            if battleships[ship] == "0":
                num_sunk += 1

        #checking if the game has ended
        if num_sunk == 5:
            print("All ships have been sunk, game won!")
            game_finished = True

if __name__ == "__main__":
    simple_game_loop()

