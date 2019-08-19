from game import CookieClickerGame
import random

game = CookieClickerGame()
game.cookies = 50

for i in range(1000):
    print(game)
    print("---")
    
    
    game.random_action(weights=[0, 10, 1, 0, 1])
    
    
    # if random.random() < 0.5:
        # idx = random.randrange(len(game.upgrades))
        # game.buy_upgrade(idx)
    # else:
        # idx = random.randrange(len(game.producers))
        # if random.random() < 0.9:
            # game.buy_producer(idx)
        # else:
            # game.sell_producer(idx)
        
    game.advance()
    