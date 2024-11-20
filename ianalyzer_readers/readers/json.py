import json
from os.path import isfile
from typing import Iterable, Optional, Union

from pandas import json_normalize
from requests import Response

from .core import Reader, Document, Source
import ianalyzer_readers.extract as extract

class JSONReader(Reader):
    """
    A base class for Readers of JSON encoded data.

    The reader can either be used on a collection of JSON files, in which each file represents a document,
    or for a JSON file containing lists of documents.

    If the attributes `record_path` and `meta` are passed, they are used as arguments to [pandas.json_normalize](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.json_normalize.html) to unnest the JSON data

    Attributes:
        record_path: a keyword or list of keywords by which a list of documents can be extracted from a large JSON file; do not define if the corpus is structured as one file per document
        meta: a list of keywords, or list of lists of keywords, by which metadata for each document can be located
    """

    record_path: Optional[list[str]] = None
    meta: Optional[list[Union[str, list[str]]]] = None

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

        if self.record_path and self.meta:
            documents = json_normalize(json_data, self.record_path, self.meta).to_dict(
                'records'
            )
        else:
            documents = list(json_data)
        self._reject_extractors(extract.XML, extract.CSV, extract.RDF)

        for doc in documents:
            field_dict = {
                field.name: field.extractor.apply(
                    doc, metadata=metadata, *nargs, **kwargs
                )
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
