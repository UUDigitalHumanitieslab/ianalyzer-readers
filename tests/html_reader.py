import os

from ianalyzer_readers.readers.html import HTMLReader
from ianalyzer_readers.readers.core import Field
from ianalyzer_readers.extract import XML

here = os.path.abspath(os.path.dirname(__file__))

class HamletHTMLReader(HTMLReader):
    """
    Example XML reader for testing
    """

    data_directory = os.path.join(here, 'html_example')

    tag_toplevel = 'body'
    tag_entry = 'p'

    def sources(self, **kwargs):
        for filename in os.listdir(self.data_directory):
            full_path = os.path.join(self.data_directory, filename)
            yield full_path, {
                'filename': filename
            }

    title = Field(
        'title',
        XML('h1', toplevel=True)
    )
    character = Field(
        'character',
        XML('b')
    )
    lines = Field(
        'lines',
        XML(None, flatten=True),
    )

    fields = [title, character, lines]