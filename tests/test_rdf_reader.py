from .rdf_reader import TestRDFReader

from .test_csvcorpus import target_documents


def test_rdf_number_documents():
    reader = TestRDFReader()
    docs = reader.documents()
    assert len(list(docs)) == 7


def test_rdf_document_content():
    reader = TestRDFReader()
    docs = reader.documents()
    for doc, target in zip(docs, target_documents):
        for key in target.keys():
            assert doc.get(key) == target.get(key)
