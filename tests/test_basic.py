import textwrap
from config19.parser import parse_config_text
from config19.xmlgen import config_to_xml_root


def test_simple_dict():
    src = textwrap.dedent("""
        @{
            NAME = "demo";
            COUNT = 3;
        }
    """)

    result = parse_config_text(src)
    cfg = result.config

    assert cfg["NAME"] == "demo"
    assert cfg["COUNT"] == 3

    xml = config_to_xml_root(cfg)
    tags = [child.tag for child in xml]
    assert "NAME" in tags
    assert "COUNT" in tags


def test_constants():
    src = textwrap.dedent("""
        X is 10;
        Y is 5;

        @{
            SUM = !(X + Y);
            MUL = !(X * Y);
            MOD = !(mod(X, Y));
        }
    """)

    result = parse_config_text(src)
    cfg = result.config

    assert cfg["SUM"] == 15
    assert cfg["MUL"] == 50
    assert cfg["MOD"] == 0
