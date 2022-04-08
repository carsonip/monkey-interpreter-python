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

    @classmethod
    def get(cls, token_type: token.TokenType, default: "Precedence") -> "Precedence":
        return {
            token.TokenType.EQ: cls.EQUALS,
            token.TokenType.NOT_EQ: cls.EQUALS,
            token.TokenType.LT: cls.LESSGREATER,
            token.TokenType.GT: cls.LESSGREATER,
            token.TokenType.PLUS: cls.SUM,
            token.TokenType.MINUS: cls.SUM,
            token.TokenType.SLASH: cls.PRODUCT,
            token.TokenType.ASTERISK: cls.PRODUCT,
        }.get(token_type, default)


class Parser:
    def __init__(self, lexer_: lexer.Lexer) -> None:
        self.lexer = lexer_
        self.errors: list[str] = []
        self.current_token: token.Token = self.lexer.next_token()
        self.peek_token: token.Token = self.lexer.next_token()

    def get_prefix_parse_func(
        self, token_type: token.TokenType
    ) -> PrefixParseFuncType | None:
        parse_funcs: dict[token.TokenType, PrefixParseFuncType] = {
            token.TokenType.IDENT: self.parse_identifier,
            token.TokenType.INT: self.parse_integer_literal,
            token.TokenType.BANG: self.parse_prefix_expression,
            token.TokenType.MINUS: self.parse_prefix_expression,
            token.TokenType.TRUE: self.parse_boolean,
            token.TokenType.FALSE: self.parse_boolean,
            token.TokenType.LPAREN: self.parse_grouped_expression,
            token.TokenType.IF: self.parse_if_expression,
        }
        return parse_funcs.get(token_type)

    def get_infix_parse_func(
        self, token_type: token.TokenType
    ) -> InfixParseFuncType | None:
        parse_funcs: dict[token.TokenType, InfixParseFuncType] = {
            token.TokenType.PLUS: self.parse_infix_expression,
            token.TokenType.MINUS: self.parse_infix_expression,
            token.TokenType.SLASH: self.parse_infix_expression,
            token.TokenType.ASTERISK: self.parse_infix_expression,
            token.TokenType.EQ: self.parse_infix_expression,
            token.TokenType.NOT_EQ: self.parse_infix_expression,
            token.TokenType.LT: self.parse_infix_expression,
            token.TokenType.GT: self.parse_infix_expression,
        }
        return parse_funcs.get(token_type)

    def next_token(self) -> None:
        self.current_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def expect_peek_and_next(self, token_type: token.TokenType) -> None:
        if not self.peek_token.is_type(token_type):
            self.errors.append(
                f"Expected next token to be {token_type.name}, got {self.peek_token.type_.name} instead"
            )
            raise UnexpectedTokenType
        self.next_token()

    def parse_program(self) -> ast.Program:
        program = ast.Program()

        while not self.current_token.is_type(token.TokenType.EOF):
            try:
                statement = self.parse_statement()
            except (UnexpectedTokenType, NoPrefixParseFuncError):
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
        while not self.current_token.is_type(token.TokenType.SEMICOLON):
            self.next_token()
        return ast.LetStatement(token=tok, name=ident, value=expression)

    def parse_return_statement(self) -> ast.ReturnStatement:
        tok = self.current_token
        self.next_token()
        expression = self.parse_expression(Precedence.LOWEST)
        while not self.current_token.is_type(token.TokenType.SEMICOLON):
            self.next_token()
        return ast.ReturnStatement(token=tok, return_value=expression)

    def parse_expression_statement(self) -> ast.ExpressionStatement:
        statement = ast.ExpressionStatement(
            token=self.current_token,
            expression=self.parse_expression(Precedence.LOWEST),
        )
        if self.peek_token.is_type(token.TokenType.SEMICOLON):
            self.next_token()
        return statement

    def parse_expression(self, precedence: Precedence) -> ast.Expression:
        prefix_parse_func = self.get_prefix_parse_func(self.current_token.type_)
        if prefix_parse_func is None:
            self.errors.append(
                f"No prefix parse function for {self.current_token.type_.name} found"
            )
            raise NoPrefixParseFuncError
        left_expression = prefix_parse_func()

        while (
            not self.peek_token.is_type(token.TokenType.SEMICOLON)
            and precedence < self.peek_precedence()
        ):
            infix_parse_func = self.get_infix_parse_func(self.peek_token.type_)
            if infix_parse_func is None:
                return left_expression

            self.next_token()
            left_expression = infix_parse_func(left_expression)

        return left_expression

    def parse_identifier(self) -> ast.Identifier:
        return ast.Identifier(
            token=self.current_token, value=self.current_token.literal
        )

    def parse_integer_literal(self) -> ast.IntegerLiteral:
        return ast.IntegerLiteral(
            token=self.current_token, value=int(self.current_token.literal, 10)
        )

    def parse_boolean(self) -> ast.Boolean:
        return ast.Boolean(
            token=self.current_token,
            value=self.current_token.type_ == token.TokenType.TRUE,
        )

    def parse_prefix_expression(self) -> ast.PrefixExpression:
        tok = self.current_token
        self.next_token()
        return ast.PrefixExpression(
            token=tok,
            operator=tok.literal,
            right=self.parse_expression(Precedence.PREFIX),
        )

    def parse_infix_expression(self, left: ast.Expression) -> ast.InfixExpression:
        tok = self.current_token
        precedence = self.current_precedence()
        self.next_token()
        right = self.parse_expression(precedence)
        return ast.InfixExpression(
            token=tok, operator=tok.literal, left=left, right=right
        )

    def parse_grouped_expression(self) -> ast.Expression:
        self.next_token()
        expression = self.parse_expression(Precedence.LOWEST)
        self.expect_peek_and_next(token.TokenType.RPAREN)
        return expression

    def parse_if_expression(self) -> ast.IfExpression:
        tok = self.current_token
        self.expect_peek_and_next(token.TokenType.LPAREN)
        self.next_token()
        condition = self.parse_expression(Precedence.LOWEST)
        self.expect_peek_and_next(token.TokenType.RPAREN)
        self.expect_peek_and_next(token.TokenType.LBRACE)
        consequence = self.parse_block_statement()
        self.expect_peek_and_next(token.TokenType.RBRACE)
        alternative: ast.BlockStatement | None = None
        if self.peek_token.is_type(token.TokenType.ELSE):
            self.next_token()
            self.expect_peek_and_next(token.TokenType.LBRACE)
            alternative = self.parse_block_statement()
            self.expect_peek_and_next(token.TokenType.RBRACE)

        return ast.IfExpression(
            token=tok,
            condition=condition,
            consequence=consequence,
            alternative=alternative,
        )

    def parse_block_statement(self) -> ast.BlockStatement:
        tok = self.current_token
        statements: list[ast.Statement] = []
        while not self.peek_token.is_type(token.TokenType.RBRACE, token.TokenType.EOF):
            self.next_token()
            statements.append(self.parse_statement())
        return ast.BlockStatement(token=tok, statements=statements)

    def current_precedence(self) -> Precedence:
        return Precedence.get(self.current_token.type_, Precedence.LOWEST)

    def peek_precedence(self) -> Precedence:
        return Precedence.get(self.peek_token.type_, Precedence.LOWEST)
