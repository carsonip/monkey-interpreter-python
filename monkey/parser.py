import types
from enum import IntEnum, auto
from typing import Callable

from monkey import lexer, token, ast

PrefixParseFuncType = Callable[[], ast.Expression]
InfixParseFuncType = Callable[[ast.Expression], ast.Expression]


class UnexpectedTokenType(Exception):
    pass


class NoPrefixParseFuncError(Exception):
    pass


class Precedence(IntEnum):
    LOWEST = auto()
    EQUALS = auto()
    LESSGREATER = auto()
    SUM = auto()
    PRODUCT = auto()
    PREFIX = auto()
    CALL = auto()


PRECEDENCES: dict[token.TokenType, Precedence] = {
    token.TokenType.EQ: Precedence.EQUALS,
    token.TokenType.NOT_EQ: Precedence.EQUALS,
    token.TokenType.LT: Precedence.LESSGREATER,
    token.TokenType.GT: Precedence.LESSGREATER,
    token.TokenType.PLUS: Precedence.SUM,
    token.TokenType.MINUS: Precedence.SUM,
    token.TokenType.SLASH: Precedence.PRODUCT,
    token.TokenType.ASTERISK: Precedence.PRODUCT,
}


class Parser:

    def __init__(self, lexer_: lexer.Lexer) -> None:
        self.prefix_parse_funcs: dict[token.TokenType, PrefixParseFuncType] = {
            token.TokenType.IDENT: type(self).parse_identifier,
            token.TokenType.INT: type(self).parse_integer_literal,
            token.TokenType.BANG: type(self).parse_prefix_expression,
            token.TokenType.MINUS: type(self).parse_prefix_expression,
        }
        self.infix_parse_funcs: dict[token.TokenType, InfixParseFuncType] = {
            token.TokenType.PLUS: type(self).parse_infix_expression,
            token.TokenType.MINUS: type(self).parse_infix_expression,
            token.TokenType.SLASH: type(self).parse_infix_expression,
            token.TokenType.ASTERISK: type(self).parse_infix_expression,
            token.TokenType.EQ: type(self).parse_infix_expression,
            token.TokenType.NOT_EQ: type(self).parse_infix_expression,
            token.TokenType.LT: type(self).parse_infix_expression,
            token.TokenType.GT: type(self).parse_infix_expression,
        }

        self.lexer = lexer_
        self.errors: list[str] = []
        self.current_token: token.Token | None = None
        self.peek_token: token.Token | None = None
        self.next_token()
        self.next_token()

    def next_token(self) -> None:
        self.current_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def expect_peek_and_next(self, token_type: token.TokenType) -> None:
        if self.peek_token.type_ != token_type:
            self.errors.append(f'Expected next token to be {token_type.name}, got {self.peek_token.type_.name} instead')
            raise UnexpectedTokenType
        self.next_token()

    def parse_program(self) -> ast.Program:
        program = ast.Program()

        while self.current_token.type_ != token.TokenType.EOF:
            try:
                statement = self.parse_statement()
            except UnexpectedTokenType:
                pass
            except NoPrefixParseFuncError:
                pass
            else:
                program.statements.append(statement)
            finally:
                self.next_token()
        return program

    def parse_statement(self) -> ast.Statement:
        match self.current_token.type_:
            case token.TokenType.LET:
                return self.parse_let_statement()
            case token.TokenType.RETURN:
                return self.parse_return_statement()
            case _:
                return self.parse_expression_statement()

    def parse_let_statement(self) -> ast.LetStatement:
        tok = self.current_token
        self.expect_peek_and_next(token.TokenType.IDENT)
        ident = self.parse_identifier()
        self.expect_peek_and_next(token.TokenType.ASSIGN)
        self.next_token()
        expression = self.parse_expression(Precedence.LOWEST)
        while self.current_token.type_ != token.TokenType.SEMICOLON:
            self.next_token()
        return ast.LetStatement(token=tok, name=ident, value=expression)

    def parse_return_statement(self) -> ast.ReturnStatement:
        tok = self.current_token
        self.next_token()
        expression = self.parse_expression(Precedence.LOWEST)
        while self.current_token.type_ != token.TokenType.SEMICOLON:
            self.next_token()
        return ast.ReturnStatement(token=tok, return_value=expression)

    def parse_expression_statement(self) -> ast.ExpressionStatement:
        statement = ast.ExpressionStatement(
            token=self.current_token,
            expression=self.parse_expression(Precedence.LOWEST),
        )
        if self.peek_token.type_ == token.TokenType.SEMICOLON:
            self.next_token()
        return statement

    def parse_expression(self, precedence: Precedence) -> ast.Expression:
        prefix_parse_func = self.prefix_parse_funcs.get(self.current_token.type_)
        if prefix_parse_func is None:
            self.errors.append(f'No prefix parse function for {self.current_token.type_.name} found')
            raise NoPrefixParseFuncError
        left_expression = types.MethodType(prefix_parse_func, self)()

        while self.peek_token.type_ != token.TokenType.SEMICOLON and precedence < self.peek_precedence():
            infix_parse_func = self.infix_parse_funcs.get(self.peek_token.type_)
            if infix_parse_func is None:
                return left_expression

            self.next_token()
            left_expression = types.MethodType(infix_parse_func, self)(left_expression)

        return left_expression

    def parse_identifier(self) -> ast.Identifier:
        return ast.Identifier(token=self.current_token, value=self.current_token.literal)

    def parse_integer_literal(self) -> ast.IntegerLiteral:
        return ast.IntegerLiteral(token=self.current_token, value=int(self.current_token.literal, 10))

    def parse_prefix_expression(self) -> ast.PrefixExpression:
        tok = self.current_token
        self.next_token()
        return ast.PrefixExpression(token=tok,
                                    operator=tok.literal,
                                    right=self.parse_expression(Precedence.PREFIX))

    def parse_infix_expression(self, left: ast.Expression) -> ast.InfixExpression:
        tok = self.current_token
        precedence = self.current_precedence()
        self.next_token()
        right = self.parse_expression(precedence)
        return ast.InfixExpression(token=tok,
                                   operator=tok.literal,
                                   left=left,
                                   right=right)

    def current_precedence(self) -> Precedence:
        return PRECEDENCES.get(self.current_token.type_, Precedence.LOWEST)

    def peek_precedence(self) -> Precedence:
        return PRECEDENCES.get(self.peek_token.type_, Precedence.LOWEST)
