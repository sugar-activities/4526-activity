"""
kuku_config

Configuration keys for Kuku Anakula
(Need to i81n this file)

GRID_SIZE      : Size of the default playing grid
FRAMES_PER_SEC : Playing speed (?)
PLAYER_SPEED   : How fast the player moves (?)
GAME_TIME      : Number of seconds allowed for each question
PLAYER_LIVES   : Number of Lives allowed for each game
QUESTION_FILES : List of question files that make up the game curriculum.
                 Each of these files is read and used sequentially throughout the game.
"""


GRID_SIZE = 3
FRAMES_PER_SEC = 15
PLAYER_SPEED   = 12
GAME_TIME = 20
PLAYER_LIVES = 3
QUESTION_FILES = [
                  #Number questions with images displaying numbers of fruits
                  "question_files/numbers/numbers_1-10.dat",
                  
                  #Addition
                  "question_files/arithmetic/addition_p0_0-10.dat",
                  
                  #Subtraction
                  "question_files/arithmetic/subtraction_p0_0-10.dat",
                  
                  #Addition and Subtraction
                  "question_files/arithmetic/addsub_p0_0-10.dat",
                  
                  #Multiplication
                  "question_files/arithmetic/multiplication_p0_0-10.dat",
                  
                  #Division
                  "question_files/arithmetic/division_p0_0-10.dat",
                  
                  #Multiplication and Division
                  "question_files/arithmetic/multdiv_p0_0-10.dat",
                  
                  #Multiples (Divisibly by x)
                  "question_files/arithmetic/multiples_p0_-10-10.dat",
                  
                  #All arithmetic
                  "question_files/arithmetic/allops_p0_0-10.dat",
                  
                  #All arithmetic with multiples
                  "question_files/arithmetic/random_p0_0-10.dat"
                  ]
# QUESTION_FILES = ["question_files/arithmetic/my_questions.dat"]

