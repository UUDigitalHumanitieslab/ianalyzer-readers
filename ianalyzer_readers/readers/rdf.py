'''
This module defines a Resource Description Framework (RDF) reader.

Extraction is based on the [rdflib library](https://rdflib.readthedocs.io/en/stable/index.html).
'''

from glob import glob
from typing import Dict, Iterable, Tuple, Union

from rdflib import BNode, Graph, Literal, URIRef

from .core import Reader, Document, Source
import ianalyzer_readers.extract as extract

Subject = Union[BNode, Literal, URIRef]

class RDFReader(Reader):
    '''
    A base class for Readers of Resource Description Framework files.
    These could be in Turtle, JSON-LD, RDFXML or other formats,
    see [rdflib parsers](https://rdflib.readthedocs.io/en/stable/plugin_parsers.html).
    '''

    def sources(self, **kwargs):
        ''' The RDFReader class overrides, atypically, the `sources` property
        to coerce the output of this function to RDF subjects, rather than file names.
        In order to adjust the strategy by which RDF files are located,
        override the `file_selector` function.
        '''
        files = self.file_selector()
        graph = Graph()
        for input_file in files:
            graph.parse(input_file)
        self.graph = graph
        for subject in self.document_subjects(graph):
            yield subject
    
    def file_selector(self) -> Iterable:
        ''' A function to locate potential RDF files
        This function assumes all files are contained within one directory
        Override this function for more complex directory structure
        and/or if rules for file selection should be applied.
        '''
        allowed_file_extensions = ['ttl', 'xml', 'json', 'rdf']
        files = []
        for extension in allowed_file_extensions:
            files.extend(glob(f'{self.data_directory}/*.{extension}'))
        return files

    def source2dicts(self, source: Union[Subject, Tuple[Subject, Dict]]) -> Iterable[Document]:
        '''
        Given a URIRef representing a subject, returns an iterable of extracted documents.

        Parameters:
            source: the subject to extract. This is an URIRef, or a tuple of a URIRef and metadata.

        Returns:
            an iterable of document dictionaries. Each of these is a dictionary,
                where the keys are names of this Reader's `fields`, and the values
                are based on the extractor of each field.
        '''
        self._reject_extractors(extract.CSV, extract.XML)
        if isinstance(source, URIRef):
            subject = source
            metadata = {}
        elif isinstance(source, bytes):
            raise NotImplementedError()
        else:
            subject, metadata = source
        yield self._document_from_subject(subject, metadata)

    def document_subjects(self, graph: Graph) -> Iterable[Subject]:
        ''' Override this function to return all subjects (i.e., first part of RDF triple) 
        with which to search for data in the RDF graph.
        Typically, such subjects are identifiers or urls.
        
        Parameters:
            graph: the graph to parse
        
        Returns:
            generator or list of nodes
        '''
        return graph.subjects()

    def _document_from_subject(self, subject: Subject, metadata: Dict) -> Document:
        return {field.name: field.extractor.apply(
                graph=self.graph, subject=subject, metadata=metadata
            ) for field in self.fields}
