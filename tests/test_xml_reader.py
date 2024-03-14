from .xml_reader import HamletXMLReader

target_documents = [
    {
        'title': 'Hamlet',
        'character': 'HAMLET',
        'lines': "Whither wilt thou lead me? Speak, I\'ll go no further."
    },
    {
        'title': 'Hamlet',
        'character': 'GHOST',
        'lines': "Mark me."
    },
    {
        'title': 'Hamlet',
        'character': 'HAMLET',
        'lines': "I will."
    },
    {
        'title': 'Hamlet',
        'character': 'GHOST',
        'lines': 
            "My hour is almost come,\n"
            "When I to sulph\'rous and tormenting flames\n"
            "Must render up myself."
    },
    {
        'title': 'Hamlet',
        'character': 'HAMLET',
        'lines': "Alas, poor ghost!"
    },
    {
        'title': 'Hamlet',
        'character': 'GHOST',
        'lines': 
            "Pity me not, but lend thy serious hearing\n"
            "To what I shall unfold."
    },
    {
        'title': 'Hamlet',
        'character': 'HAMLET',
        'lines': "Speak, I am bound to hear."
    },
]


def test_xml():
    reader = HamletXMLReader()
    docs = reader.documents()

    for doc, target in zip(docs, target_documents):
        assert doc == target
