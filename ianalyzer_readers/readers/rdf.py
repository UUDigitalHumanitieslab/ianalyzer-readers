'''
This module defines a Resource Description Framework (RDF) reader.

Extraction is based on the [rdflib library](https://rdflib.readthedocs.io/en/stable/index.html).
'''

from typing import Iterable, Union

from rdflib import BNode, Graph, Literal, URIRef

from .core import Reader, Document, Source
import ianalyzer_readers.extract as extract


class RDFReader(Reader):
    '''
    A base class for Readers of Resource Description Framework files.
    These could be in Turtle, JSON-LD, RDFXML or other formats,
    see [rdflib parsers](https://rdflib.readthedocs.io/en/stable/plugin_parsers.html).
    '''

    def source2dicts(self, source: Source) -> Iterable[Document]:
        '''
        Given a RDF source file, returns an iterable of extracted documents.

        Parameters:
            source: the source file to extract. This can be a string of the file path, or a tuple of the file path and metadata.

        Returns:
            an iterable of document dictionaries. Each of these is a dictionary,
                where the keys are names of this Reader's `fields`, and the values
                are based on the extractor of each field.
        '''
        self._reject_extractors(extract.CSV, extract.XML)
        
        metadata = None
        if type(source) == tuple:
            filename = source[0]
            metadata = source[1]
        elif type(source) == bytes:
            raise Exception('The current reader cannot handle sources of bytes type, provide a file path as string instead')
        else:
            filename = source
        g = Graph()
        g.parse(filename)
        document_subjects = self.document_subjects(g)
        for subject in document_subjects:
            content = self._document_from_subject(g, subject)
            if metadata:
                yield content, metadata
            else:
                yield content

    def document_subjects(self, graph: Graph) -> Iterable[Union[BNode, Literal, URIRef]]:
        ''' Override this function to return all subjects (i.e., first part of RDF triple) 
        with which to search for data in the RDF graph.
        Typically, such subjects are identifiers or urls.
        
        Parameters:
            graph: the graph to parse
        
        Returns:
            generator or list of nodes
        '''
        return graph.subjects()

    def _document_from_subject(self, graph: Graph, subject: Union[BNode, Literal, URIRef]) -> dict:
        return {field.name: field.extractor.apply(graph=graph, subject=subject) for field in self.fields}
