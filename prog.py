from treeparse import tp
from state import lexer

plus = lambda x, y: x + y
minus = lambda x, y: x - y

class Engine:
    def __init__(self, context=None, builtins=None):
        self.ctx = context if context else {}
        self.ctx.update(builtins if builtins else{
            '+': plus, '-': minus
        })

    def run(self, script):
        lexed = lexer.words(script)
        tree = tp.parse(lexed)

        return self.resolve(tree)
    
    def resolve(self, tree):
        func = self.ctx[tree[0]]
        return func(*[
            self.resolve(arg) if type(arg) == list else arg
            for arg in tree[1:]
        ])
