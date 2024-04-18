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
from yach import configurable


@configurable()
class Model(torch.nn.Module):
    def __init__(self, input_channels, output_channels):
        self.net = torch.nn.Linear(input_channels, output_channels)


model = Model()
```


## How is it work?
YACH maintains a gobal CfgNode in `yach.config`.