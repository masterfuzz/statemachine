# leaf -> into current branch
# infix branch -> left, rest into new branch (precedence?)
# prefix branch -> new branch, rest under
# postfix branch -> end branch

#['op', 'word'...]


class TreeParse:
    def __init__(self, **symbol_categories):
        self.sc = {
            sym: cat for cat, sym_list in symbol_categories.items()
            for sym in sym_list
        }

    def parse(self, lex):
        tree = [None]
        def _parse(branch, lex):
            if not lex: return branch

            while True:
                try: 
                    sym, val = next(lex)
                except StopIteration:
                    return branch

                cat = self.sc.get(sym, None)
                if cat == 'leaf':
                    if sym == 'number':
                        branch.append(float(val))
                    else:
                        branch.append(val)
                elif cat == 'prefix':
                    branch.append(_parse([None], lex))
                elif cat == 'postfix':
                    return branch
                elif cat == 'infix':
                    if branch[0] is None:
                        branch[0] = val
                    else:
                        left = branch.pop()
                        branch.append(_parse([val, left], lex))
                else:
                    return branch
            return branch

        return _parse(tree, iter(lex))


tp = TreeParse(
    leaf = ['word', 'number'],
    infix = ['op'],
    prefix = ['lparen'],
    postfix = ['rparen']
)

