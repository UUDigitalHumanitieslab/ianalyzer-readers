from tests.json.json_reader import JSONTestReader

expected = [
    {
        'act': 'ACT I',
        'scene': 'SCENE I.  A desert place.',
        'stage_direction': 'Thunder and lightning. Enter three Witches\nExeunt',
        'character': 'First Witch',
        'lines': 'When shall we three meet again\nIn thunder, lightning, or in rain?',
    },
    *[{}] * 8,
    {
        'act': 'ACT I',
        'scene': 'SCENE I.  A desert place.',
        'stage_direction': 'Thunder and lightning. Enter three Witches\nExeunt',
        'character': 'ALL',
        'lines': "Fair is foul, and foul is fair:\nHover through the fog and filthy air.",
    },
]


def test_json_read_file():
    reader = JSONTestReader()
    docs = list(reader.documents())
    assert len(docs) == len(expected)
    _assert_matches(expected[0], docs[0])
    _assert_matches(expected[-1], docs[-1])


def _assert_matches(target: dict, doc: dict):
    assert len(target.keys()) == len(doc.keys())
    for key in target.keys():
        assert doc.get(key) == target.get(key)
