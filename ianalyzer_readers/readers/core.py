'''
This module defines the base classes on which all Readers are built.

It implements very little functionality of its own, but defines the interface
that Readers implement.

The module defines two classes, `Field` and `Reader`.
'''

from .. import extract
from datetime import datetime
from typing import List, Iterable, Dict, Any
import logging

logger = logging.getLogger()


class Reader(object):
    '''
    A base class for readers. Readers are objects that can generate documents
    from a source dataset.

    Subclasses of `Reader` can be created to read particular data formats or even
    particular datasets.
    
    The `Reader` class is not intended to be used directly. Some methods need to
    be implemented in child components, and will raise `NotImplementedError` if
    you try to use `Reader` directly.

    A fully implemented `Reader` subclass will define how to read a dataset by
    describing:

    - How to obtain its source files.
    - What fields each document contains.
    - How to extract said fields from the source files.
    '''

    @property
    def data_directory(self) -> str:
        '''
        Path to source data directory.

        Raises:
            NotImplementedError: This method needs to be implementd on child
                classes. It will raise an error by default.
        '''
        raise NotImplementedError('Reader missing data_directory')


    @property
    def fields(self) -> List:
        '''
        The list of fields that are extracted from documents.

        These should be instances of the `Field` class (or implement the same API).

        Raises:
            NotImplementedError: This method needs to be implementd on child
                classes. It will raise an error by default.
        '''
        raise NotImplementedError('Reader missing fields')

    @property
    def fieldnames(self) -> List[str]:
        '''
        A list containing the name of each field of this Reader
        '''
        return [field.name for field in self.fields]

    def sources(self, **kwargs) -> Iterable:
        '''
        Obtain source files for the Reader.

        Returns:
            an iterable of tuples that each contain a string path, and a dictionary
                with associated metadata. The metadata can contain any data that was
                extracted before reading the file itself, such as data based on the
                file path, or on a metadata file.

        Raises:
            NotImplementedError: This method needs to be implementd on child
                classes. It will raise an error by default.
        '''
        raise NotImplementedError('CorpusDefinition missing sources')

    def source2dicts(self, source) -> Iterable[Dict[str, Any]]:
        '''
        Given a source file, returns an iterable of extracted documents.

        Returns:
            an iterable of document dictionaries. Each of these is a dictionary,
                where the keys are names of this Reader's `fields`, and the values
                are based on the extractor of each field.

        Raises:
            NotImplementedError: This method needs to be implementd on child
                classes. It will raise an error by default.
        '''
        raise NotImplementedError('CorpusDefinition missing source2dicts')

    def documents(self, sources:Iterable[str]=None) -> Iterable[Dict[str, Any]]:
        '''
        Returns an iterable of extracted documents from source files.

        Parameters:
            sources: an iterable of paths to source files. If omitted, the reader
                class will use the value of `self.sources()` instead.

        Returns:
            an iterable of document dictionaries. Each of these is a dictionary,
                where the keys are names of this Reader's `fields`, and the values
                are based on the extractor of each field.
        '''
        sources = sources or self.sources()
        return (document
                for source in sources
                for document in self.source2dicts(
                    source
                )
                )

    def _reject_extractors(self, *inapplicable_extractors):
        '''
        Raise errors if any fields use extractors that are not applicable
        for the corpus.
        '''
        for field in self.fields:
            if isinstance(field.extractor, inapplicable_extractors):
                raise RuntimeError(
                    "Specified extractor method cannot be used with this type of data")

# Fields ######################################################################

class Field(object):
    '''
    Fields are the elements of information that you wish to extract from each document.

    Parameters:
        name:  a short hand name (name), which will be used as its key in the document
        extractor: an Extractor object that defines how this field's data can be
            extracted from source documents.
        required: whether this field is required. The `Reader` class should skip the
            document is the value for this Field is `None`, though this is not supported
            for all readers.
        skip: if `True`, this field will not be included in the results.
    '''

    def __init__(self,
                 name=None,
                 extractor=extract.Constant(None),
                 required=False,
                 skip=False,
                 **kwargs
                 ):

        self.name = name
        self.extractor = extractor
        self.required = required
        self.skip = skip
