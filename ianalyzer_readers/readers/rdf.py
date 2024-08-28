'''
This module defines a Resource Description Framework (RDF) reader.

Extraction is based on the [rdflib library](https://rdflib.readthedocs.io/en/stable/index.html).
'''

import logging
from typing import Iterable, Union

from rdflib import BNode, Graph, Literal, URIRef

from .core import Reader, Document, Source
import ianalyzer_readers.extract as extract

logger = logging.getLogger('ianalyzer-readers')


class RDFReader(Reader):
    '''
    A base class for Readers of Resource Description Framework files.
    These could be in Turtle, JSON-LD, RDFXML or other formats,
    see [rdflib parsers](https://rdflib.readthedocs.io/en/stable/plugin_parsers.html).

    Note that this reader expects all relevant information to be in one file.
    If you have RDF data spread over multiple files,
    you can refer to the `combine_rdf_files` utility funciton to combine them.
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
        
        if type(source) == bytes:
            raise Exception('The current reader cannot handle sources of bytes type, provide a file path as string instead')
        (filename, metadata) = source

        logger.info(f"parsing {filename}")
        g = Graph()
        g.parse(filename)
        document_subjects = self.document_subjects(g)
        for subject in document_subjects:
            yield self._document_from_subject(g, subject, metadata)
            
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

    def _document_from_subject(self, graph: Graph, subject: Union[BNode, Literal, URIRef], metadata: dict) -> dict:
        return {field.name: field.extractor.apply(graph=graph, subject=subject, metadata=metadata) for field in self.fields}


def get_uri_value(node: URIRef) -> str:
    ''' a utility function to extract the last part of a uri
    For instance, if the input is URIRef('https://purl.org/mynamespace/ernie'),
    the function will return 'ernie'

    Parameters:
        node: an URIRef input node
    
    Returns:
        a string with the last element of the uri
       '''
    return node.n3().strip('<>').split('/')[-1]

def combine_rdf_files(files: list[str], output_file: str):
    ''' A utility function to combine multiple rdf files into one
    
    Parameters:
        files: a list of filepaths, as for instance returned by the glob module
        output_file: the filename of the combined file
    
    Usage:
    ```python
    from glob import glob
    from ianalyer_readers.readers.rdf import combine_rdf_files

    files = glob('my/directory/*.ttl')
    combine_rdf_files(files, 'my/directory/output.rdf')
    ```
    '''
    graph = Graph()
    for rdf_file in files:
        graph.parse(rdf_file)
    graph.serialize(destination=output_file)