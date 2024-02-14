'''
Mode for the HTML reader.

The HTML reader is implemented as a subclas of the XML reader.
'''

from .. import extract
from .xml import XMLReader
import bs4
import logging

logger = logging.getLogger()


class HTMLReader(XMLReader):
    '''
    An HTML reader extracts data from HTML sources. It is based on the XML reader.
    '''

    def source2dicts(self, source):
        '''
        Generate document dictionaries from a given HTML file.
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
