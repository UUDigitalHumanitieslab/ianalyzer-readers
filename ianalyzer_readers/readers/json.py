import json
from os.path import isfile
from typing import Iterable

from requests import Response

from .core import Reader, Document, Source
import ianalyzer_readers.extract as extract

class JSONReader(Reader):
    """
    A base class for Readers of JSON encoded data.

    Attributes:
        document_path (Iterable[str]): a keyword or list of keywords by which a list of documents can be extracted
    """

    document_path = []

    def source2dicts(self, source: Source, *nargs, **kwargs) -> Iterable[Document]:
        """
        Given a Python dictionary, returns an iterable of extracted documents.

        Parameters:
            source: the input data

        Returns:
            list of documents
        """
        if type(source) == tuple:
            metadata = source[1]
            json_data = self._get_json_data(source[0])
        else:
            metadata = None
            json_data = self._get_json_data(source)
        data = self._parse_json_tree(json_data)
        self._reject_extractors(extract.XML, extract.CSV, extract.RDF)

        field_dict = {
            field.name: field.extractor.apply(data, metadata=metadata, *nargs, **kwargs)
            for field in self.fields
        }

        yield field_dict

    def _get_json_data(self, source: Source) -> dict:
        if isfile(source):
            with open(source, "r") as f:
                return json.load(f)
        elif type(source) == Response:
            return source.json()
        elif type(source) == bytes:
            return json.loads(source)
        else:
            raise Exception("Unexpected source type for JSON Reader")

    def _parse_json_tree(self, data: dict, output: dict = {}) -> Iterable[dict]:
        """Step through the dict recursively, collecting all data
        Documents can be members of a list
        """
        while len(self.document_path):
            document_key = self.document_path.pop(0)
            data_keys = data.keys()
            for data_key in data_keys:
                if data_key != document_key:
                    output[data_key] == data[data_key]
            try:
                path_content = data[document_key]
            except KeyError:
                raise Exception("path to identify documents is invalid")
            if type(path_content) == list:
                new_data = path_content.pop(0)
                self._parse_json_tree(new_data, output)
            else:
                output[document_key] = path_content
        return output
