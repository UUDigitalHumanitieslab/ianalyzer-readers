from .ttl_reader import EuParlRDFReader

target_documents = [
    {
        'speaker': 'Hamlet, Prince of Denmark',
        'party': 'HAMLET',
        'speech': "HAMLET \n Whither wilt thou lead me? Speak, I\'ll go no further."
    },
]


def test_rdf():
    reader = EuParlRDFReader()
    docs = reader.documents()

    for doc, target in zip(docs, target_documents):
        assert doc == target
