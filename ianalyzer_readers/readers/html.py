'''
This module defines the XML Reader.

The HTML reader is implemented as a subclas of the XML reader, and uses
BeautifulSoup to parse files.
'''

from .. import extract
from .core import Source, Document
from .xml import XMLReader
import bs4
import logging
from typing import Iterable

logger = logging.getLogger()


class HTMLReader(XMLReader):
    '''
    An HTML reader extracts data from HTML sources.

    It is based on the XMLReader and supports the same options (`tag_toplevel` and
    `tag_entry`).

    In addition to generic extractor classes, this reader supports the `XML` and
    `FilterAttribute` extractors.
    '''

    def source2dicts(self, source: Source) -> Iterable[Document]:
        '''
        Given an HTML source file, returns an iterable of extracted documents.

        Parameters:
            source: the source file to extract. This can be a string with the path to
                the file, or a tuple with a path and a dictionary containing metadata.
        
        Returns:
            an iterable of document dictionaries. Each of these is a dictionary,
                where the keys are names of this Reader's `fields`, and the values
                are based on the extractor of each field.
        '''
        (filename, metadata) = source

        self._reject_extractors(extract.CSV)

        # Loading HTML
        logger.info('Reading HTML file {} ...'.format(filename))
        with open(filename, 'rb') as f:
            data = f.read()
        # Parsing HTML
        soup = bs4.BeautifulSoup(data, 'html.parser')
        logger.info('Loaded {} into memory ...'.format(filename))

        # Extract fields from soup
        tag0 = self.tag_toplevel
        tag = self.tag_entry

        bowl = soup.find(tag0) if tag0 else soup

        # if there is a entry level tag, with html this is not always the case
        if bowl and tag:
            # Note that this is non-recursive: will only find direct descendants of the top-level tag
            for i, spoon in enumerate(bowl.find_all(tag)):
                # yield
                yield {
                    field.name: field.extractor.apply(
                        # The extractor is put to work by simply throwing at it
                        # any and all information it might need
                        soup_top=bowl,
                        soup_entry=spoon,
                        metadata=metadata,
                        index=i
                    ) for field in self.fields if not field.skip
                }
        else:
            # yield all page content
            yield {
                field.name: field.extractor.apply(
                    # The extractor is put to work by simply throwing at it
                    # any and all information it might need
                    soup_top='',
                    soup_entry=soup,
                    metadata=metadata,
                ) for field in self.fields if not field.skip
            }
