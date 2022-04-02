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
            return Token(TokenType.EOF, "")

        self._skip_whitespace()

        if self.pos >= len(self.source):
            return Token(TokenType.EOF, "")

        char = self.source[self.pos]
        if char == "=":
            self.pos += 1
            if self.peek_char() == "=":
                self.pos += 1
                return Token(TokenType.EQ, "==")
            else:
                return Token(TokenType.ASSIGN, char)
        elif char == "!":
            self.pos += 1
            if self.peek_char() == "=":
                self.pos += 1
                return Token(TokenType.NOT_EQ, "!=")
            else:
                return Token(TokenType.BANG, char)
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

    def _read_identifier(self) -> str:
        pos = self.pos
        while _is_letter(self.peek_char()):
            self.pos += 1
        return self.source[pos : self.pos]

    def _read_number(self) -> str:
        pos = self.pos
        while self.peek_char().isnumeric():
            self.pos += 1
        return self.source[pos : self.pos]

    def _skip_whitespace(self) -> None:
        while self.peek_char() in (" ", "\t", "\n"):
            self.pos += 1

    def peek_char(self) -> str:
        return self.source[self.pos] if self.pos < len(self.source) else ""


KEYWORDS: Dict[str, TokenType] = {
    "let": TokenType.LET,
    "fn": TokenType.FUNCTION,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "return": TokenType.RETURN,
}


def _lookup_ident(ident: str) -> TokenType:
    return KEYWORDS.get(ident, TokenType.IDENT)


def _is_letter(char: str) -> bool:
    return char.isalnum() or char in ("_",)
