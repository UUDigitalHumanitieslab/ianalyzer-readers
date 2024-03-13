from .html_reader import HamletHTMLReader

target_documents = [
    {
        'title': 'Hamlet, Prince of Denmark',
        'character': 'HAMLET',
        'lines': "HAMLET \n Whither wilt thou lead me? Speak, I\'ll go no further."
    },
    {
        'title': 'Hamlet, Prince of Denmark',
        'character': 'GHOST',
        'lines': "GHOST \n Mark me."
    },
    {
        'title': 'Hamlet, Prince of Denmark',
        'character': 'HAMLET',
        'lines': "HAMLET \n I will."
    },
    {
        'title': 'Hamlet, Prince of Denmark',
        'character': 'GHOST',
        'lines': 
            "GHOST \n "
            "My hour is almost come,\n "
            "When I to sulph\'rous and tormenting flames\n "
            "Must render up myself."
    },
    {
        'title': 'Hamlet, Prince of Denmark',
        'character': 'HAMLET',
        'lines': "HAMLET \n Alas, poor ghost!"
    },
    {
        'title': 'Hamlet, Prince of Denmark',
        'character': 'GHOST',
        'lines': 
            "GHOST \n "
            "Pity me not, but lend thy serious hearing\n "
            "To what I shall unfold."
    },
    {
        'title': 'Hamlet, Prince of Denmark',
        'character': 'HAMLET',
        'lines': "HAMLET \n Speak, I am bound to hear."
    },
]


def test_html():
    reader = HamletHTMLReader()
    docs = reader.documents()

    for doc, target in zip(docs, target_documents):
        assert doc == target
