import os

from rdflib import URIRef

from ianalyzer_readers.readers.rdf import RDFReader
from ianalyzer_readers.readers.core import Field
from ianalyzer_readers.extract import Choice, RDF

here = os.path.abspath(os.path.dirname(__file__))


def parse_date(input):
    return input


def extract_speaker_name(input):
    return input


def extract_party_name(input):
    return input


def get_speech_text(input):
    return input


def get_source_language(input):
    return input


def construct_url(input):
    return input


class EuParlRDFReader(RDFReader):
    """
    Example XML reader for testing
    """

    data_directory = os.path.join(here, 'ttl_example')

    def sources(self, **kwargs):
        for filename in os.listdir(self.data_directory):
            full_path = os.path.join(self.data_directory, filename)
            yield full_path

    id = Field(
        'id',
        RDF(
            URIRef('http://purl.org/linkedpolitics/eu/plenary/'),
            node_type='subject',
        ),
    )

    date = Field(
        'date',
        RDF(
            URIRef('http://purl.org/linkedpolitics/eu/plenary/'),
            node_type='subject',
            transform=parse_date
        )
    )

    speaker = Field(
        'speaker',
        RDF(
            URIRef('http://purl.org/linkedpolitics/vocabulary/unclassifiedMetadata'),
            transform=extract_speaker_name
        )
    )
    party = Field(
        'party',
        RDF(
            URIRef('http://purl.org/linkedpolitics/vocabulary/unclassifiedMetadata'),
            transform=extract_party_name
        )
    )
    speech = Field(
        'speech',
        Choice(
            RDF(
                URIRef('http://purl.org/linkedpolitics/vocabulary/translatedText'),
                transform=get_speech_text
            ),
            RDF(
                URIRef('http://purl.org/linkedpolitics/vocabulary/translatedText'),
                transform=get_speech_text
            )
        )
    )
    source_language = Field(
        RDF(
            URIRef('http://purl.org/linkedpolitics/vocabulary/translatedText'),
            transform=get_source_language
        )
    )
    url = Field(
        RDF(
            URIRef('http://purl.org/linkedpolitics/eu/plenary/'),
            node_type='subject',
            transform=construct_url
        )
    )

    fields = [id, date, speaker, party, speech, source_language, url]
