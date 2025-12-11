from dataclasses import dataclass
from typing import Any, Dict, Optional, Union
from pathlib import Path

from lark import Lark, Transformer, v_args, UnexpectedInput

class ConfigError(Exception):
    pass


GRAMMAR_PATH = Path(__file__).with_name("grammar.lark")


def load_grammar() -> str:
    return GRAMMAR_PATH.read_text(encoding="utf-8")


def create_parser() -> Lark:
    return Lark(load_grammar(), start="start", parser="lalr")


@dataclass
class ProgramResult:
    consts: Dict[str, Any]
    config: Any


@v_args(inline=True)
class ConfigTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self.consts: Dict[str, Any] = {}
        self.config: Optional[Any] = None

    def NAME(self, token):
        return str(token)

    def NUMBER(self, token):
        text = str(token)
        try:
            return int(text)
        except ValueError:
            return float(text)

    def STRING(self, token):
        text = str(token)
        # убираем кавычки, обрабатываем escape
        return bytes(text[1:-1], "utf-8").decode("unicode_escape")

    def const_decl(self, name, value):
        if name in self.consts:
            raise ConfigError(f"Повторная константа: {name}")
        self.consts[name] = value
        return None

    def top_value(self, value):
        self.config = value
        return value

    def dict(self, *pairs):
        d = {}
        for k, v in pairs:
            if k in d:
                raise ConfigError(f"Повторяющийся ключ: {k}")
            d[k] = v
        return d

    def pair(self, name, value):
        return name, value

    def string_value(self, s):
        return s

    def number_value(self, n):
        return n

    def const_expr(self, expr_value):
        return expr_value

    def number_atom(self, n):
        return n

    def var(self, name):
        if name not in self.consts:
            raise ConfigError(f"Неизвестная константа: {name}")
        return self.consts[name]

    def mod_call(self, a, b):
        if b == 0:
            raise ConfigError("mod() деление на ноль")
        return a % b

    def group(self, expr):
        return expr

    # арифметические операции
    def add(self, a, b):
        return a + b

    def sub(self, a, b):
        return a - b

    def mul(self, a, b):
        return a * b

    def div(self, a, b):
        if b == 0:
            raise ConfigError("Деление на ноль")
        return a / b

    def neg(self, x):
        return -x

    def pos(self, x):
        return +x


def parse_config_text(text: str) -> ProgramResult:
    parser = create_parser()
    try:
        tree = parser.parse(text)
    except UnexpectedInput as e:
        raise ConfigError(f"Синтаксическая ошибка: {e}") from e

    transformer = ConfigTransformer()
    transformer.transform(tree)

    if transformer.config is None:
        raise ConfigError("Не найдено корневое значение (последний словарь).")

    return ProgramResult(consts=transformer.consts, config=transformer.config)


def parse_config_file(path: Union[str, Path]) -> ProgramResult:
    text = Path(path).read_text(encoding="utf-8")
    return parse_config_text(text)

