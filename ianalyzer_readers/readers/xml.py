'''
This module defines the XML Reader.

Extraction is based on BeautifulSoup.
'''

from .. import extract
from .core import Reader, Source, Document
import itertools
import bs4
import logging
from typing import Union, Dict, Callable, Any, Iterable

logger = logging.getLogger()

TagSpecification = Union[
    None,
    str,
    Dict[str, Any],
    Callable[[Any, Dict], Union[None, str, Dict[str, Any]]]
]
'''
A specification for an XML tag used in the `XMLReader`.

These can be:

- None
- a string with the name of the tag
- a dictionary with the named arguments that should be passed to the `find()` / `find_all()`
    method of a BeautifulSoup node.
- A callable that takes an `XMLReader` instance and a dictionary with file metadata, and
    returns any of the above.
'''

class XMLReader(Reader):
    '''
    A base class for Readers that extract data from XML files.

    The built-in functionality of the XML reader is quite versatile, and can be further expanded by
    adding custom functions to XML extractors that interact directly with BeautifulSoup nodes.

    The Reader is suitable for datasets where each file should be extracted as a single document, or
    ones where each file contains multiple documents.

    In addition to generic extractor classes, this reader supports the `XML` and
    `FilterAttribute` extractors.
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

        # extract information from external xml files first, if applicable
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
            spoonfuls = bowl.find_all(**tag) if tag else [bowl]
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

    def _get_tag_requirements(self, specification, metadata):
        '''
        Get the requirements for a tag given the specification and metadata.

        The specification can be:
        - None
        - A string with the name of the tag
        - A dict with the named arguments to soup.find() / soup.find_all()
        - A callable that takes the document metadata as input and outputs one of the above.

        Output is either None or a dict with the arguments for soup.find() / soup.find_all()
        '''

        if callable(specification):
            condition = specification(metadata)
        else:
            condition = specification

        if condition is None:
            return None
        elif type(condition) == str:
            return {'name': condition}
        elif type(condition) == dict:
            return condition
        else:
            raise TypeError('Tag must be a string or dict')

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
            spoon = None
            if field.extractor.secondary_tag:
                # find a specific subtree in the xml tree identified by matching a secondary tag
                try:
                    spoon = bowl.find(
                        field.extractor.secondary_tag['tag'],
                        string=metadata[field.extractor.secondary_tag['match']]).parent
                except:
                    logging.debug('tag {} not found in metadata'.format(
                        field.extractor.secondary_tag
                    ))
            if not spoon:
                spoon = field.extractor.external_file['xml_tag_entry']
            if bowl:
                external_dict[field.name] = field.extractor.apply(
                    soup_top=bowl,
                    soup_entry=spoon,
                    metadata=metadata
                )
            else:
                logger.warning(
                    'Top-level tag not found in `{}`'.format(bowl))
        return external_dict

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

    def _bowl_from_soup(self, soup, toplevel_tag=None, entry_tag=None, metadata = {}):
        '''
        Returns bowl (subset of soup) of soup object. Bowl contains everything within the toplevel tag.
        If no such tag is present, it contains the entire soup.
        '''
        if toplevel_tag == None:
            toplevel_tag = self._get_tag_requirements(self.tag_toplevel, metadata)

        return soup.find(**toplevel_tag) if toplevel_tag else soup

    def _metadata_from_xml(self, filename, tags):
        '''
        Given a filename of an xml with metadata, and a range of tags to extract,
        return a dictionary of all the contents of the requested tags.
        A tag can either be a string, or a dictionary:
        {
            "tag": "tag_to_extract",
            "attribute": attribute to additionally filter on, optional
            "save_as": key to use in output dictionary, optional
        }
        '''
        out_dict = {}
        soup = self._soup_from_xml(filename)
        for tag in tags:
            if isinstance(tag, str):
                tag_info = soup.find(tag)
                if not tag_info:
                    continue
                out_dict[tag] = tag_info.text
            else:
                candidates = soup.find_all(tag['tag'])
                if 'attribute' in tag:
                    right_tag = next((candidate for candidate in candidates if
                                      candidate.attrs == tag['attribute']), None)
                elif 'list' in tag:
                    if 'subtag' in tag:
                        right_tag = [candidate.find(
                            tag['subtag']) for candidate in candidates]
                    else:
                        right_tag = candidates
                elif 'subtag' in tag:
                    right_tag = next((candidate.find(tag['subtag']) for candidate in candidates if
                                      candidate.find(tag['subtag'])), None)
                else:
                    right_tag = next((candidate for candidate in candidates if
                                      candidate.attrs == {}), None)
                if not right_tag:
                    continue
                if 'save_as' in tag:
                    out_tag = tag['save_as']
                else:
                    out_tag = tag['tag']
                if 'list' in tag:
                    out_dict[out_tag] = [t.text for t in right_tag]
                else:
                    out_dict[out_tag] = right_tag.text
        return out_dict

