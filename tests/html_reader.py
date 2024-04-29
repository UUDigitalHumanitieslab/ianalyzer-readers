import os

from ianalyzer_readers.readers.html import HTMLReader
from ianalyzer_readers.readers.core import Field
from ianalyzer_readers.extract import XML
from ianalyzer_readers.utils import XMLTag, CurrentTag

here = os.path.abspath(os.path.dirname(__file__))

class HamletHTMLReader(HTMLReader):
    """
    Example XML reader for testing
    """

    data_directory = os.path.join(here, 'html_example')

    tag_toplevel = XMLTag('body')
    tag_entry = XMLTag('p')

    def sources(self, **kwargs):
        for filename in os.listdir(self.data_directory):
            full_path = os.path.join(self.data_directory, filename)
            yield full_path, {
                'filename': filename
            }

    title = Field(
        'title',
        XML(XMLTag('h1'), toplevel=True)
    )
    character = Field(
        'character',
        XML(XMLTag('b'))
    )
    lines = Field(
        'lines',
        XML(CurrentTag(), flatten=True),
    )

    fields = [title, character, lines]