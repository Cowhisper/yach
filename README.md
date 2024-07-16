# YACH: Yet Anothor Configuration system by Hinting

## Why YACH?
There are hundreds of configuration system package for python. `YACS` (by @rbgirshick) is a great one especially for DeepLearnig projects.
Many famous projects' configuration system is based on `YACS`. Such as Detectron2, fvcore, etc. However, even if yasc is a handy and reliable
configuration system, it still has some inconvenience. `YASC` keep all information in `CfgNode` which leads to an unsolved issue, how to gracefully
map these information to an existing code (funciton or class). For instance

```python
import torch
from yacs.config import CfgNode


class Model(torch.nn.Module):
    def __init__(self, input_channels, output_channels):
        self.net = torch.nn.Linear(input_channels, output_channels)

    @staticmethod
    def from_config(cfg):
        return Model(
            input_channels=cfg.input_channels,
            output_channels=cfg.output_channels
        )

cfg = CfgNode({'input_channels': 3, 'output_channels': 32})

# Option 1, do arguments mapping in main loop
model = Model(
    input_channels=cfg.input_channels,
    output_channels=cfg.output_channels
)

# Option 2, do some extra coding in class defination. Define a staticmethod in class.
model = Model.from_config(cfg)
```

YACH is offers a more convenient way
```python
# Option 3, use yach!
import torch
from yach import configurable, _C

# register module with specific scope

_C.register('Model1')
_C.Model1.input_channels = 1
_C.Model1.output_channels = 2

@configurable().register  # equal  @configurable('Model1').register
class Model1(torch.nn.Module):
    def __init__(self, input_channels, output_channels):
        super().__init__()
        self.net = torch.nn.Linear(input_channels, output_channels)

model = Model1()

# register module with unbind prefix
_C.register('Model1')
_C.l1.input_channels = 1
_C.l1.output_channels = 2
_C.l2.input_channels = 3
_C.l2.output_channels = 4

@configurable(configurable.UNBIND).register
class Model2(torch.nn.Module):
    def __init__(self, input_channels, output_channels):
        super().__init__()
        self.net = torch.nn.Linear(input_channels, output_channels)

model1 = configurable('l1')(Model2)()
model2 = configurable('l2')(Model2)()

# you can overwrite augments by passing a new value
model1 = configurable('l1')(Model2)(output_channels=100)
```