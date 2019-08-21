import torch.nn as nn
import torch
from torch.nn.functional import relu, smooth_l1_loss
from torch import sigmoid
from torch.optim import RMSprop

class LinearPredictor(nn.Module):
    def __init__(self, input_size, output_size):
        super().__init__()
        
        self.lin1 = nn.Linear(input_size, 32)
        self.lin2 = nn.Linear(32, 32)
        self.lin3 = nn.Linear(32, 32)
        self.head = nn.Linear(32, output_size)
        
        self.loss = smooth_l1_loss
        self.optimizer = RMSprop(self.parameters())
        
    def forward(self, x):
        x = relu(self.lin1(x))
        x = relu(self.lin2(x))
        x = relu(self.lin3(x))
        y = sigmoid(self.head(x))
        
        return y
        
def train(model, actual, outputs):
    model.optimizer.zero_grad()
    loss = model.loss(actual, outputs)
    loss.backward()
    model.optimizer.step()
        
        
if __name__ == "__main__":
    model = LinearPredictor(10, 10)
    print(model)
    inputs = torch.tensor([0]*10, dtype=torch.float)
    desired = torch.tensor([0]*9 + [1], dtype=torch.float)
    
    for i in range(100):
        pred = model(inputs)
        print(pred)
        train(model, desired, pred)