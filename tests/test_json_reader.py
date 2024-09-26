from tests.json.json_reader import JSONTestReader

expected = [
    {
        "act": "ACT I",
        "scene": "SCENE I.  A desert place.",
        "character": "First Witch",
        "lines": [
            "When shall we three meet again",
            "In thunder, lightning, or in rain?",
        ],
    }
]


def test_json_read_file():
    reader = JSONTestReader()
    docs = reader.documents()
    for doc, target in zip(docs, expected):
        assert len(target.keys()) == len(doc.keys())
        for key in target.keys():
            assert doc.get(key) == target.get(key)
