class Node:
    def __init__(self, val, *children):
        self.val = val
        self.children = list(map(Node, children))

class ClassAll:
    def __contains__(self, x):
        return True
All = ClassAll()

class Marker:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name
    def __str__(self):
        return repr(self)

Eof = Marker("Eof")
Sof = Marker("Sof")
Or = lambda x: (lambda f, g: f(x) or g(x))

def pred(m):
    if callable(m):
        return m
    elif m is None:
        return lambda x: x is None
    else:
        return lambda x: x == m

class Tr:
    def __init__(self, *transitions, **ktrans):
        self.t = { k: pred(v) for k, v in transitions }
        self.t.update({k: pred(v) for k, v in ktrans.items()})

    def add(state, acceptor):
        self.t[state] = acceptor
    
    def __call__(self, x):
        for s, t in self.t.items():
            try:
                match = t(x)
                if match:
                    return s
            except:
                continue
        return False

class MachineInstance:
    def __init__(self, state_machine, start_state=None, accept_states=None):
        self.inner = state_machine
        if start_state:
            self.start = start_state
        else:
            self.start = state_machine.start
        if accept_states:
            self.accept_states = accept_states
        else:
            self.accept_states = state_machine.accept_states

    def accepted(self, state):
        return state in self.accept_states

    @property
    def transition(self):
        return self.inner.transition

class StateMachine:
    def __init__(self, _start_state='start', _accept_states=None, _include_eof=False, _drop_states=None,
                    *transitions, **ktransitions):
        self.transition = {k: v for k, v in transitions}
        self.transition.update(ktransitions)
        self.accept_states = _accept_states if _accept_states else ['accept']
        self.start = _start_state if _start_state else 'start'
        self.eof = _include_eof
        self.drop = _drop_states if _drop_states else []

    def merge(self, part):
        self.transition.update(part.transition)
        self.accept_states += part.accept_states
        self.drop += part.drop

    def accepted(self, state):
        return state in self.accept_states

    def run(self, events, initial=None):
        symbol, state = list(self.gen(events, initial))[-1]
        return symbol, state, self.accepted(state)

    def gen(self, events, initial=None):
        initial = initial if initial else self.start
        machine_stack = []
        state_stack = []
        machine = self
        state = initial

        yield Sof, state
        for event in events:
            transition = machine.transition[state]
            if isinstance(transition, MachineInstance):
                machine_stack.append(machine)
                machine = transition
                state_stack.append(machine.start)
                state = transition.start
            
            state = machine.transition[state](event)
            yield event, state
            if not state:
                return
            if len(machine_stack) and machine.accepted(state):
                # drop down
                # state = machine.escape
                machine = machine_stack.pop()
                # state = state_stack.pop()
        if machine.eof:
            state = machine.transition[state](Eof)
            yield Eof, state

    def words(self, events, initial=None):
        current_state = initial if initial else self.start
        bucket = []
        for symbol, new_state in self.gen(events, initial):
            if current_state == new_state:
                bucket.append(symbol)
            else:
                if current_state not in self.drop:
                    yield current_state, "".join(map(str, bucket))
                bucket = [symbol]
                current_state = new_state
        if current_state not in self.drop:
            yield current_state, "".join(map(str, bucket))

    def submachine(self, initial=None, escape=None):
        return MachineInstance(self, start_state=initial, accept_states=escape)


alpha = lambda x: x >= "A" and x <= "z"
num = lambda x: x >= "0" and x <= "9"
alnum = lambda x: alpha(x) or num(x)
space = lambda x: x.strip() == ""
op = lambda x: x in "+-*/="

lexer = StateMachine(
    _accept_states=["end"],
    _include_eof=True,
    _drop_states=["start", "space", 'end']
)
lexer.merge(StateMachine(
    start = Tr(
        word = alpha, start = space, number = num, lparen = "("
    ),
    word = Tr(
        word = alnum, space = space, end = Eof, op = op, lparen = "(", rparen = ")"
    ),
    number = Tr(
        number = num, space = space, decimal = ".", op = op, end = Eof, rparen = ")"
    ),
    decimal = Tr(
        fraction = num
    ),
    fraction = Tr(
        fraction = num, space = space, op = op, end = Eof, rparen = ")"
    ),
    op = Tr(
        start = space, word = alpha, number = num, lparen = "("
    ),
    space = Tr(
        space = space, op = op, end = Eof, rparen = ")"
    ),
    lparen = lexer.submachine(escape='rparen'),
    rparen = Tr(
        space = space, op = op, end = Eof
    )
))

from treeparse import tp

lex = lexer.words("hello + world")
