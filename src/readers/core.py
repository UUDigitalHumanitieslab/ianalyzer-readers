'''
More with core classes
'''

from ..extractors import extract
from datetime import datetime

import logging

logger = logging.getLogger()


class CorpusDefinition(object):
    '''
    Subclasses of this class define corpora and their documents by specifying:

    - How to obtain its source files.
    - What attributes its documents have.
    - How to extract said attributes from the source files.
    - What each attribute looks like in terms of the search form.
    '''

    @property
    def data_directory(self):
        '''
        Path to source data directory.
        '''
        raise NotImplementedError('CorpusDefinition missing data_directory')


    @property
    def fields(self):
        '''
        Each corpus should implement a list of fields, that is, instances of
        the `Field` class, containing information about each attribute.
        MUST include a field with `name='id'`.
        '''
        raise NotImplementedError('CorpusDefinition missing fields')

    def sources(self, **kwargs):
        '''
        Obtain source files for the corpus, relevant to the given timespan.

        Specifically, returns an iterator of tuples that each contain a string
        filename and a dictionary of associated metadata. The latter is usually
        empty or contains only a timestamp; but any data that is to be
        extracted without reading the file itself can be specified there.
        '''
        raise NotImplementedError('CorpusDefinition missing sources')

    def source2dicts(self, sources):
        '''
        Generate an iterator of document dictionaries from a given source file.

        The dictionaries are created from this corpus' `Field`s.
        '''
        raise NotImplementedError('CorpusDefinition missing source2dicts')

    def documents(self, sources=None):
        '''
        Generate an iterator of document dictionaries directly from the source
        files. The source files are generated by self.sources(); however, if
        `sources` is specified, those source/metadata tuples are used instead.
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

class ParentCorpusDefinition(CorpusDefinition):
    ''' A class from which other corpus definitions can inherit.
    This class is in charge of setting fields, usually without defining an extractor.
    The subclassed CorpusDefinitions will set extractors on the fields -
    this way, CorpusDefinitions can share the same mappings and filters,
    while the logic to collect sources and populate the fields can be different.
    The ParentCorpusDefinition can also be used to allow cross-corpus search and filtering.
    '''
    #define fields property so it can be set in __init__
    @property
    def fields(self):
        return self._fields

    @fields.setter
    def fields(self, value):
        self._fields = value

    def __init__(self):
        ''' Specify a list of fields which all subclasses share
            A subclass of ParentCorpusDefinition will provide extractors for the fields,
            and potentially prune done the list of fields to those which have an extractor
        '''
        self.fields = []


# Fields ######################################################################

class FieldDefinition(object):
    '''
    Fields hold the following data:
    - a short hand name (name)
    - how to extract data from the source documents (extractor)
    - whether this field is required
    '''

    def __init__(self,
                 name=None,
                 extractor=extract.Constant(None),
                 required=False,
                 **kwargs
                 ):

        self.name = name
        self.extractor = extractor
        self.required = required

# Helper functions ############################################################


def string_contains(target):
    '''
    Return a predicate that performs a case-insensitive search for the target
    string and returns whether it was found.
    '''
    def f(string):
        return bool(target.lower() in string.lower() if string else False)
    return f


def until(year):
    '''
    Returns a predicate to determine from metadata whether its 'date' field
    represents a date before or on the given year.
    '''
    def f(metadata):
        date = metadata.get('date')
        return date and date.year <= year
    return f


def after(year):
    '''
    Returns a predicate to determine from metadata whether its 'date' field
    represents a date after the given year.
    '''
    def f(metadata):
        date = metadata.get('date')
        return date and date.year > year
    return f


def consolidate_start_end_years(start, end, min_date, max_date):
    ''' given a start and end date provided by the user, make sure
    - that start is not before end
    - that start is not before min_date (corpus variable)
    - that end is not after max_date (corpus variable)
    '''
    if isinstance(start, int):
        start = datetime(year=start, month=1, day=1)
    if isinstance(end, int):
        end = datetime(year=end, month=12, day=31)
    if start > end:
        tmp = start
        start = end
        end = tmp
    if start < min_date:
        start = min_date
    if end > max_date:
        end = max_date
