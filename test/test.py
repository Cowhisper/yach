import pytest
import sys
sys.path.append('.')
print(sys.path)
from yach.config import XCfgNode, configurable, CFG, merge_from_sys_argv


# write pytest test case of XCfgNode

def test_xcfgnode():
    node = XCfgNode({'a': 1})
    assert node.get('a') == 1
    
    node.set('b', 2)
    assert node.get('b') == 2
    
    node.freeze(True)
    assert node.is_frozen()

    with pytest.raises(AttributeError):
        node.set('c', 3)

    node.freeze(False)
    with pytest.raises(AttributeError):
        node.set('a.b.c', 3)

    node.delete('a')
    assert node.has('a') is False

    node.register('a.b.c')
    assert isinstance(node.get('a.b.c'), XCfgNode)

    node_new = node.clone()
    assert node_new == node

    text = node.pprint()
    result = """
b: 2
a:
  b:
    c:
""".strip()
    assert text.strip() == result


@configurable()
class ExampleClass1:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    @property
    def c(self):
        return self.a + self.b
    
    @staticmethod
    def d():
        return 1
    
    def __call__(self, c):
        return self.a + self.b + c

def test_configurable():
    CFG.a = 1
    CFG.b = 2
    ec = ExampleClass1()
    assert ec.a == 1
    assert ec.b == 2
    assert ec.c == 3
    assert ec.d() == 1
    # assert ExampleClass1.d() == 1
    assert ec(3) == 6


def test_merge_from_sys_argv():
    sys.argv.append('a=1')
    sys.argv.append('b=test')
    sys.argv.append('c=True')
    merge_from_sys_argv()
    assert CFG.a == 1
    assert CFG.b == 'test'
    assert CFG.c is True