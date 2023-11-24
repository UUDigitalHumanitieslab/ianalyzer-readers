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

class HTMLCorpusDefinition(XMLCorpusDefinition):
    '''
    An HTMLCorpus is any corpus that extracts its data from HTML sources.
    '''

    def source2dicts(self, source):
        '''
        Generate a document dictionaries from a given HTML file. This is the
        default implementation for HTML layouts; may be subclassed if more
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
                    ) for field in self.fields if field.indexed
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
                ) for field in self.fields if field.indexed
            }
