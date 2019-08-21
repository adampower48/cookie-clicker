from game import CookieClickerGame
import random
from network import LinearPredictor, train
import torch

def argmax(x):
    return max(range(len(x)), key=lambda i: x[i])

class State:
    def __init__(self, game):
        self.game = game
        
    def get_state(self):
        upgrade_state = [int(u.owned) for u in self.game.upgrades]
        producer_state = [int(p.n_owned) for p in self.game.producers]
    
        return producer_state + upgrade_state
        
    def get_action_space(self):
        all_actions = self.game.get_all_actions()
        
        total_actions = 0
        for action in all_actions:
            if len(action) == 1:
                total_actions += 1
            else:
                total_actions += len(action[1])
                
        return total_actions
        
    def get_action_availability(self):
        all_actions = self.game.get_all_actions()
        avail_actions = self.game.get_available_actions()
        action_availability = []
        
        for i, action in enumerate(all_actions):
            if len(action) == 1:
                action_availability.append(True)
            else:
                for args in action[1]:
                    if args in avail_actions[i][1]:
                        action_availability.append(True)
                    else:
                        action_availability.append(False)
                        
        return action_availability
        
    def prediction_to_action(self, pred):
        all_actions = self.game.get_all_actions()
        
        for i, action in enumerate(all_actions):
            if len(action) == 1:
                if pred == 0:
                    return action
                else:
                    pred -= 1
                    
            else:
                if pred < len(action[1]):
                    return action[0], action[1][pred]
                else:
                    pred -= len(action[1])
            
        return None
        
    def perform_action(self, action, advance=True):
        old_state = self.get_state()
        old_value = self.game.cpt
    
    
        if len(action) == 1:
            action[0]()
        else:
            action[0](*action[1])
            
        if advance:
            self.game.advance()
    
        new_state = self.get_state()
        new_value = self.game.cpt
        
        return new_value - old_value # reward
        
        
class Predictor:
    def __init__(self):
        self.model = self.build_model()
        
    def build_model(self):
        def rand_model(state):
            n_actions = state.get_action_space()
            return [random.random() for _ in range(n_actions)]
            
        return rand_model
        
    def predict(self, state):
        preds = self.model(state)
        avail = state.get_action_availability()
        preds = [p * a for p, a in zip(preds, avail)]
        print(preds)
        return argmax(preds)
        
def reinforcement_learn(predictor, turns=1000):
    game = CookieClickerGame(verbose=False)
    game.cookies = 100
    state = State(game)
    # predictor = Predictor()
    # predictor = LinearPredictor(len(state.get_state()), state.get_action_space())
    
    for i in range(1000):
        # print(game.str_basic())
        # print(game)
        
        # pred = predictor.predict(state)
        inputs_tensor = torch.tensor(state.get_state(), dtype=torch.float)
        pred_tensor = predictor(inputs_tensor)
        
        avail_preds = [p * a for p, a in zip(pred_tensor.detach().numpy(), state.get_action_availability())]
        # pred_idx = argmax(avail_preds)
        pred_idx = random.choices(range(len(avail_preds)), avail_preds, k=1)[0]
        
        
        action = state.prediction_to_action(pred_idx)
        reward = state.perform_action(action)
        # print(avail_preds, "->", pred_idx)
        # print("reward:", reward)
        
        desired_tensor = pred_tensor.clone()
        
        alpha = 0.01
        if reward > 0:
            desired_tensor[pred_idx] += alpha
            train(predictor, desired_tensor, pred_tensor)
        elif reward < 0:
            desired_tensor[pred_idx] -= alpha
            train(predictor, desired_tensor, pred_tensor)
            
    print(game.total_cookies, game.cpt)
    
        
if __name__ == "__main__":
    _state = State(CookieClickerGame())
    predictor = LinearPredictor(len(_state.get_state()), _state.get_action_space())
    
    for i in range(10):
        reinforcement_learn(predictor, 1000)