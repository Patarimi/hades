from hades.parsers.raw import parse_raw


def test_parse_raw():
    df = parse_raw("./tests/test_parser/test_data/schem_test.out")
    assert len(df["time"]) == 508
