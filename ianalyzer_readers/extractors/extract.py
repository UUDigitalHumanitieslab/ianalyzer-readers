'''
This module contains extractor classes that can be used to obtain values for each field
in a Reader.
'''

import bs4
import html
import re
import logging
import traceback
logger = logging.getLogger()


class Extractor(object):
    '''
    An extractor contains a method that can be used to gather data for a field. 
    '''

    def __init__(self,
                 applicable=None,  # Predicate that takes metadata and decides whether
                 # this extractor is applicable. None means always.
                 transform=None   # Optional function to postprocess extracted value
                 ):
        self.transform = transform
        self.applicable = applicable

    def apply(self, *nargs, **kwargs):
        '''
        Test if the extractor is applicable to the given arguments and if so,
        try to extract the information.
        '''
        if self.applicable is None or self.applicable(kwargs.get('metadata')):
            result = self._apply(*nargs, **kwargs)
            try:
                if self.transform:
                    return self.transform(result)
            except Exception:
                logger.error(traceback.format_exc())
                logger.critical("Value {v} could not be converted."
                                .format(v=result))
                return None
            else:
                return result
        else:
            return None

    def _apply(self, *nargs, **kwargs):
        '''
        Actual extractor method to be implemented in subclasses (assume that
        testing for applicability and post-processing is taken care of).
        '''
        raise NotImplementedError()


class Choice(Extractor):
    '''
    Use the first applicable extractor from a list of extractors.
    '''

    def __init__(self, *nargs, **kwargs):
        self.extractors = list(nargs)
        super().__init__(**kwargs)

    def _apply(self, metadata, *nargs, **kwargs):
        for extractor in self.extractors:
            if extractor.applicable is None or extractor.applicable(metadata):
                return extractor.apply(metadata=metadata, *nargs, **kwargs)
        return None


class Combined(Extractor):
    '''
    Apply all given extractors and return the results as a tuple.
    '''

    def __init__(self, *nargs, **kwargs):
        self.extractors = list(nargs)
        super().__init__(**kwargs)

    def _apply(self, *nargs, **kwargs):
        return tuple(
            extractor.apply(*nargs, **kwargs) for extractor in self.extractors
        )


class Backup(Extractor):
    '''
    Try all given extractors in order and return the first result that evaluates as true
    '''
    def __init__(self, *nargs, **kwargs):
        self.extractors = list(nargs)
        super().__init__(**kwargs)

    def _apply(self, *nargs, **kwargs):
        for extractor in self.extractors:
            result = extractor.apply(*nargs, **kwargs)
            if result:
                return result
        return None


class Constant(Extractor):
    '''
    This extractor 'extracts' the same value every time, regardless of input.
    '''

    def __init__(self, value, *nargs, **kwargs):
        self.value = value
        super().__init__(*nargs, **kwargs)

    def _apply(self, *nargs, **kwargs):
        return self.value


class Metadata(Extractor):
    '''
    This extractor extracts a value from provided metadata.
    '''

    def __init__(self, key, *nargs, **kwargs):
        self.key = key
        super().__init__(*nargs, **kwargs)

    def _apply(self, metadata, *nargs, **kwargs):
        return metadata.get(self.key)

class Pass(Extractor):
    '''
    An extractor that just passes the value of another extractor.

    Useful if you want to stack multiple `transform` arguments
    '''

    def __init__(self, extractor, *nargs, **kwargs):
        self.extractor = extractor
        super().__init__(**kwargs)

    def _apply(self, *nargs, **kwargs):
        return self.extractor.apply(*nargs, **kwargs)

class Order(Extractor):
    '''
    An extractor that returns the index of the document in its
    source file.
    '''

    def _apply(self, index=None, *nargs, **kwargs):
        return index

