from typing import Iterable

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
        document_subjects = self.document_subjects(g)
        for subject in document_subjects:
            yield self._document_from_subject(g, subject)

    def document_subjects(self, graph: Graph) -> list:
        ''' override this function such that each subject can be used to
        retrieve a separate document in the resulting index
        Parameters:
            graph: the graph to parse
        Returns:
            list of nodes
        '''
        return list(graph.subjects())

    def _document_from_subject(self, graph: Graph, subject: BNode) -> dict:
        return {field.name: field.extractor.apply(graph=graph, subject=subject) for field in self.fields}
