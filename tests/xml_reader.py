import os

from ianalyzer_readers.readers.xml import XMLReader
from ianalyzer_readers.readers.core import Field
from ianalyzer_readers.extract import XML

here = os.path.abspath(os.path.dirname(__file__))

class HamletXMLReader(XMLReader):
    """
    Example XML reader for testing
    """

    data_directory = os.path.join(here, 'xml_example')

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