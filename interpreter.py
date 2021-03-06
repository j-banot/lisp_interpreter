import operator as op

# Lisp type definitions
Symbol = str             # A Lisp Symbol is implemented as a Python str
Number = (int, float)    # A Lisp Number is implemented as a Python int or float
Atom = (Symbol, Number)  # A Lips Atom is a Symbol or Number
List = list              # A Lisp List is implemeted as a Python list
Exp = (Atom, List)       # A Scheme expression is an Atom or List
Env = dict               # An Environment dictionary


def tokenize(chars: str) -> list:
    """
    Converts a string of characters into a list of tokens
    :param chars: an input program string
    :return: a list of tokens
    """
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()


def read_from_tokens(tokens: list) -> Exp:
    """
    Assembles nested list of prefix expressions from tokenized program input string
    :param tokens: list of tokens
    :return: nested list of expressions or a symbol
    """
    if not tokens:
        raise SyntaxError('unexpected EOF')
    token = tokens.pop(0)
    if token == '(':
        form = []
        while tokens[0] != ')':
            form.append(read_from_tokens(tokens))
        tokens.pop(0)  # pop off ending )
        return form
    elif token == ')':
        raise SyntaxError('unexpected )')
    else:
        return atom(token)


def atom(token: str) -> Atom:
    """
    Distinguishes number tokens from symbol tokens by converting token to an integer or floating point number
    :param token: single token
    :return: token in correct type
    """
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)


def parse(input_program: str) -> Exp:
    """
    Reads a scheme expression from an input program string
    :param input_program: input program string
    :return: nested list of expressions
    """
    return read_from_tokens(tokenize(input_program))


def standard_env() -> Env:
    """
    An environment maps includes necessary lisp standard function to their python implementation
    :return: dictionary with mapping from lisp primitives to python implementation
    """
    env = Env()
    env.update({
        '+': op.add,
        '-': op.sub,
        '*': op.mul,
        '/': op.truediv,
        '>': op.gt,
        '<': op.lt,
        '>=': op.ge,
        '<=': op.le,
        'eq': op.eq,
        'cons': lambda x, y: [x, y],
        'car': lambda x: x[0],
        'cdr': lambda x: x[1],
        'atom': lambda x: isinstance(x, Atom)
    })
    return env


global_env = standard_env()


def lisp_eval(x: Exp, env=global_env) -> Exp:
    """
    Evaluation of lisp expressions consist of 6 scenarios:
    - a symbol interpreted as a variable name
    - a number that evaluates to itself
    - a conditional if statement
    - a new variable definition
    - a quote operation
    - a procedure call
    :param x: parsed expression
    :param env: environment dictionary
    :return: evaluation result
    """
    if isinstance(x, Symbol):
        return env[x]
    elif isinstance(x, Number):
        return x
    elif x[0] == 'quote':
        (_, result) = x
        return result
    elif x[0] == 'if':
        (_, condition, consequent, alternative) = x
        exp = (consequent if lisp_eval(condition, env) else alternative)
        return lisp_eval(exp, env)
    elif x[0] == 'define':
        (_, symbol, exp) = x
        env[symbol] = lisp_eval(exp, env)
    else:
        proc = lisp_eval(x[0], env)
        args = [lisp_eval(arg, env) for arg in x[1:]]
        return proc(*args)


def repl(prompt='>> '):
    """
    REPL - a read-eval-print loop
    :param prompt: prompt string
    """
    print("Lisp interpreter")
    while True:
        try:
            val = lisp_eval(parse(input(prompt)))
            if val is not None:
                print(lisp_str(val))
        except SyntaxError as e:
            print(f"Syntax error: {e}")
        except ZeroDivisionError:
            print("Zero Division Error")
        except KeyError as e:
            print(f"Lisp syntax error: {e}")
        except KeyboardInterrupt:
            print("Keyboard Interrupt")
            break


def lisp_str(exp):
    """
    Converts a Python object back into scheme-readable string
    :param exp: nested expression
    :return: scheme-readable string
    """
    if isinstance(exp, List):
        return '(' + ' '.join(map(lisp_str, exp)) + ')'
    else:
        return str(exp)
