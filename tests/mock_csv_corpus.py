from ianalyzer_readers.readers.csv import CSVReader
from ianalyzer_readers.readers.core import Field
from ianalyzer_readers.extract import CSV
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
            extractor=CSV(column='character')
        ),
        Field(
            name='lines',
            extractor=CSV(
                column='line',
                multiple=True,
            )
        )
    ]
