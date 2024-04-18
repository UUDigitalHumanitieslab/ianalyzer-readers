import os

from ianalyzer_readers.readers.turtle import RDFReader
from ianalyzer_readers.readers.core import Field
from ianalyzer_readers.extract import RDF

here = os.path.abspath(os.path.dirname(__file__))


class EuParlRDFReader(RDFReader):
    """
    Example XML reader for testing
    """

    data_directory = os.path.join(here, 'ttl_example')

    def sources(self, **kwargs):
        for filename in os.listdir(self.data_directory):
            full_path = os.path.join(self.data_directory, filename)
            yield full_path, {
                'filename': filename
            }

    speaker = Field(
        'speaker',
        RDF('speaker')
    )
    party = Field(
        'party',
        RDF('party')
    )
    speech = Field(
        'speech',
        RDF('speech')
    )

    fields = [speaker, party, speech]