class XML(Extractor):
    '''
    Extractor for XML data. Searches through a BeautifulSoup document.
    '''

    def __init__(self,
                 # Tag to select. When this is a list, read as a path
                 # e.g. to select successive children; makes sense when recursive=False)
                 # Pass None if the information is in the attribute of the
                 # current head of the tree
                 tag=[],
                 # whether to ascend the tree to find the indicated tag
                 # useful when a part of the tree has been selected with secondary_tag
                 parent_level=None,
                 attribute=None,  # Which attribute, if any, to select
                 flatten=False,  # Flatten the text content of a non-text children?
                 toplevel=False,  # Tag to select for search: top-level or entry tag
                 recursive=False,  # Whether to search all descendants
                 multiple=False,  # Whether to abandon the search after the first element
                 secondary_tag={
                     'tag': None,
                     'match': None,
                     'exact': None,
                 },  # Whether the tag's content should match a given metadata field ('match') or string ('exact')
                 external_file={  # Whether to search other xml files for this field, and the file tag these files should have
                     'xml_tag_toplevel': None,
                     'xml_tag_entry': None
                 },
                 # a function [e.g. `my_func(soup)`]` to transform the soup directly
                 # after _select was called, i.e. before further processing (attributes, flattening, etc).
                 # Keep in mind that the soup passed could be None.
                 transform_soup_func=None,
                 # a function to extract a value directly from the soup object, instead of using the content string
                 # or giving an attribute
                # Keep in mind that the soup passed could be None.
                 extract_soup_func=None,
                 *nargs,
                 **kwargs
                 ):

        self.tag = tag
        self.parent_level = parent_level
        self.attribute = attribute
        self.flatten = flatten
        self.toplevel = toplevel
        self.recursive = recursive
        self.multiple = multiple
        self.secondary_tag = secondary_tag if secondary_tag['tag'] != None else None
        self.external_file = external_file if external_file['xml_tag_toplevel'] else None
        self.transform_soup_func = transform_soup_func
        self.extract_soup_func = extract_soup_func
        super().__init__(*nargs, **kwargs)

    def _select(self, soup, metadata=None):
        '''
        Return the BeautifulSoup element that matches the constraints of this
        extractor.
        '''
        # If the tag was a path, walk through it before continuing
        tag = self.tag
        if not tag:
            return soup
        if isinstance(self.tag, list):
            if len(tag) == 0:
                return soup
            for i in range(0, len(self.tag)-1):
                if self.tag[i] == '..':
                    soup = soup.parent
                elif self.tag[i] == '.':
                    pass
                else:
                    soup = soup.find(self.tag[i], recursive=self.recursive)
                if not soup:
                    return None
            tag = self.tag[-1]

        # Find and return a tag which is a sibling of a secondary tag
        # e.g., we need a category tag associated with a specific id
        if self.secondary_tag:
            # match metadata field
            if self.secondary_tag.get('match') is not None:
                match_string = metadata[self.secondary_tag['match']]
            elif self.secondary_tag.get('exact') is not None:
                match_string = self.secondary_tag['exact']
            sibling = soup.find(self.secondary_tag['tag'], string=match_string)
            if sibling:
                return sibling.parent.find(tag)

        # Find and return (all) relevant BeautifulSoup element(s)
        if self.multiple:
            return soup.find_all(tag, recursive=self.recursive)
        elif self.parent_level:
            count = 0
            while count < self.parent_level:
                soup = soup.parent
                count += 1
            return soup.find(tag, recursive=self.recursive)
        else:
            return soup.find(tag, recursive=self.recursive)

    def _apply(self, soup_top, soup_entry, *nargs, **kwargs):
        if 'metadata' in kwargs:
            # pass along the metadata to the _select method
            soup = self._select(
                soup_top if self.toplevel else soup_entry, metadata=kwargs['metadata'])
        # Select appropriate BeautifulSoup element
        else:
            soup = self._select(soup_top if self.toplevel else soup_entry)
        if self.transform_soup_func:
            if type(soup) == bs4.element.ResultSet:
                soup = [self.transform_soup_func(bowl) for bowl in soup]
            else:
                soup = self.transform_soup_func(soup)
        if not soup:
            return None

        # Use appropriate extractor
        if self.extract_soup_func:
            return self.extract_soup_func(soup)
        elif self.attribute:
            return self._attr(soup)
        else:
            if self.flatten:
                return self._flatten(soup)
            else:
                return self._string(soup)

    def _string(self, soup):
        '''
        Output direct text contents of a node.
        '''

        if isinstance(soup, bs4.element.Tag):
            return soup.string
        else:
            return [node.string for node in soup]

    def _flatten(self, soup):
        '''
        Output text content of node and descendant nodes, disregarding
        underlying XML structure.
        '''

        if isinstance(soup, bs4.element.Tag):
            text = soup.get_text()
        else:
            text = '\n\n'.join(node.get_text() for node in soup)

        _softbreak = re.compile('(?<=\S)\n(?=\S)| +')
        _newlines = re.compile('\n+')
        _tabs = re.compile('\t+')

        return html.unescape(
            _newlines.sub(
                '\n',
                _softbreak.sub(' ', _tabs.sub('', text))
            ).strip()
        )

    def _attr(self, soup):
        '''
        Output content of nodes' attribute.
        '''

        if isinstance(soup, bs4.element.Tag):
            if self.attribute == 'name':
                return soup.name
            return soup.attrs.get(self.attribute)
        else:
            if self.attribute == 'name':
                return [ node.name for node in soup]
            return [
                node.attrs.get(self.attribute)
                for node in soup if node.attrs.get(self.attribute) is not None
            ]


