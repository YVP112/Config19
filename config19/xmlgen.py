from xml.etree.ElementTree import Element, ElementTree
from typing import Any, Mapping, Union
from pathlib import Path


class XmlGenerationError(Exception):
    pass


def _value_to_xml(parent: Element, key: str, value: Any) -> None:
    elem = Element(key)

    if isinstance(value, Mapping):
        # Вложенный словарь → вложенные элементы
        for k, v in value.items():
            _value_to_xml(elem, str(k), v)
    else:
        # Скаляры: строки, числа
        elem.text = str(value)

    parent.append(elem)


def config_to_xml_root(config: Any) -> Element:

    root = Element("config")

    if isinstance(config, Mapping):
        for key, value in config.items():
            _value_to_xml(root, str(key), value)
    else:
        _value_to_xml(root, "value", config)

    return root


def write_xml_file(config: Any, output_path: Union[str, Path]) -> None:
    root = config_to_xml_root(config)
    tree = ElementTree(root)
    output_path = Path(output_path)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)
