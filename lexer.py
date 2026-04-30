import re
from enum import Enum, auto

class TT(Enum):
    INT_KW = auto(); FLOAT_KW = auto()
    IF     = auto(); COLON    = auto()
    ID     = auto()
    FLOAT  = auto(); INT      = auto()
    PLUS   = auto(); MINUS    = auto()
    STAR   = auto(); SLASH    = auto()
    LPAREN = auto(); RPAREN   = auto()
    EQ     = auto(); EQEQ     = auto()
    NEQ    = auto(); LT       = auto()
    LE     = auto(); GT       = auto()
    GE     = auto()
    NEWLINE= auto(); INDENT   = auto()
    DEDENT = auto(); EOF      = auto()

TOKEN_SPEC = [
    ('FLOAT_LIT', r'\d+\.\d+'),
    ('INT_LIT',   r'\d+'),
    ('KW_ID',     r'[A-Za-z_]\w*'),
    ('EQEQ',  r'=='), ('NEQ', r'!='),
    ('LE',    r'<='), ('GE',  r'>='),
    ('EQ',    r'='),  ('LT',  r'<'), ('GT', r'>'),
    ('PLUS',  r'\+'), ('MINUS', r'-'),
    ('STAR',  r'\*'), ('SLASH', r'/'),
    ('LPAREN',r'\('), ('RPAREN',r'\)'),
    ('COLON', r':'),
    ('SKIP',  r'[ \t]+'),
    ('MISMATCH', r'.'),
]

KEYWORDS = {'int': TT.INT_KW, 'float': TT.FLOAT_KW, 'if': TT.IF}
MASTER_RE = re.compile('|'.join(f'(?P<{n}>{p})' for n, p in TOKEN_SPEC))

class Token:
    __slots__ = ('type', 'value', 'line')
    def __init__(self, t, v, l): self.type=t; self.value=v; self.line=l
    def __repr__(self): return f'Token({self.type}, {self.value!r})'

def tokenize(source: str) -> list:
    tokens = []
    indent_stack = [0]

    for lineno, raw in enumerate(source.splitlines(), 1):
        if not raw.strip():
            continue
        stripped = raw.lstrip(' ')
        indent   = len(raw) - len(stripped)
        current  = indent_stack[-1]

        if indent > current:
            indent_stack.append(indent)
            tokens.append(Token(TT.INDENT, indent, lineno))
        elif indent < current:
            while indent_stack[-1] > indent:
                indent_stack.pop()
                tokens.append(Token(TT.DEDENT, indent, lineno))

        for mo in MASTER_RE.finditer(stripped):
            kind, val = mo.lastgroup, mo.group()
            if kind == 'SKIP':
                continue
            elif kind == 'MISMATCH':
                raise SyntaxError(f'Unexpected {val!r} at line {lineno}')
            elif kind == 'FLOAT_LIT':
                tokens.append(Token(TT.FLOAT, float(val), lineno))
            elif kind == 'INT_LIT':
                tokens.append(Token(TT.INT, int(val), lineno))
            elif kind == 'KW_ID':
                tokens.append(Token(KEYWORDS.get(val, TT.ID), val, lineno))
            else:
                tokens.append(Token(getattr(TT, kind), val, lineno))

        tokens.append(Token(TT.NEWLINE, '\n', lineno))

    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(Token(TT.DEDENT, 0, 0))

    tokens.append(Token(TT.EOF, None, 0))
    return tokens