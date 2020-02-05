from treeparse import tp, Literal, Leaf
from state import lexer

BUILTINS = {
    '+': lambda x, y: x + y,
    '-': lambda x, y: x - y,
    '*': lambda x, y: x * y,
    '/': lambda x, y: x / y,
    'print': lambda *x: print(x)
}

class Engine:
    def __init__(self, context=None, builtins=None):
        self.ctx = context if context else {}
        self.ctx.update(builtins if builtins else BUILTINS)
        self.ctx['='] = self._set_op()

    def _set_op(self):
        def inner(left, right):
            if type(left) == Leaf:
                self.ctx[left.value] = right
                return right
            else:
                raise ValueError("can't set non symbol")
        return inner

    def run(self, script):
        lexed = lexer.words(script)
        tree = tp.parse(lexed)

        return self.resolve(tree)

    def leaf_resolve(self, leaf):
        if isinstance(leaf, Literal):
            return leaf.value
        else:
            if leaf.value in self.ctx:
                return self.ctx[leaf.value]
            else:
                return leaf
    
    def resolve(self, tree):
        func = self.ctx[tree[0]]
        return func(*[
            self.resolve(arg) if type(arg) == list else self.leaf_resolve(arg)
            for arg in tree[1:]
        ])

e = Engine()