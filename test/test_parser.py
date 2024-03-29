import pytest

from monkey.ast import (
    LetStatement,
    ReturnStatement,
    Program,
    Identifier,
    ExpressionStatement,
    IntegerLiteral,
    PrefixExpression,
    InfixExpression,
    Boolean,
    IfExpression,
    BlockStatement,
)
from monkey.lexer import Lexer
from monkey.parser import Parser
from monkey.token import Token, TokenType


@pytest.mark.parametrize(
    "input,length",
    [
        (
            """
let x = 5;
let y = 10;
let foobar = 838383;
""",
            3,
        ),
    ],
)
def test_parse_program(input, length):
    lexer = Lexer(input)
    parser = Parser(lexer)

    program = parser.parse_program()
    assert not parser.errors
    assert len(program.statements) == length


@pytest.mark.xfail
@pytest.mark.parametrize(
    "input,errors",
    [
        (
            """
let x 5;
let = 10;
let 838383;
""",
            [
                "Expected next token to be ASSIGN, got INT instead",
                "Expected next token to be IDENT, got ASSIGN instead",
                "Expected next token to be IDENT, got INT instead",
            ],
        ),
    ],
)
def test_parse_program_errors(input, errors):
    lexer = Lexer(input)
    parser = Parser(lexer)

    parser.parse_program()
    assert parser.errors == errors


@pytest.mark.parametrize(
    "input,name,value",
    [
        ("let x = 5;", "x", "5"),
        ("let y = 10;", "y", "10"),
        ("let foobar = 838383;", "foobar", "838383"),
    ],
)
def test_let_statements(input, name, value):
    lexer = Lexer(input)
    parser = Parser(lexer)

    program = parser.parse_program()
    assert not parser.errors
    assert len(program.statements) == 1

    statement = program.statements[0]
    assert isinstance(statement, LetStatement)
    assert statement.name.token_literal() == name
    assert statement.value.token_literal() == value


@pytest.mark.parametrize(
    "input,value",
    [
        ("return 5;", "5"),
        ("return 10;", "10"),
        ("return 993322;", "993322"),
    ],
)
def test_return_statements(input, value):
    lexer = Lexer(input)
    parser = Parser(lexer)

    program = parser.parse_program()
    assert not parser.errors
    assert len(program.statements) == 1

    statement = program.statements[0]
    assert isinstance(statement, ReturnStatement)
    assert statement.return_value.token_literal() == value


def test_string():
    program = Program(
        statements=[
            LetStatement(
                token=Token(type_=TokenType.LET, literal="let"),
                name=Identifier(
                    Token(type_=TokenType.IDENT, literal="myVar"), value="myVar"
                ),
                value=Identifier(
                    Token(type_=TokenType.IDENT, literal="anotherVar"),
                    value="anotherVar",
                ),
            )
        ]
    )
    assert program.string() == "let myVar = anotherVar;"


def test_identifier_expression():
    input = "foobar;"
    lexer = Lexer(input)
    parser = Parser(lexer)

    program = parser.parse_program()
    assert not parser.errors
    ident = Token(type_=TokenType.IDENT, literal="foobar")
    assert program.statements == [
        ExpressionStatement(
            token=ident, expression=Identifier(token=ident, value=ident.literal)
        )
    ]


@pytest.mark.parametrize(
    "input,expression",
    [
        ("5;", IntegerLiteral(token=Token(type_=TokenType.INT, literal="5"), value=5)),
        (
            "true;",
            Boolean(token=Token(type_=TokenType.TRUE, literal="true"), value=True),
        ),
        (
            "false;",
            Boolean(token=Token(type_=TokenType.FALSE, literal="false"), value=False),
        ),
    ],
)
def test_literal_expression(input, expression):
    lexer = Lexer(input)
    parser = Parser(lexer)

    program = parser.parse_program()
    assert not parser.errors
    assert len(program.statements) == 1
    statement = program.statements[0]
    assert isinstance(statement, ExpressionStatement)
    assert statement.expression == expression


