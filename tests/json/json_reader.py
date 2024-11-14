from glob import glob
import os

from ianalyzer_readers.extract import JSON
from ianalyzer_readers.readers.core import Field
from ianalyzer_readers.readers.json import JSONReader


class JSONTestReader(JSONReader):
    """
    Example JSON reader for testing, using JSON data from https://github.com/tux255/analyzing-shakespeare
    """

    data_directory = os.path.join(os.path.dirname(__file__), "data")
    document_path = ["SCENE", "SPEECH"]

    def sources(self, **kwargs):
        for filename in glob(f"{self.data_directory}/*.json"):
            full_path = os.path.join(self.data_directory, filename)
            yield full_path

    act = Field("act", JSON("TITLE"))
    scene = Field("scene", JSON("SCENE", "TITLE"))
    character = Field("character", JSON("SCENE", "SPEECH", "SPEAKER"))
    lines = Field(
        "lines", JSON("SCENE", "SPEECH", "LINE"), transform=lambda x: " ".join(x)
    )

    fields = [
        act,
        scene,
        character,
        lines,
    ]
