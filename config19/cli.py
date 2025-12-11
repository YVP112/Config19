import argparse
import sys
from pathlib import Path

from .parser import parse_config_file, ConfigError
from .xmlgen import write_xml_file


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Учебный конфигурационный язык (вариант 19) → XML"
    )

    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Путь к входному конфигурационному файлу"
    )

    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Путь к выходному XML"
    )

    args = parser.parse_args(argv)

    input_path = Path(args.input)
    output_path = Path(args.output)

    try:
        program = parse_config_file(input_path)
        write_xml_file(program.config, output_path)
    except ConfigError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Неожиданная ошибка: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
