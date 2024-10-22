from . import html_reader
import csv

def test_csv_export(tmpdir):
    reader = html_reader.HamletHTMLReader()
    path = tmpdir / 'hamlet.csv'
    reader.export_csv(path)

    with open(path) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        assert csv_reader.fieldnames == reader.fieldnames
        rows = list(row for row in csv_reader)
        assert len(rows) == 7