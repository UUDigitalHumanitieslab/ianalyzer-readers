import json
from os.path import isfile
import requests
from typing import Iterable

from .core import Reader, Document, Source
import ianalyzer_readers.extract as extract

class JSONReader(Reader):
    '''
    A base class for Readers of JSON encoded data.
    '''

    def source2dicts(self, source: Source, *nargs, **kwargs) -> Iterable[Document]:
        '''
        Given a Python dictionary, returns an iterable of extracted documents. 
        
        Parameters:
            source: a 
        '''
        if type(source) == tuple:
            metadata = source[1]
            json_data = self._get_json_data(source[0])
        else:
            metadata = None
            json_data = self._get_json_data(source)
        self._reject_extractors(extract.XML, extract.CSV, extract.RDF)

        field_dict = {
            field.name: field.extractor.apply(
                json_data, metadata=metadata, *nargs, **kwargs
            )
            for field in self.fields
        }

        yield field_dict

    def _get_json_data(self, source: Source) -> dict:
        if type(source) == bytes:
            return source
        elif isfile(source):
            return json.load(source)
        else:
            response = requests.get(source)
            return response.json()
