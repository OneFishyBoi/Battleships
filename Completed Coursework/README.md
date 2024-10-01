# Battleships game!
## Introduction:

A recreation of battleships which allows the user to select a difficulty, place their ships in a custom configuration and then input coordinates play against the difficulty selected until either the player or the ai wins, it achieves this through launching a interactable web interface. Battleships is a two player game where both players place ships of varying length on thier own boards, then each player takes turn giving a coordinate they would like to attack in the hopes of hitting where the other player has placed a ship. This is repeated until all of the ships of one player are completely destroyed.

## Prerequisites:

Python version 3.11.1

## Installation:

You will need to install the following modules by installing pip, navigating to your terminal, and inputting:

pip install Flask

## Getting started tutorial:

In order to run the game as intended complete the following steps:

1.Run the file battleships_pkg\main.py

2.Navigate to your web browser and enter the local server URL: http://127.0.0.1:5000/select

3.Select a difficulty from the drop down menu and press submit, this will redirect you to: http://127.0.0.1:5000/placement

4.Now you will place your ships by hovering over the squares on the grid displayed where it will show a "shadow" of where the placed ship will go, if you would like to rotate the ship press R, left click on the square when the ship is in a position you would like to place it in. Repeat this until all ships have been placed.

5.Press the green send game button this will cause a popup to flash up saying "Board sent successfully, Redirecting to game", press the okay button. This will redirection you to: http://127.0.0.1:5000/ which is where the main game loop occurs. It contains a large white grid for the player to attack and see if they hit or miss, a smaller blue grid to the side of the screen which shows the players ships and the AI's attacks, and finally a game log which shows all of the AI's past moves and whether they hit or miss.

6.The game will now become a sequence of attacks and notifications. To attack hover over the square you would like to attack on the large white grid and left click. If you hit a ship it will display a red square, if you miss a ship it will display a blue square, if you attack a ship until it is sunk a notification saying "ship sunk" will pop up, simply select ok. Repeat this until a notification saying either "you win", "you lose", or "you drew" pops up.

7.Select ok, this will alter the page to show the ended state of the game and remove the ai attack log. The game is not finished.

## Testing:
Modules needed to test code:
pytest
pytest-depends
pytest-cov

In order to run the tests for the program open the completed coursework file in a code editor such as vscode, navigate the the beaker symbol on the left, select configure tests, select the battleships_pkg file and run the tests inside the tests file.

## Developer documentation:
The main game is made up of a few phases, the difficulty select, the placement, and the attack game loop.
The difficulty select is created using a simple html template which is rendered when the user goes to the http://127.0.0.1:5000/select URL, this part of the game is essentially just made up of rendering the template in the difficulty_select() function and recieving the selection; setting it to a global variable.
The placement phase is similar when the user opens the link http://127.0.0.1:5000/placement it runs the function placement_interface() which checks for a get request, if it is the template will be loaded. It then waits for the user to place all the ships which is done frontend. Then when the user clicks the send game button it sends the placement data to the backend where it is placed onto a global player board using the place_input function. Finally, it sends a verification message to say the placement data has been recieved.
The final phase, the attack phase is a loop where the player clicks, it updates and processes the players attack, then creates and processes the ai attack which is passed to the front end (The backend passes the coord and if the ai hit). This loop repeats until all of the ships of one of the players is sunk, causing the backend to send a message to the front end saying the game is over and who won.

## Details:
license is: Completed Coursework/LISCENSE.txt
source code is: Completed Courseowrk/battleships_pkg
acknowledgements: The GOAT of programming Matt Collinson