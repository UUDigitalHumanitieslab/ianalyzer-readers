'''
Module for the CSV reader

Extraction is based on python's `csv` library.
'''

from .. import extract
from .core import Reader
import csv
import sys

import logging

logger = logging.getLogger()


class CSVReader(Reader):
    '''
    An CSVReader extracts data from comma separated value files.

    By default, the reader will extract one document per row, but you
    can also set `field_entry` to group grows.
    '''

    field_entry = None
    '''
    If applicable, the field that identifies entries. Subsequent rows with the same
    value for this field are treated as a single document. If left blank, each row
    is treated as a document.
    '''

    required_field = None
    '''
    Specifies a required field, for example the main content. Rows with
    an empty value for `required_field` will be skipped.
    '''

    delimiter = ','
    '''
    The delimiter for the CSV reader.
    '''

    skip_lines = 0
    '''
    Number of lines to skip before reading the header
    '''

    def source2dicts(self, source):
        '''
        Generate document dicts from a CSV file
        '''

        # make sure the field size is as big as the system permits
        csv.field_size_limit(sys.maxsize)
        self._reject_extractors(extract.XML, extract.FilterAttribute)

        if isinstance(source, str):
            filename = source
            metadata = {}
        if isinstance(source, bytes):
            raise NotImplementedError()
        else:
            filename, metadata = source

        with open(filename, 'r') as f:
            logger.info('Reading CSV file {}...'.format(filename))

            # skip first n lines
            for _ in range(self.skip_lines):
                next(f)

            reader = csv.DictReader(f, delimiter=self.delimiter)
            document_id = None
            rows = []
            index = 0
            for row in reader:
                is_new_document = True

                if self.required_field and not row.get(self.required_field):  # skip row if required_field is empty
                    continue


                if self.field_entry:
                    identifier = row[self.field_entry]
                    if identifier == document_id:
                        is_new_document = False
                    else:
                        document_id = identifier

                if is_new_document and rows:
                    yield self.document_from_rows(rows, metadata, index)
                    rows = [row]
                    index += 1
                else:
                    rows.append(row)

            yield self.document_from_rows(rows, metadata, index)

    def document_from_rows(self, rows, metadata, row_index):
        '''
        Extract a single document from a list of rows
        '''

        doc = {
            field.name: field.extractor.apply(
                # The extractor is put to work by simply throwing at it
                # any and all information it might need
                rows=rows, metadata = metadata, index=row_index
            )
            for field in self.fields if not field.skip
        }

        return doc
