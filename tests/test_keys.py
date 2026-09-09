from dj_collection_set_builder.keys import camelot_code, notation_bundle, open_key_code


def test_a_minor_is_8a_and_1m():
    assert camelot_code("A", "minor") == "8A"
    assert open_key_code("8A") == "1m"
    tonic, standard, camelot, open_key = notation_bundle("A", "minor")
    assert tonic == "A"
    assert standard == "A minor"
    assert camelot == "8A"
    assert open_key == "1m"


def test_c_major_is_8b():
    tonic, standard, camelot, open_key = notation_bundle("C", "major")
    assert standard == "C major"
    assert camelot == "8B"
    assert open_key == "1d"


def test_enharmonic_spellings_share_camelot():
    assert camelot_code("Db", "major") == camelot_code("C#", "major") == "3B"
    assert camelot_code("Bb", "minor") == camelot_code("A#", "minor") == "3A"
    assert camelot_code("G#", "minor") == "1A"


def test_open_key_wraps_from_1_and_12():
    assert open_key_code("1A") == "6m"
    assert open_key_code("7A") == "12m"
    assert open_key_code("12B") == "5d"
