import sys
from lexer import tokenize
from parser import Parser
from ast_nodes import *

class TypeEnv:
    def __init__(self): self.store = {}
    def push(self):     pass
    def pop(self):      pass
    def declare(self, name, t): self.store[name] = t
    def lookup(self, name):     return self.store.get(name, 'unknown')

PROMO = {
    ('int',   'int'):   'int',
    ('float', 'float'): 'float',
    ('int',   'float'): 'float',
    ('float', 'int'):   'float',
}

def decorate(node: Node, env: TypeEnv) -> str:
    if isinstance(node, Program):
        for s in node.stmts:
            decorate(s, env)
        node.dtype = 'void'

    elif isinstance(node, DeclAssign):
        et = decorate(node.expr, env)
        if et != node.decl_type and et not in ('unknown', 'error'):
            node.dtype = f'error: expected {node.decl_type}, got {et}'
        else:
            node.dtype = node.decl_type
        env.declare(node.name, node.decl_type)

    elif isinstance(node, Assign):
        et = decorate(node.expr, env)
        declared = env.lookup(node.name)
        if declared == 'unknown':
            node.dtype = et
            env.declare(node.name, et)
        elif et not in ('unknown',) and et != declared:
            node.dtype = f'error: expected {declared}, got {et}'
        else:
            node.dtype = declared

    elif isinstance(node, IfStmt):
        decorate(node.cond, env)
        for s in node.body:
            decorate(s, env)
        node.dtype = 'void'

    elif isinstance(node, BinOp):
        lt = decorate(node.left,  env)
        rt = decorate(node.right, env)
        node.dtype = PROMO.get((lt, rt), 'unknown')

    elif isinstance(node, UnaryOp):
        node.dtype = decorate(node.operand, env)

    elif isinstance(node, Num):
        node.dtype = node.raw_type

    elif isinstance(node, Var):
        node.dtype = env.lookup(node.name)

    return node.dtype

def render(node: Node, indent: int = 0) -> str:
    pad = '  ' * indent
    lines = []

    if isinstance(node, Program):
        lines.append(f'{pad}Program  [dtype: {node.dtype}]')
        for s in node.stmts:
            lines.append(render(s, indent + 1))

    elif isinstance(node, DeclAssign):
        lines.append(f'{pad}DeclAssign  name={node.name}  decl_type={node.decl_type}  [dtype: {node.dtype}]')
        lines.append(render(node.expr, indent + 1))

    elif isinstance(node, Assign):
        lines.append(f'{pad}Assign  name={node.name}  [dtype: {node.dtype}]')
        lines.append(render(node.expr, indent + 1))

    elif isinstance(node, IfStmt):
        lines.append(f'{pad}IfStmt  [dtype: {node.dtype}]')
        lines.append(f'{pad}  cond:')
        lines.append(render(node.cond, indent + 2))
        lines.append(f'{pad}  body:')
        for s in node.body:
            lines.append(render(s, indent + 2))

    elif isinstance(node, BinOp):
        lines.append(f'{pad}BinOp  op={node.op!r}  [dtype: {node.dtype}]')
        lines.append(render(node.left,  indent + 1))
        lines.append(render(node.right, indent + 1))

    elif isinstance(node, UnaryOp):
        lines.append(f'{pad}UnaryOp  op={node.op!r}  [dtype: {node.dtype}]')
        lines.append(render(node.operand, indent + 1))

    elif isinstance(node, Num):
        lines.append(f'{pad}Num  value={node.value}  [dtype: {node.dtype}]')

    elif isinstance(node, Var):
        lines.append(f'{pad}Var  name={node.name}  [dtype: {node.dtype}]')

    return '\n'.join(lines)

def main():
    if len(sys.argv) != 3:
        print('Usage: python x.py gramatica.txt cadenas.txt')
        sys.exit(1)

    _, _gram_file, cadenas_file = sys.argv

    with open(cadenas_file, encoding='utf-8') as f:
        source = f.read()

    tokens = tokenize(source)
    tree   = Parser(tokens).parse()
    env    = TypeEnv()
    decorate(tree, env)

    output   = render(tree)
    out_file = cadenas_file.replace('.txt', '_ast.txt')

    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f'AST written to {out_file}')
    print(output)

if __name__ == '__main__':
    main()