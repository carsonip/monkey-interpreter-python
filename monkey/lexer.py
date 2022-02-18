from typing import Dict

from monkey.token import Token, TokenType


class Lexer:
    source: str
    pos: int

    def __init__(self, source: str) -> None:
        self.source = source
        self.pos = 0

    def next_token(self) -> Token:
        if self.pos >= len(self.source):
            return Token(TokenType.EOF, '')
        while self.pos < len(self.source) and self.source[self.pos] in (' ', '\t', '\n'):
            self.pos += 1
        if self.pos >= len(self.source):
            return Token(TokenType.EOF, '')

        char = self.source[self.pos]
        if char == '=':
            self.pos += 1
            return Token(TokenType.ASSIGN, char)
        elif char == '+':
            self.pos += 1
            return Token(TokenType.PLUS, char)
        elif char == ',':
            self.pos += 1
            return Token(TokenType.COMMA, char)
        elif char == ';':
            self.pos += 1
            return Token(TokenType.SEMICOLON, char)
        elif char == '(':
            self.pos += 1
            return Token(TokenType.LPAREN, char)
        elif char == ')':
            self.pos += 1
            return Token(TokenType.RPAREN, char)
        elif char == '{':
            self.pos += 1
            return Token(TokenType.LBRACE, char)
        elif char == '}':
            self.pos += 1
            return Token(TokenType.RBRACE, char)
        elif char.isalnum():
            literal = self._read_identifier()
            return Token(_lookup_ident(literal), literal)
        return Token(TokenType.ILLEGAL, '')

    def _read_identifier(self):
        pos = self.pos
        while self.pos < len(self.source) and self.source[self.pos].isalnum():
            self.pos += 1
        return self.source[pos:self.pos]


KEYWORDS: Dict[str, TokenType] = {
    'let': TokenType.LET,
    'fn': TokenType.FUNCTION,
}


def _lookup_ident(ident: str) -> TokenType:
    return KEYWORDS.get(ident, TokenType.IDENT)
