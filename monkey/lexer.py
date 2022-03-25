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

        self._skip_whitespace()

        if self.pos >= len(self.source):
            return Token(TokenType.EOF, '')

        char = self.source[self.pos]
        if char == '=':
            self.pos += 1
            return Token(TokenType.ASSIGN, char)
        elif (token_type := TokenType.get(char)) is not None:
            self.pos += 1
            return Token(token_type, char)
        elif char.isalpha():
            literal = self._read_identifier()
            return Token(_lookup_ident(literal), literal)
        elif char.isnumeric():
            literal = self._read_number()
            return Token(TokenType.INT, literal)
        else:
            self.pos += 1
            return Token(TokenType.ILLEGAL, char)

    def _read_identifier(self):
        pos = self.pos
        while self.pos < len(self.source) and _is_letter(self.source[self.pos]):
            self.pos += 1
        return self.source[pos:self.pos]

    def _read_number(self):
        pos = self.pos
        while self.pos < len(self.source) and self.source[self.pos].isnumeric():
            self.pos += 1
        return self.source[pos:self.pos]

    def _skip_whitespace(self):
        while self.pos < len(self.source) and self.source[self.pos] in (' ', '\t', '\n'):
            self.pos += 1


KEYWORDS: Dict[str, TokenType] = {
    'let': TokenType.LET,
    'fn': TokenType.FUNCTION,
    'true': TokenType.TRUE,
    'false': TokenType.FALSE,
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'return': TokenType.RETURN,
}


def _lookup_ident(ident: str) -> TokenType:
    return KEYWORDS.get(ident, TokenType.IDENT)


def _is_letter(char: str) -> bool:
    return char.isalnum() or char in ('_',)
