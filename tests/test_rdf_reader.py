from .rdf_reader import EuParlRDFReader

target_documents = [
    {
        'speaker': 'Hamlet, Prince of Denmark',
        'party': 'HAMLET',
        'speech': "HAMLET \n Whither wilt thou lead me? Speak, I\'ll go no further."
    },
]


def test_rdf_number_documents():
    reader = EuParlRDFReader()
    docs = reader.documents()
    assert len(list(docs)) == 10


def test_rdf_document_content():
    reader = EuParlRDFReader()
    docs = reader.documents()
    for doc, target in zip(docs, target_documents):
        assert doc == target
