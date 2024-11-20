from glob import glob
import os

from ianalyzer_readers.extract import JSON
from ianalyzer_readers.readers.core import Field
from ianalyzer_readers.readers.json import JSONReader


def merge_lines(lines: list | str) -> str:
    if isinstance(lines, list):
        return "\n".join(lines)
    return lines


class JSONTestReader(JSONReader):
    """
    Example JSON reader for testing, using JSON data from https://github.com/tux255/analyzing-shakespeare
    """

    data_directory = os.path.join(os.path.dirname(__file__), "data")
    record_path = ["SCENE", "SPEECH"]
    meta = ["TITLE", ["SPEECH", "TITLE"], ["SPEECH", "STAGEDIR"]]

    def sources(self, **kwargs):
        for filename in glob(f"{self.data_directory}/*.json"):
            full_path = os.path.join(self.data_directory, filename)
            yield full_path

    act = Field("act", JSON("TITLE"))
    scene = Field("scene", JSON("SPEECH.TITLE"))
    character = Field("character", JSON("SPEAKER"))
    lines = Field("lines", JSON("LINE", transform=merge_lines))
    stage_dir = Field("stage_direction", JSON("SPEECH.STAGEDIR", transform=merge_lines))

    fields = [act, scene, character, lines, stage_dir]
