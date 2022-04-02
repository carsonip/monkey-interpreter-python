import abc
import dataclasses

from monkey import token


class Node(abc.ABC):
    @abc.abstractmethod
    def token_literal(self) -> str:
        pass

    @abc.abstractmethod
    def string(self) -> str:
        pass

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return NotImplemented
        return self.__dict__ == other.__dict__


class Statement(Node, abc.ABC):
    pass


class Expression(Node, abc.ABC):
    pass


@dataclasses.dataclass
class Program(Node):
    statements: list[Statement] = dataclasses.field(default_factory=lambda: [])

    def token_literal(self) -> str:
        return self.statements[0].token_literal() if self.statements else ""

    def string(self) -> str:
        return "\n".join(statement.string() for statement in self.statements)


@dataclasses.dataclass
class Identifier(Expression):
    token: token.Token
    value: str

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        return self.value


@dataclasses.dataclass
class LetStatement(Statement):
    token: token.Token
    name: Identifier
    value: Expression

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        return f"{self.token.literal} {self.name.string()} = {self.value.string()};"


@dataclasses.dataclass
class ReturnStatement(Statement):
    token: token.Token
    return_value: Expression

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        return f"{self.token.literal} {self.return_value.string()};"


@dataclasses.dataclass
class ExpressionStatement(Statement):
    token: token.Token
    expression: Expression

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        return self.expression.string()


@dataclasses.dataclass
class IntegerLiteral(Expression):
    token: token.Token
    value: int

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        return f"{self.value}"


@dataclasses.dataclass
class PrefixExpression(Expression):
    token: token.Token
    operator: str
    right: Expression

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        return f"({self.operator}{self.right.string()})"


@dataclasses.dataclass
class InfixExpression(Expression):
    token: token.Token
    left: Expression
    operator: str
    right: Expression

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        return f"({self.left.string()} {self.operator} {self.right.string()})"


@dataclasses.dataclass
class Boolean(Expression):
    token: token.Token
    value: bool

    def token_literal(self) -> str:
        return self.token.literal

    def string(self) -> str:
        return str(self.value).lower()
