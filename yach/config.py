import sys
import copy
import inspect


class XCfgNode(dict):
    def __init__(self, init_dict=None, freeze=False):
        init_dict = {} if init_dict is None else init_dict
        super(XCfgNode, self).__init__(init_dict)
        self.__dict__['__immutable__'] = freeze

    def is_frozen(self):
        return self.__dict__['__immutable__']

    def freeze(self, freeze=True):
        self.__dict__['__immutable__'] = freeze
        for v in self.__dict__.values():
            if isinstance(v, XCfgNode):
                v.freeze(freeze)

    def __getattr__(self, key):
        if key in self:
            return self.get(key)
        else:
            raise AttributeError(
                "No such attribute '{}' in config node".format(key)
            )

    def __setattr__(self, key, value):
        self.set(key, value)

    def get(self, key):
        ks = key.split('.')
        if len(ks) == 1:
            return self[ks[0]]
        else:
            k_suf = '.'.join(ks[1:])
            return self[ks[0]].get(k_suf)

    def set(self, key, value):
        if self.is_frozen():
            raise AttributeError(
                "Attempted to modify on a frozen config node"
            )
        ks = key.split('.')
        if len(ks) == 1:
            self[ks[0]] = value
            return
        else:
            node_key = '.'.join(ks[:-1])
            if not self.has(node_key):
                self.register(node_key)
            node = self.get(node_key)
            if isinstance(node, XCfgNode):
                node[ks[-1]] = value
            else:
                raise AttributeError(f"{node_key} is not a XCfgNode")
            return

    def has(self, key):
        ks = key.split('.')
        if len(ks) == 1:
            return ks[0] in self
        else:
            if ks[0] not in self:
                return False
            if isinstance(self[ks[0]], XCfgNode):
                return self[ks[0]].has('.'.join(ks[1:]))
            else:
                return False

    def register(self, key):
        if self.is_frozen():
            raise AttributeError(
                "Attempted to modify on a frozen config node"
            )
        ks = key.split('.')
        if len(ks) > 1:
            if ks[0] not in self:
                self[ks[0]] = XCfgNode()
            if isinstance(self[ks[0]], XCfgNode):
                self[ks[0]].register('.'.join(ks[1:]))
            else:
                raise AttributeError(f'{ks[0]} is not a XCfgNode')
        else:
            self[key] = XCfgNode()

    def clone(self):
        return copy.deepcopy(self)

    def pprint(self):
        # print in yaml format
        def _recursive(cfg, indent=0):
            s = ''
            for k, v in cfg.items():
                if isinstance(v, XCfgNode):
                    s += ' ' * indent + k + ':\n'
                    s += _recursive(v, indent + 2)
                else:
                    s += ' ' * indent + k + ': ' + str(v) + '\n'
            return s
        return _recursive(self)

    def delete(self, key):
        ks = key.split('.')
        if ks[0] not in self:
            raise AttributeError(f'{ks[0]} does not exist')
        if len(ks) == 1:
            del self[ks[0]]
        else:
            if isinstance(self[ks[0]], XCfgNode):
                self[ks[0]].delete('.'.join(ks[1:]))
            else:
                raise AttributeError(f'{ks[0]} is not a XCfgNode')

CFG = XCfgNode()


def configurable(scope=None):
    def _configurable(func):
        def wrapper(*args, **kwargs):
            signature = inspect.signature(func)
            for name, param in signature.parameters.items():
                if isinstance(param.annotation, str):
                    if scope is not None and param.annotation.startswith('.'):
                        annotation = scope + param.annotation
                    else:
                        annotation = param.annotation
                    if name not in kwargs:
                        kwargs[name] = CFG.get(annotation)
                else:
                    annotation = scope + '.' + name if scope is not None else name
                    if name not in kwargs:
                        kwargs[name] = CFG.get(annotation)
            return func(*args, **kwargs)
        return wrapper
    return _configurable


def merge_from_sys_argv(cfg=None):
    cfg = CFG if cfg is None else cfg
    for arg in sys.argv[1:]:
        if '=' in arg:
            k, v = arg.split('=')
            try:
                v = eval(v)
            except:
                pass
            cfg[k] = v

