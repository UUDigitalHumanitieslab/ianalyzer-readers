from .xlsx_reader import HamletXLSXReader

target_documents = [
    {
        'character': 'HAMLET',
        'lines': "Whither wilt thou lead me? Speak, Iʼll go no further."
    },
    {
        'character': 'GHOST',
        'lines': "Mark me."
    },
    {
        'character': 'HAMLET',
        'lines': "I will."
    },
    {
        'character': 'GHOST',
        'lines': 
            "My hour is almost come,\n"
            "When I to sulphʼrous and tormenting flames\n"
            "Must render up myself."
    },
    {
        'character': 'HAMLET',
        'lines': "Alas, poor ghost!"
    },
    {
        'character': 'GHOST',
        'lines': 
            "Pity me not, but lend thy serious hearing\n"
            "To what I shall unfold."
    },
    {
        'character': 'HAMLET',
        'lines': "Speak, I am bound to hear."
    },
]


def test_xlsx():
    reader = HamletXLSXReader()
    docs = reader.documents()

    for doc, target in zip(docs, target_documents):
        assert doc == target
