'''
This module defines the XML Reader.

Extraction is based on BeautifulSoup.
'''

import itertools
import bs4
import logging
from typing import Union, Dict, Callable, Any, Iterable, Tuple

from .. import extract
from .core import Reader, Source, Document
from ..utils import XMLTag

logger = logging.getLogger()

TagSpecification = Union[
    None,
    XMLTag,
    Callable[[Any, Dict], Union[None, XMLTag]]
]
'''
A specification for an XML tag used in the `XMLReader`.

These can be:

- None
- An `XMLTag` object
- A callable that takes an `XMLReader` instance and a dictionary with metadata for the
    file, and returns one of the above.
'''

class XMLReader(Reader):
    '''
    A base class for Readers that extract data from XML files.

    The built-in functionality of the XML reader is quite versatile, and can be further expanded by
    adding custom functions to XML extractors that interact directly with BeautifulSoup nodes.

    The Reader is suitable for datasets where each file should be extracted as a single document, or
    ones where each file contains multiple documents.

    In addition to generic extractor classes, this reader supports the `XML` extractor.
    '''

    tag_toplevel: TagSpecification = None
    '''
    The top-level tag in the source documents.

    Can be:

    - None
    - A string with the name of the tag
    - A dictionary that gives the named arguments to soup.find_all()
    - A bound method that takes the metadata of the document as input and outputs one of the above.
    '''

    tag_entry: TagSpecification = None
    '''
    The tag that corresponds to a single document entry.

    Can be:

    - None
    - A string with the name of the tag
    - A dictionary that gives the named arguments to soup.find_all()
    - A bound method that takes the metadata of the document as input and outputs one of the above.
    '''

    def source2dicts(self, source: Source) -> Iterable[Document]:
        '''
        Given an XML source file, returns an iterable of extracted documents.

        Parameters:
            source: the source file to extract. This can be a string with the path to
                the file, or a tuple with a path and a dictionary containing metadata.
        
        Returns:
            an iterable of document dictionaries. Each of these is a dictionary,
                where the keys are names of this Reader's `fields`, and the values
                are based on the extractor of each field.
        '''
        # Make sure that extractors are sensible
        self._reject_extractors(extract.CSV)

        soup, metadata = self._soup_and_metadata_from_source(source)

        # extract information from external xml files first, if applicable
        if metadata and 'external_file' in metadata:
            external_fields = [field for field in self.fields if
                               isinstance(field.extractor, extract.XML) and
                               field.extractor.external_file]
            regular_fields = [field for field in self.fields if
                              field not in external_fields]
            external_soup = self._soup_from_xml(metadata['external_file'])
        else:
            regular_fields = self.fields
            external_dict = {}
            external_fields = None
        required_fields = [
            field.name for field in self.fields if field.required]
        # Extract fields from the soup

        tag = self._get_tag_requirements(self.tag_entry, metadata)
        bowl = self._bowl_from_soup(soup, metadata=metadata)
        if bowl:
            spoonfuls = tag.find_in_soup(bowl) if tag else [bowl]
            for i, spoon in enumerate(spoonfuls):
                regular_field_dict = {field.name: field.extractor.apply(
                    # The extractor is put to work by simply throwing at it
                    # any and all information it might need
                    soup_top=bowl,
                    soup_entry=spoon,
                    metadata=metadata,
                    index=i,
                ) for field in regular_fields if not field.skip}
                external_dict = {}
                if external_fields:
                    metadata.update(regular_field_dict)
                    external_dict = self._external_source2dict(
                        external_soup, external_fields, metadata)

                # yield the union of external fields and document fields
                full_dict = dict(itertools.chain(
                    external_dict.items(), regular_field_dict.items()))

                # check if required fields are filled
                if all((full_dict[field_name]
                        for field_name in required_fields)):
                    yield full_dict
        else:
            logger.warning(
                'Top-level tag not found in `{}`'.format(source))

    def _get_tag_requirements(self, specification: TagSpecification, metadata: Dict) -> Union[None, XMLTag]:
        '''
        Get the requirements for a tag given the specification and metadata.

        The specification can be:
        - None
        - An `XMLTag` object
        - A callable that takes an `XMLReader` instance and a dictionary with metadata for the
            file, and returns one of the above.

        Returns:
            either `None` or an `XMLTag` object
            
        If the specification is a callable, this method calls it.
        '''

        if callable(specification):
            return specification(metadata)
        else:
            return specification

    def _external_source2dict(self, soup, external_fields, metadata):
        '''
        given an external xml file with metadata,
        return a dictionary with tags which were found in that metadata
        wrt to the current source.
        '''
        external_dict = {}
        for field in external_fields:
            bowl = self._bowl_from_soup(
                soup, field.extractor.external_file['xml_tag_toplevel'])
            if bowl:
                external_dict[field.name] = field.extractor.apply(
                    soup_top=bowl,
                    soup_entry=bowl,
                    metadata=metadata
                )
            else:
                logger.warning(
                    'Top-level tag not found in `{}`'.format(bowl))
        return external_dict

    def _soup_and_metadata_from_source(self, source: Source) -> Tuple[bs4.BeautifulSoup, Dict]:
        metadata = {}
        if isinstance(source, str):
            # no metadata
            filename = source
            soup = self._soup_from_xml(filename)
        elif isinstance(source, bytes):
            soup = self._soup_from_data(source)
            filename = soup.find('RecordID')
        else:
            filename = source[0]
            soup = self._soup_from_xml(filename)
            metadata = source[1] or None
            soup = self._soup_from_xml(filename)
        return soup, metadata

    def _soup_from_xml(self, filename):
        '''
        Returns beatifulsoup soup object for a given xml file
        '''
        # Loading XML
        logger.info('Reading XML file {} ...'.format(filename))
        with open(filename, 'rb') as f:
            data = f.read()
        logger.info('Loaded {} into memory...'.format(filename))
        return self._soup_from_data(data)

    def _soup_from_data(self, data):
        '''
        Parses content of a xml file
        '''
        return bs4.BeautifulSoup(data, 'lxml-xml')

    def _bowl_from_soup(self,
            soup,
            toplevel_tag: TagSpecification = None,
            metadata: Dict = {}
        ):
        '''
        Returns bowl (subset of soup) of soup object. Bowl contains everything within the toplevel tag.
        If no such tag is present, it contains the entire soup.
        '''
        if toplevel_tag == None:
            toplevel_tag = self._get_tag_requirements(self.tag_toplevel, metadata)
        else:
            toplevel_tag = self._get_tag_requirements(toplevel_tag, metadata)

        if toplevel_tag:
            return toplevel_tag.find_next_in_soup(soup)
        else:
            return soup

