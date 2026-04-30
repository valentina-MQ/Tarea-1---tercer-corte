class Node:
    dtype = None

class Program(Node):
    def __init__(self, stmts): self.stmts = stmts

class DeclAssign(Node):
    # int a = expr  /  float a = expr
    def __init__(self, decl_type, name, expr):
        self.decl_type = decl_type   # 'int' | 'float'
        self.name      = name
        self.expr      = expr

class Assign(Node):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

class IfStmt(Node):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body   # list[Node]

class BinOp(Node):
    def __init__(self, op, left, right):
        self.op = op; self.left = left; self.right = right

class UnaryOp(Node):
    def __init__(self, op, operand):
        self.op = op; self.operand = operand

class Num(Node):
    def __init__(self, value, raw_type):
        self.value    = value
        self.raw_type = raw_type   # 'int' | 'float'

class Var(Node):
    def __init__(self, name): self.name = name