'''
Module contains the base classes from which corpora can derive;
'''

from . import extract
import itertools
import bs4
import csv
import sys
from datetime import datetime
from os.path import isdir

from django.conf import settings

import logging

logger = logging.getLogger('indexing')

class CSVCorpusDefinition(CorpusDefinition):
    '''
    An CSVCorpus is any corpus that extracts its data from CSV sources.
    '''

    '''
    If applicable, the field that identifies entries. Subsequent rows with the same
    value for this field are treated as a single document. If left blank, each row
    is treated as a document.
    '''
    field_entry = None

    '''
    Specifies a required field, for example the main content. Rows with
    an empty value for `required_field` will be skipped.
    '''
    required_field = None

    '''
    The delimiter for the CSV reader.
    '''
    delimiter = ','

    '''
    Number of lines to skip before reading the header
    '''
    skip_lines = 0

    def source2dicts(self, source):
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
        doc = {
            field.name: field.extractor.apply(
                # The extractor is put to work by simply throwing at it
                # any and all information it might need
                rows=rows, metadata = metadata, index=row_index
            )
            for field in self.fields if field.indexed
        }

        return doc
