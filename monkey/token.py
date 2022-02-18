import dataclasses
from enum import Enum, auto


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class TokenType(AutoName):
    ILLEGAL = auto()
    EOF = auto()

    IDENT = auto()
    INT = auto()

    ASSIGN = '='
    PLUS = '+'

    COMMA = ','
    SEMICOLON = ';'

    LPAREN = '('
    RPAREN = ')'
    LBRACE = '{'
    RBRACE = '}'

    FUNCTION = auto()
    LET = auto()


@dataclasses.dataclass
class Token:
    type_: TokenType
    literal: str