@pytest.mark.parametrize(
    "input,expression",
    [
        (
            "!5;",
            PrefixExpression(
                token=Token(type_=TokenType.BANG, literal="!"),
                operator="!",
                right=IntegerLiteral(
                    token=Token(type_=TokenType.INT, literal="5"), value=5
                ),
            ),
        ),
        (
            "-15;",
            PrefixExpression(
                token=Token(type_=TokenType.MINUS, literal="-"),
                operator="-",
                right=IntegerLiteral(
                    token=Token(type_=TokenType.INT, literal="15"), value=15
                ),
            ),
        ),
    ],
)
def test_parsing_prefix_expressions(input, expression):
    lexer = Lexer(input)
    parser = Parser(lexer)

    program = parser.parse_program()
    assert not parser.errors
    assert program.statements == [
        ExpressionStatement(token=expression.token, expression=expression)
    ]


@pytest.mark.parametrize(
    "input,expression",
    [
        (
            "5 + 5;",
            InfixExpression(
                token=Token(type_=TokenType.PLUS, literal="+"),
                left=IntegerLiteral(
                    token=Token(type_=TokenType.INT, literal="5"), value=5
                ),
                operator="+",
                right=IntegerLiteral(
                    token=Token(type_=TokenType.INT, literal="5"), value=5
                ),
            ),
        ),
        (
            "5 - 5;",
            InfixExpression(
                token=Token(type_=TokenType.MINUS, literal="-"),
                left=IntegerLiteral(
                    token=Token(type_=TokenType.INT, literal="5"), value=5
                ),
                operator="-",
                right=IntegerLiteral(
                    token=Token(type_=TokenType.INT, literal="5"), value=5
                ),
            ),
        ),
        (
            "5 * 5;",
            InfixExpression(
                token=Token(type_=TokenType.ASTERISK, literal="*"),
                left=IntegerLiteral(
                    token=Token(type_=TokenType.INT, literal="5"), value=5
                ),
                operator="*",
                right=IntegerLiteral(
                    token=Token(type_=TokenType.INT, literal="5"), value=5
                ),
            ),
        ),
        (
            "5 / 5;",
            InfixExpression(
                token=Token(type_=TokenType.SLASH, literal="/"),
                left=IntegerLiteral(
                    token=Token(type_=TokenType.INT, literal="5"), value=5
                ),
                operator="/",
                right=IntegerLiteral(
                    token=Token(type_=TokenType.INT, literal="5"), value=5
                ),
            ),
        ),
        (
            "5 > 5;",
            InfixExpression(
                token=Token(type_=TokenType.GT, literal=">"),
                left=IntegerLiteral(
                    token=Token(type_=TokenType.INT, literal="5"), value=5
                ),
                operator=">",
                right=IntegerLiteral(
                    token=Token(type_=TokenType.INT, literal="5"), value=5
                ),
            ),
        ),
        (
            "5 < 5;",
            InfixExpression(
                token=Token(type_=TokenType.LT, literal="<"),
                left=IntegerLiteral(
                    token=Token(type_=TokenType.INT, literal="5"), value=5
                ),
                operator="<",
                right=IntegerLiteral(
                    token=Token(type_=TokenType.INT, literal="5"), value=5
                ),
            ),
        ),
        (
            "5 == 5;",
            InfixExpression(
                token=Token(type_=TokenType.EQ, literal="=="),
                left=IntegerLiteral(
                    token=Token(type_=TokenType.INT, literal="5"), value=5
                ),
                operator="==",
                right=IntegerLiteral(
                    token=Token(type_=TokenType.INT, literal="5"), value=5
                ),
            ),
        ),
        (
            "5 != 5;",
            InfixExpression(
                token=Token(type_=TokenType.NOT_EQ, literal="!="),
                left=IntegerLiteral(
                    token=Token(type_=TokenType.INT, literal="5"), value=5
                ),
                operator="!=",
                right=IntegerLiteral(
                    token=Token(type_=TokenType.INT, literal="5"), value=5
                ),
            ),
        ),
        (
            "true == true;",
            InfixExpression(
                token=Token(type_=TokenType.EQ, literal="=="),
                left=Boolean(
                    token=Token(type_=TokenType.TRUE, literal="true"), value=True
                ),
                operator="==",
                right=Boolean(
                    token=Token(type_=TokenType.TRUE, literal="true"), value=True
                ),
            ),
        ),
        (
            "true != false;",
            InfixExpression(
                token=Token(type_=TokenType.NOT_EQ, literal="!="),
                left=Boolean(
                    token=Token(type_=TokenType.TRUE, literal="true"), value=True
                ),
                operator="!=",
                right=Boolean(
                    token=Token(type_=TokenType.FALSE, literal="false"), value=False
                ),
            ),
        ),
        (
            "false == false;",
            InfixExpression(
                token=Token(type_=TokenType.EQ, literal="=="),
                left=Boolean(
                    token=Token(type_=TokenType.FALSE, literal="false"), value=False
                ),
                operator="==",
                right=Boolean(
                    token=Token(type_=TokenType.FALSE, literal="false"), value=False
                ),
            ),
        ),
    ],
)
def test_parsing_infix_expressions(input, expression):
    lexer = Lexer(input)
    parser = Parser(lexer)

    program = parser.parse_program()
    assert not parser.errors
    assert len(program.statements) == 1
    statement = program.statements[0]
    assert isinstance(statement, ExpressionStatement)
    assert statement.expression == expression


