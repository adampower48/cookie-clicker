from game import CookieClickerGame
import random

game = CookieClickerGame()
game.cookies = 100

for i in range(100):
    print(game)
    print("---")
    
    idx = random.randrange(len(game.producers))
    if random.random() < 0.9:
        game.buy_producer(idx)
    else:
        game.sell_producer(idx)
        
    game.advance()
    