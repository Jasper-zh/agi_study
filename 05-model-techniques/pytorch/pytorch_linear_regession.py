"""
1. y = ax + b

>>>
1. 数据 tensor
2. model
3. 完成training
    3.1 forward
    3.2 backword (loss)
    3.3 optimizer
4. matplotlib
"""

import torch
import torch.nn as nn
import matplotlib.pyplot as plt


# x = torch.linspace(0, 20, 500)
# k = 3
# b = 10
# y = k*x + b
# plt.scatter(x.data.numpy(), y.data.numpy())
# plt.show()

# 1. data

x = torch.rand(512)
noise = 0.2 * torch.rand(x.size())
k = 3
b = 10
y = k*x + b + noise
# plt.scatter(x.data.numpy(), y.data.numpy())
# plt.show()

class LinearModel(nn.Module):
    def __init__(self, in_fea, out_fea):
        super(LinearModel, self).__init__()
        self.out = nn.Linear(in_features=in_fea, out_features= out_fea)

    def forward(self, x):
        x = self.out(x)
        return x


input_x = torch.unsqueeze(x, dim=1)
input_y = torch.unsqueeze(y, dim=1)
model = LinearModel(1,1)
loss_func = nn.MSELoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.002)

plt.ion()
for step in range(1000):
    pred = model(input_x)
    loss = loss_func(pred, input_y)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    if step % 10 == 0:
        plt.cla()
        plt.scatter(input_x.data.numpy(),input_y.data.numpy())
        plt.plot(input_x.data.numpy(),pred.data.numpy(), 'r-', lw=5)
        [w,b] = model.parameters()
        plt.xlim(0, 1.1)
        plt.ylim(0,20)
        plt.text(0,0.5, 'loss=%.4f, k=%.2f, b=%.2f'%(loss.item(),w.item(), b.item()))
        plt.pause(1)

plt.ioff()
plt.show()