@pytest.mark.parametrize(
    "input,expected",
    [
        ("true", "true"),
        ("false", "false"),
        ("3 > 5 == false", "((3 > 5) == false)"),
        ("3 < 5 == true", "((3 < 5) == true)"),
        ("1 + (2 + 3) + 4", "((1 + (2 + 3)) + 4)"),
        ("(5 + 5) * 2", "((5 + 5) * 2)"),
        ("2 / (5 + 5)", "(2 / (5 + 5))"),
        ("-(5 + 5)", "(-(5 + 5))"),
        ("!(true == true)", "(!(true == true))"),
    ],
)
def test_operator_precedence_parsing(input, expected):
    lexer = Lexer(input)
    parser = Parser(lexer)

    program = parser.parse_program()
    assert not parser.errors
    assert len(program.statements) == 1
    assert program.statements[0].string() == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        (
            "if (x < y) { x }",
            IfExpression(
                token=Token(type_=TokenType.IF, literal="if"),
                condition=InfixExpression(
                    token=Token(type_=TokenType.LT, literal="<"),
                    left=Identifier(
                        token=Token(type_=TokenType.IDENT, literal="x"), value="x"
                    ),
                    operator="<",
                    right=Identifier(
                        token=Token(type_=TokenType.IDENT, literal="y"), value="y"
                    ),
                ),
                consequence=BlockStatement(
                    token=Token(type_=TokenType.LBRACE, literal="{"),
                    statements=[
                        ExpressionStatement(
                            token=Token(type_=TokenType.IDENT, literal="x"),
                            expression=Identifier(
                                token=Token(type_=TokenType.IDENT, literal="x"),
                                value="x",
                            ),
                        )
                    ],
                ),
                alternative=None,
            ),
        ),
        (
            "if (x < y) { x } else { y }",
            IfExpression(
                token=Token(type_=TokenType.IF, literal="if"),
                condition=InfixExpression(
                    token=Token(type_=TokenType.LT, literal="<"),
                    left=Identifier(
                        token=Token(type_=TokenType.IDENT, literal="x"), value="x"
                    ),
                    operator="<",
                    right=Identifier(
                        token=Token(type_=TokenType.IDENT, literal="y"), value="y"
                    ),
                ),
                consequence=BlockStatement(
                    token=Token(type_=TokenType.LBRACE, literal="{"),
                    statements=[
                        ExpressionStatement(
                            token=Token(type_=TokenType.IDENT, literal="x"),
                            expression=Identifier(
                                token=Token(type_=TokenType.IDENT, literal="x"),
                                value="x",
                            ),
                        )
                    ],
                ),
                alternative=BlockStatement(
                    token=Token(type_=TokenType.LBRACE, literal="{"),
                    statements=[
                        ExpressionStatement(
                            token=Token(type_=TokenType.IDENT, literal="y"),
                            expression=Identifier(
                                token=Token(type_=TokenType.IDENT, literal="y"),
                                value="y",
                            ),
                        )
                    ],
                ),
            ),
        ),
    ],
)
def test_if_expression(input, expected):
    lexer = Lexer(input)
    parser = Parser(lexer)

    program = parser.parse_program()
    assert not parser.errors
    statement = program.statements[0]
    assert isinstance(statement, ExpressionStatement)
    assert statement.expression == expected
