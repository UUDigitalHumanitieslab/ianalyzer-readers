from os.path import expanduser, realpath, join, dirname, relpath, abspath
from datetime import datetime
from importlib import reload

import pytest

#from ianalyzer.tests.conftest import test_app
from addcorpus import load_corpus


def test_times_source(test_app):
    '''
    Verify that times source files are read correctly.
    '''
    # initialize the corpora module within the testing context
    times_corpus = load_corpus.load_corpus('times')

    print(dirname(__file__), times_corpus.data_directory)

    # Assert that indeed we are drawing sources from the testing folder
    assert dirname(__file__) == abspath(times_corpus.data_directory)


    # Obtain our mock source XML
    sources = times_corpus.sources(
        start=datetime(1970,1,1),
        end=datetime(1970,1,1)
    )


    docs = times_corpus.documents(sources)
    doc1 = next(docs)
    assert len(list(docs)) == 1
    # doc2 = next(docs)
    assert 'Category A' in doc1['category']
    assert doc1['content'] == 'A test paragraph.\nAnd another.'
    assert doc1['date'] == '1970-01-01'



