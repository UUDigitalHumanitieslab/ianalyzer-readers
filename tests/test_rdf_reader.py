from .rdf_reader import TestRDFReader

target_documents = [
    {
        'character': 'HAMLET',
        'lines': ["Whither wilt thou lead me? Speak, I\'ll go no further."],
        'opacity': 1.0
    },
    {
        'character': 'GHOST',
        'lines': ["Mark me."],
        'opacity': 0.3
    },
    {
        'character': 'HAMLET',
        'lines': ["I will."],
        'opacity': 1.0
    },
    {
        'character': 'GHOST',
        'lines': [
            "My hour is almost come,",
            "When I to sulph\'rous and tormenting flames",
            "Must render up myself."
        ],
        'opacity': 0.3
    },
    {
        'character': 'HAMLET',
        'lines': ["Alas, poor ghost!"],
        'opacity': 1.0,
    },
    {
        'character': 'GHOST',
        'lines': [
            "Pity me not, but lend thy serious hearing",
            "To what I shall unfold."
        ],
        'opacity': 0.3
    },
    {
        'character': 'HAMLET',
        'lines': ["Speak, I am bound to hear."],
        'opacity': 1.0
    },
]

def test_rdf_number_documents():
    reader = TestRDFReader()
    docs = reader.documents()
    assert len(list(docs)) == 7


def test_rdf_document_content():
    reader = TestRDFReader()
    docs = reader.documents()
    for doc, target in zip(docs, target_documents):
        assert len(target.keys()) == len(doc.keys())
        for key in target.keys():
            assert doc.get(key) == target.get(key)
