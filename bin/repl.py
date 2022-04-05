from monkey.lexer import Lexer
from monkey.token import TokenType


def repl() -> None:
    while True:
        line = input(">> ")
        lexer = Lexer(line)
        while (tok := lexer.next_token()).type_ != TokenType.EOF:
            print(tok)


if __name__ == "__main__":
    repl()
