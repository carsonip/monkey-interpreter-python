import sys

from monkey.lexer import Lexer
from monkey.token import TokenType


def prompt():
    print('>> ', end='')
    sys.stdout.flush()


def repl():
    prompt()
    for line in sys.stdin:
        lexer = Lexer(line)
        while (tok := lexer.next_token()).type_ != TokenType.EOF:
            print(tok)
        prompt()


if __name__ == '__main__':
    repl()
