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
from ..utils import XMLTag, CurrentTag

TagSpecification = Union[
    XMLTag,
    Callable[[Any, Dict], XMLTag]
]

logger = logging.getLogger()

class XMLReader(Reader):
    '''
    A base class for Readers that extract data from XML files.

    The built-in functionality of the XML reader is quite versatile, and can be further expanded by
    adding custom functions to XML extractors that interact directly with BeautifulSoup nodes.

    The Reader is suitable for datasets where each file should be extracted as a single document, or
    ones where each file contains multiple documents.

    In addition to generic extractor classes, this reader supports the `XML` extractor.
    '''

    tag_toplevel: TagSpecification = CurrentTag()
    '''
    The top-level tag in the source documents.

    Can be:

    - An XMLTag
    - A 
    - A dictionary that gives the named arguments to soup.find_all()
    - A bound method that takes the metadata of the document as input and outputs one of the above.
    '''

    tag_entry: TagSpecification = CurrentTag()
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

        filename, soup, metadata = self._filename_soup_and_metadata_from_source(source)

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

        tag = self._resolve_tag(self.tag_entry, metadata)
        bowl = self._bowl_from_soup(soup, metadata=metadata)
        if bowl:
            spoonfuls = tag.find_in_soup(bowl)
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
                'Top-level tag not found in `{}`'.format(filename))

    def _resolve_tag(self, specification: TagSpecification, metadata: Dict) -> XMLTag:
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
                    'Top-level tag not found in `{}`'.format(metadata['external_file']))
        return external_dict

    def _filename_soup_and_metadata_from_source(self, source: Source) -> Tuple[str, bs4.BeautifulSoup, Dict]:
        if isinstance(source, str):
            filename = source
            soup = self._soup_from_xml(filename)
            metadata = {}
        elif isinstance(source, bytes):
            soup = self._soup_from_data(source)
            filename = None
            metadata = {}
        else:
            filename = source[0]
            soup = self._soup_from_xml(filename)
            metadata = source[1] or None
        return filename, soup, metadata

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
            toplevel_tag = self._resolve_tag(self.tag_toplevel, metadata)
        else:
            toplevel_tag = self._resolve_tag(toplevel_tag, metadata)

        return toplevel_tag.find_next_in_soup(soup)

