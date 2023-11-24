from readers.csv import CSVReader
from readers.core import Field
from extractors.extract import CSV
import os

here = os.path.abspath(os.path.dirname(__file__))


class TestCSVReader(CSVReader):
    """Example CSV corpus class for testing"""

    data_directory = os.path.join(here, 'csv_example')
    field_entry = 'character'

    def sources(self, **kwargs):
        for filename in os.listdir(self.data_directory):
            full_path = os.path.join(self.data_directory, filename)
            yield full_path, {
                'filename': filename
            }

    fields = [
        Field(
            name='character',
            extractor=CSV(field='character')
        ),
        Field(
            name='lines',
            extractor=CSV(
                field='line',
                multiple=True,
            )
        )
    ]
