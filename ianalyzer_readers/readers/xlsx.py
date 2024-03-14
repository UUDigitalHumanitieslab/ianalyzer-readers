import logging
import openpyxl
from openpyxl.worksheet.worksheet import Worksheet
from typing import Iterable

from .core import Reader, Document, Source
from .. import extract

logger = logging.getLogger()


class XLSXReader(Reader):
    '''
    A base class for Readers that extract data from .xlsx spreadsheets

    The XLSXReader is quite rudimentary, and is designed to extract data from
    spreadsheets that are formatted like a CSV table, with a clear column layout. The
    sheet should have a header row.

    The data should be structured in one of the following ways:
    
    - one document per row (this is the default)
    - each document spans a number of consecutive rows. In this case, there should be a
        column that indicates the identity of the document.

    The XLSXReader will only look at the _first_ sheet in each file.

    In addition to generic extractor classes, this reader supports the `CSV` extractor.
    '''

    field_entry = None
    '''
    If applicable, the name of column that identifies entries. Subsequent rows with the
    same value for this column are treated as a single document. If left blank, each row
    is treated as a document.
    '''

    required_field = None
    '''
    Specifies the name of a required column, for example the main content. Rows with
    an empty value for `required_field` will be skipped.
    '''

    skip_lines = 0
    '''
    Number of lines in the sheet to skip before reading the header. Can be used when files
    use a fixed "preamble", e.g. to describe metadata or provenance.
    '''


    def source2dicts(self, source: Source) -> Iterable[Document]:
        '''
        Given an XLSX source file, returns an iterable of extracted documents.

        Parameters:
            source: the source file to extract. This can be a string with the path to
                the file, or a tuple with a path and a dictionary containing metadata.
        
        Returns:
            an iterable of document dictionaries. Each of these is a dictionary,
                where the keys are names of this Reader's `fields`, and the values
                are based on the extractor of each field.
        '''

        self._reject_extractors(extract.XML, extract.FilterAttribute)

        if isinstance(source, str):
            filename = source
            metadata = {}
        elif isinstance(source, bytes):
            raise NotImplementedError()
        else:
            filename, metadata = source

        wb = openpyxl.load_workbook(filename)
        logger.info('Reading XLSX file {}...'.format(filename))

        sheets = wb.sheetnames
        sheet = wb[sheets[0]]
        return self._sheet2dicts(sheet, metadata)

    def _sheet2dicts(self, sheet: Worksheet, metadata):
        '''
        Extract documents from a single worksheet
        '''
        
        data = (row for row in sheet.values)

        for _ in range(self.skip_lines):
            next(data)

        header = list(next(data))

        index = 0
        document_id = None
        rows = []

        for row in data:
            values = {
                col: value
                for col, value in zip(header, row)
            }

            # skip row if required_field is empty
            if self.required_field and not values.get(self.required_field):
                continue

            identifier = values.get(self.field_entry, None)
            is_new_document = identifier == None or identifier != document_id
            document_id = identifier

            if is_new_document and rows:
                yield self._document_from_rows(rows, metadata, index)
                rows = [values]
                index += 1
            else:
                rows.append(values)

        if rows:
            yield self._document_from_rows(rows, metadata, index)

    def _document_from_rows(self, rows, metadata, doc_index):
        '''
        Extract a single document from a list of row data

        Parameters:
            rows: a list of row data. Each row is expected to be a dictionary.
            metadata: a dictionary with file metadata. 
            doc_index: the index of this document in the source file. The first document
                extracted from a file should have index 0, the second should have index 1,
                and so forth.
        '''

        doc = {
            field.name: field.extractor.apply(
                rows=rows, metadata=metadata, index=doc_index
            )
            for field in self.fields if not field.skip
        }

        return doc
