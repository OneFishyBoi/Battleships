import components
import random
import game_engine

#settings up player dictionary
players = dict()

#function that creates board coordinates in the form of a tuple
def generate_attack():
    #find the length of the players board
    board_size = 9
    
    #generate a tuple between 0 and the size of the board
    coord = (random.randint(0, board_size),random.randint(0, board_size))

    return coord

def ai_opponent_game_loop():
    print("welcome to battleships, have fun 😎😎😎")

    #initialising the players
    human_username = input("please input human username: ")
    ai_username = input("please input AI username: ")
    board_size = int(input("please input the size of the board you would like to play on: "))

    #setting up board and ships
    players[human_username] = [components.initialise_board(board_size), components.create_battleships()]
    players[ai_username] = [components.initialise_board(board_size), components.create_battleships()]
    
    #placing ships
    players[human_username][0] = components.place_battleships(players[human_username][0], players[human_username][1], "custom")
    players[ai_username][0] = components.place_battleships(players[ai_username][0], players[ai_username][1], "random")

    game_over = False
    #game loop
    while not game_over:
        #declaring variables
        ai_sunk = 0
        human_sunk = 0

        #user attack
        print("----------human move----------")
        if game_engine.attack(game_engine.cli_coordinates_input(), players[ai_username][0], players[ai_username][1]):
            print("hit")
        else:
            print("miss")
        
        #checking if the one of the players ships are all sunk
        for ship in players[human_username][1]:
            if players[ai_username][1][ship] == "0":
                ai_sunk += 1

        #checking if player has won
        if ai_sunk == 5:
            print("You win 🤑🤑🤑")
            return

        #ai attack
        print("----------AI move----------")
        if game_engine.attack(generate_attack(), players[human_username][0], players[human_username][1]):
            print("hit")
        else:
            print("miss")

        #creating ascii representation of human player board
        #looping through all rows
        print("----------human board----------")
        for row in range(0, board_size):
            #looping through all collums
            current_collumn = ""
            for collumn in range(0, board_size):
                #printing X for ship and O for nothing
                if players[human_username][0][row][collumn] == None:
                    current_collumn = current_collumn + "O "
                else:
                    current_collumn = current_collumn + "X "
            print(current_collumn)
        
        #checking if the one of the players ships are all sunk
        for ship in players[human_username][1]:
            if players[human_username][1][ship] == "0":
                human_sunk += 1
        
        #checking if player has lost
        if human_sunk == 5:
            print("You lose 🤡🤡🤡")
            return
        
#live game
ai_opponent_game_loop()