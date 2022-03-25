import dataclasses
from enum import Enum, auto
from typing import Optional, Any, List


class AutoName(Enum):
    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: List[Any]) -> Any:
        return name


class TokenType(AutoName):
    ILLEGAL = auto()
    EOF = auto()

    IDENT = auto()
    INT = auto()

    ASSIGN = '='
    PLUS = '+'
    MINUS = '-'
    SLASH = '/'
    BANG = '!'
    ASTERISK = '*'

    LT = '<'
    GT = '>'

    EQ = '=='
    NOT_EQ = '!='

    COMMA = ','
    SEMICOLON = ';'

    LPAREN = '('
    RPAREN = ')'
    LBRACE = '{'
    RBRACE = '}'

    FUNCTION = auto()
    LET = auto()
    TRUE = auto()
    FALSE = auto()
    IF = auto()
    ELSE = auto()
    RETURN = auto()

    @classmethod
    def get(cls, val: str) -> Optional['TokenType']:
        return cls._value2member_map_.get(val, None)  # type: ignore


@dataclasses.dataclass
class Token:
    type_: TokenType
    literal: str
