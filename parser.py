from lexer import TT, Token
from ast_nodes import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos    = 0

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def consume(self, *types) -> Token:
        tok = self.peek()
        if types and tok.type not in types:
            raise SyntaxError(
                f'Expected {types}, got {tok.type} ({tok.value!r}) at line {tok.line}')
        self.pos += 1
        return tok

    def match(self, *types) -> bool:
        return self.peek().type in types

    def skip_newlines(self):
        while self.match(TT.NEWLINE):
            self.consume(TT.NEWLINE)

    def parse(self) -> Program:
        stmts = self.stmt_list()
        self.consume(TT.EOF)
        return Program(stmts)

    def stmt_list(self) -> list:
        stmts = []
        self.skip_newlines()
        while not self.match(TT.EOF, TT.DEDENT):
            stmts.append(self.stmt())
            self.skip_newlines()
        return stmts

    def stmt(self) -> Node:
        tok = self.peek()
        if tok.type in (TT.INT_KW, TT.FLOAT_KW):
            return self.decl_assign()
        elif tok.type == TT.IF:
            return self.if_stmt()
        elif tok.type == TT.ID:
            if self.tokens[self.pos + 1].type == TT.EQ:
                return self.assign()
        return self.expr_stmt()

    def decl_assign(self) -> DeclAssign:
        type_tok = self.consume(TT.INT_KW, TT.FLOAT_KW)
        decl_t   = 'int' if type_tok.type == TT.INT_KW else 'float'
        name     = self.consume(TT.ID).value
        self.consume(TT.EQ)
        expr     = self.expr()
        self.consume(TT.NEWLINE)
        return DeclAssign(decl_t, name, expr)

    def assign(self) -> Assign:
        name = self.consume(TT.ID).value
        self.consume(TT.EQ)
        expr = self.expr()
        self.consume(TT.NEWLINE)
        return Assign(name, expr)

    def expr_stmt(self) -> Node:
        node = self.expr()
        self.consume(TT.NEWLINE)
        return node

    def if_stmt(self) -> IfStmt:
        self.consume(TT.IF)
        self.consume(TT.LPAREN)
        cond = self.comparison()
        self.consume(TT.RPAREN)
        self.consume(TT.COLON)
        self.consume(TT.NEWLINE)
        self.consume(TT.INDENT)
        body = self.stmt_list()
        self.consume(TT.DEDENT)
        return IfStmt(cond, body)

    #expr → expr (+|-) term | term
    def expr(self) -> Node:
        node = self.term()
        while self.match(TT.PLUS, TT.MINUS):
            op   = self.consume().value
            node = BinOp(op, node, self.term())
        return node

    #term → term (*|/) factor | factor
    def term(self) -> Node:
        node = self.factor()
        while self.match(TT.STAR, TT.SLASH):
            op   = self.consume().value
            node = BinOp(op, node, self.factor())
        return node

    #factor → (expr) | -factor | ID | NUM
    def factor(self) -> Node:
        tok = self.peek()
        if tok.type == TT.LPAREN:
            self.consume(TT.LPAREN)
            node = self.expr()
            self.consume(TT.RPAREN)
            return node
        elif tok.type == TT.MINUS:
            self.consume(TT.MINUS)
            return UnaryOp('-', self.factor())
        elif tok.type == TT.INT:
            self.consume(TT.INT)
            return Num(tok.value, 'int')
        elif tok.type == TT.FLOAT:
            self.consume(TT.FLOAT)
            return Num(tok.value, 'float')
        elif tok.type == TT.ID:
            self.consume(TT.ID)
            return Var(tok.value)
        raise SyntaxError(f'Unexpected token {tok} in factor')

    #comparison → expr (==|!=|<|<=|>|>=) expr
    def comparison(self) -> Node:
        left = self.expr()
        if self.match(TT.EQEQ, TT.NEQ, TT.LT, TT.LE, TT.GT, TT.GE):
            op    = self.consume().value
            right = self.expr()
            return BinOp(op, left, right)
        return left