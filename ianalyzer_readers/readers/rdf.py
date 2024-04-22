from typing import List, Dict, Iterable

from rdflib import BNode, Graph

from .core import Reader, Document, Source


class RDFReader(Reader):
    '''
    A base class for Readers of Resource Description Framework files.
    These could be in Turtle, JSON-LD, RDFXML or other formats,
    see [rdflib parsers](https://rdflib.readthedocs.io/en/stable/plugin_parsers.html)
    '''

    def source2dicts(self, source: Source) -> Iterable[Document]:
        '''
        Given a RDF source file, returns an iterable of extracted documents.

        Parameters:
            source: the source file to extract. This is a string of the file path

        Returns:
            an iterable of document dictionaries. Each of these is a dictionary,
                where the keys are names of this Reader's `fields`, and the values
                are based on the extractor of each field.
        '''
        filename = source
        g = Graph()
        g.parse(filename)
        distinct_subjects = list(set(list(g.subjects())))
        for subject in distinct_subjects:
            yield self._document_from_triples(g, subject)

    def _document_from_triples(self, graph: Graph, subject: BNode) -> dict:
        return {field.name: field.extractor.apply(
                subject=subject, graph=graph, metadata={}) for field in self.fields}
