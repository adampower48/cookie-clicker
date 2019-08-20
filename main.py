from game import CookieClickerGame
import random

game = CookieClickerGame()
game.cookies = 0

for i in range(int(100e3)):
    print("---")
    print(game)
    print("---")
    
    
    game.random_action(weights=[0, 10, 1, 0, 1])
    game.advance()
    