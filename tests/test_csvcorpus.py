import pytest

from .mock_csv_corpus import TestCSVReader
import os

here = os.path.abspath(os.path.dirname(__file__))


target_documents = [
    {
        'character': 'HAMLET',
        'lines': ["Whither wilt thou lead me? Speak, I\'ll go no further."]
    },
    {
        'character': 'GHOST',
        'lines': ["Mark me."]
    },
    {
        'character': 'HAMLET',
        'lines': ["I will."]
    },
    {
        'character': 'GHOST',
        'lines': [
            "My hour is almost come,",
            "When I to sulph\'rous and tormenting flames",
            "Must render up myself."
        ]
    },
    {
        'character': 'HAMLET',
        'lines': ["Alas, poor ghost!"]
    },
    {
        'character': 'GHOST',
        'lines': [
            "Pity me not, but lend thy serious hearing",
            "To what I shall unfold."
        ]
    },
    {
        'character': 'HAMLET',
        'lines': ["Speak, I am bound to hear."]
    },
]


def test_csv():
    corpus = TestCSVReader()

    sources = list(corpus.sources())
    assert len(sources) == 1

    docs = corpus.source2dicts(sources[0])
    for doc, target in zip(docs, target_documents):
        assert doc == target

def test_csv_supported_source_types():
    corpus = TestCSVReader()
    source = next(corpus.sources())
    assert isinstance(source, str)

    # should work with a path as the source
    list(corpus.source2dicts(source))

    # should work with a path + metadata as the source
    source_with_metadata = source, {}
    list(corpus.source2dicts(source_with_metadata))