class FilterAttribute(XML):
    '''
    This extractor extracts attributes or contents from a BeautifulSoup node.
    It is an extension of the XML extractor
    '''

    def __init__(self,
                 attribute_filter={  # Specify an attribute / value pair by which to select content
                     'attribute': None,
                     'value': None},
                 *nargs,
                 **kwargs
                 ):
        super().__init__(*nargs, **kwargs)
        self.attribute_filter = attribute_filter

    def _select(self, soup, metadata):
        '''
        Return the BeautifulSoup element that matches the constraints of this
        extractor.
        '''
        # If the tag was a path, walk through it before continuing
        tag = self.tag

        if isinstance(self.tag, list):
            if len(tag) == 0:
                return soup
            for i in range(0, len(self.tag)-1):
                if self.tag[i] == '..':
                    soup = soup.parent
                elif self.tag[i] == '.':
                    pass
                else:
                    soup = soup.find(self.tag[i], recursive=self.recursive)

                if not soup:
                    return None
            tag = self.tag[-1]

        # Find and return (all) relevant BeautifulSoup element(s)
        if self.multiple:
            return soup.find_all(tag, recursive=self.recursive)
        else:
            return(soup.find(tag, {self.attribute_filter['attribute']: self.attribute_filter['value']}))

class CSV(Extractor):
    '''
    This extractor extracts values from a list of CSV or spreadsheet rows.

    Parameters:
    - multiple: Boolean. If a document spans multiple rows, the extracted value for a field with
    `multiple = True` is a list of the value in each row. If `multiple = False` (default), only the value
    from the first row is extracted.
    - convert_to_none: optional, default is `['']`. Listed values are converted to `None`. If `None`/`False`, nothing is converted.
    '''
    def __init__(self,
            field,
            multiple=False,
            convert_to_none = [''],
            *nargs, **kwargs):
        self.field = field
        self.multiple = multiple
        self.convert_to_none = convert_to_none or []
        super().__init__(*nargs, **kwargs)

    def _apply(self, rows, *nargs, **kwargs):
        if self.field in rows[0]:
            if self.multiple:
                return [self.format(row[self.field]) for row in rows]
            else:
                row = rows[0]
                return self.format(row[self.field])

    def format(self, value):
        if value and value not in self.convert_to_none:
            return value

class ExternalFile(Extractor):

    def __init__(self, stream_handler, *nargs, **kwargs):
        '''
        Free for all external file extractor that provides a stream to `stream_handler`
        to do whatever is needed to extract data from an external file. Relies on `associated_file`
        being present in the metadata. Note that the XMLExtractor has a built in trick to extract
        data from external files (i.e. setting `external_file`), so you probably need that if your
        external file is XML.

        Parameters:
            folder -- folder where the file is located.
            stream_handler -- function that will handle the opened file.
        '''
        super().__init__(*nargs, **kwargs)
        self.stream_handler = stream_handler

    def _apply(self, metadata, *nargs, **kwargs):
        '''
        Extract `associated_file` from metadata and call `self.stream_handler` with file stream.
        '''
        return self.stream_handler(open(metadata['associated_file'], 'r'))
