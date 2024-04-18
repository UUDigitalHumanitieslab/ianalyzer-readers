from typing import List, Dict, Iterable

from rdflib import Graph

from .core import Reader, Document, Source
from .. import extract


class RDFReader(Reader):
    '''
    A base class for Readers of .ttl (linked data) files.
    '''

    def source2dicts(self, source: Source) -> Iterable[Document]:
        '''
        Given a .ttl source file, returns an iterable of extracted documents.

        Parameters:
            source: the source file to extract. This can be a string with the path to
                the file, or a tuple with a path and a dictionary containing metadata.

        Returns:
            an iterable of document dictionaries. Each of these is a dictionary,
                where the keys are names of this Reader's `fields`, and the values
                are based on the extractor of each field.
        '''
        filename = source
        g = Graph()
        g.parse(filename, format='ttl')
        print(len(g))
        yield g
