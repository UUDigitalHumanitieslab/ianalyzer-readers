import os

from ianalyzer_readers.readers.xml import XMLReader
from ianalyzer_readers.readers.core import Field
from ianalyzer_readers.extract import XML

class HamletXMLReader(XMLReader):
    """
    Example XML reader for testing
    """

    data_directory = os.path.join(os.path.dirname(__file__), 'data')

    tag_toplevel = 'document'
    tag_entry = 'lines'

    def sources(self, **kwargs):
        for filename in os.listdir(self.data_directory):
            full_path = os.path.join(self.data_directory, filename)
            yield full_path, {
                'filename': filename
            }

    title = Field(
        'title',
        XML('title', toplevel=True, recursive=True)
    )
    character = Field(
        'character',
        XML(None, attribute='character')
    )
    lines = Field(
        'lines',
        XML('l', multiple=True, transform='\n'.join),
    )

    fields = [title, character, lines]

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


def test_xml_reader():
    reader = HamletXMLReader()
    docs = reader.documents()

    for doc, target in zip(docs, target_documents):
        assert doc == target
