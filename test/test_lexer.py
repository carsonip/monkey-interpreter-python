import pytest

from monkey.lexer import Lexer
from monkey.token import Token, TokenType


@pytest.mark.parametrize('input,expected_token', [
    ('=', Token(TokenType.ASSIGN, '=')),
    ('+', Token(TokenType.PLUS, '+')),
    (',', Token(TokenType.COMMA, ',')),
    (';', Token(TokenType.SEMICOLON, ';')),
    ('(', Token(TokenType.LPAREN, '(')),
    (')', Token(TokenType.RPAREN, ')')),
    ('{', Token(TokenType.LBRACE, '{')),
    ('}', Token(TokenType.RBRACE, '}')),
    ('let', Token(TokenType.LET, 'let')),
    ('letter', Token(TokenType.IDENT, 'letter')),
    ('fn', Token(TokenType.FUNCTION, 'fn')),
    ('fnn', Token(TokenType.IDENT, 'fnn')),
    ('', Token(TokenType.EOF, '')),
])
def test_next_token(input, expected_token):
    lexer = Lexer(input)
    assert lexer.next_token() == expected_token


def test_next_token_long():
    input = """let five = 5;
let ten = 10;

let add = fn(x, y) {
  x + y;
}

let result = add(five, ten);
"""
    expected_tokens = [
        Token(TokenType.LET, 'let'),
        Token(TokenType.IDENT, 'five'),
        Token(TokenType.ASSIGN, '='),
        Token(TokenType.IDENT, '5'),
        Token(TokenType.SEMICOLON, ';'),
        Token(TokenType.LET, 'let'),
        Token(TokenType.IDENT, 'ten'),
        Token(TokenType.ASSIGN, '='),
        Token(TokenType.IDENT, '10'),
        Token(TokenType.SEMICOLON, ';'),
        Token(TokenType.LET, 'let'),
        Token(TokenType.IDENT, 'add'),
        Token(TokenType.ASSIGN, '='),
        Token(TokenType.FUNCTION, 'fn'),
        Token(TokenType.LPAREN, '('),
        Token(TokenType.IDENT, 'x'),
        Token(TokenType.COMMA, ','),
        Token(TokenType.IDENT, 'y'),
        Token(TokenType.RPAREN, ')'),
        Token(TokenType.LBRACE, '{'),
        Token(TokenType.IDENT, 'x'),
        Token(TokenType.PLUS, '+'),
        Token(TokenType.IDENT, 'y'),
        Token(TokenType.SEMICOLON, ';'),
        Token(TokenType.RBRACE, '}'),
        Token(TokenType.LET, 'let'),
        Token(TokenType.IDENT, 'result'),
        Token(TokenType.ASSIGN, '='),
        Token(TokenType.IDENT, 'add'),
        Token(TokenType.LPAREN, '('),
        Token(TokenType.IDENT, 'five'),
        Token(TokenType.COMMA, ','),
        Token(TokenType.IDENT, 'ten'),
        Token(TokenType.RPAREN, ')'),
        Token(TokenType.SEMICOLON, ';'),
        Token(TokenType.EOF, ''),
    ]
    lexer = Lexer(input)
    actual = []
    while True:
        token = lexer.next_token()
        actual.append(token)
        if token.type_ == TokenType.EOF:
            break
    assert actual == expected_tokens
