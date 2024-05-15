import csv
import os
from glob import glob

from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF

from ianalyzer_readers.readers.rdf import RDFReader
from ianalyzer_readers.readers.core import Field
from ianalyzer_readers.extract import RDF as RDFExtractor

here = os.path.abspath(os.path.dirname(__file__))

ns_character = "http://example.org/shakespeare/character"
ns_speaker = "http://example.org/shakespeare/hasSpeaker"
ns_text = "http://example.org/shakespeare/hasText"
ns_line_id = "http://example.org/shakespeare/line"


class TestRDFReader(RDFReader):
    """
    Example XML reader for testing
    """

    data_directory = os.path.join(here, 'ttl_example')

    def document_subects(self, graph: Graph):
        ''' get all subjects which do not contain objects with a RDF.rest predicate '''
        have_rest = list(graph.subjects(RDF.rest))
        subjects = [subj for subj in list(
            graph.subjects) if subj not in have_rest]
        return subjects

    def sources(self, **kwargs):
        for filename in glob(f'{self.data_directory}/*.ttl'):
            full_path = os.path.join(self.data_directory, filename)
            yield full_path

    character = Field(
        'character',
        RDFExtractor(
            URIRef(ns_speaker),
            transform=lambda k: str(k)
        )
    )
    lines = Field(
        'lines',
        RDFExtractor(
            URIRef(ns_text),
            multiple=True
        )
    )

    fields = [character, lines]


def create_test_data():
    graph = Graph()
    with open('./tests/csv_example/example.csv', 'r') as f:
        reader = csv.DictReader(f)
        character = ''
        for index, row in enumerate(reader):
            identifier = f'{ns_line_id}/hamlet-actI-scene5-{index}'
            if character == row['character']:
                graph.add((URIRef(identifier),
                           RDF.first, Literal(row['line'])))
            else:
                if index > 0:
                    # remove the reference to the next line if this is a new speaker
                    graph.remove(rest_triple)
                character = row['character']
                graph.add((URIRef(identifier),
                           RDF.first, Literal(row['line'])))

            graph.add((URIRef(identifier),
                       URIRef(ns_speaker), URIRef(f'{ns_character}/{character}')))

            next_id = f'{ns_line_id}/hamlet-actI-scene5-{index+1}'
            rest_triple = (URIRef(identifier),
                           RDF.rest, URIRef(next_id))
            graph.add(rest_triple)

        graph.remove((rest_triple))

        graph.serialize(destination='./tests/ttl_example/hamlet.ttl')
