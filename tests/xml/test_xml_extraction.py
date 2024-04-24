import os
import re

from ianalyzer_readers.readers.xml import XMLReader
from ianalyzer_readers.extract import XML
from ianalyzer_readers.readers.core import Field


def make_test_reader(extractor, toplevel_tag, entry_tag, doc, tmpdir):
    path = os.path.join(tmpdir, 'test.xml')
    with open(path, 'w') as f:
        f.write(doc)

    class TestReader(XMLReader):
        data_directory = tmpdir
        tag_toplevel = toplevel_tag
        tag_entry = entry_tag

        def sources(self, *args, **kwargs):
            yield path
        
        fields = [
            Field(name='test', extractor=extractor)
        ]
    
    return TestReader()

basic_doc = '''
<?xml version="1.0" encoding="UTF-8"?>
<play>
    <lines>
        <character>HAMLET</character>
        <l>Whither wilt thou lead me? Speak, I'll go no further.</l>
    </lines>
</play>
'''


def assert_extractor_output(reader, expected):
    doc = next(reader.documents())
    assert doc['test'] == expected


def test_xml_basic(tmpdir):
    extractor = XML(tag='character')
    reader = make_test_reader(extractor, 'play', 'lines', basic_doc, tmpdir)
    assert_extractor_output(reader, 'HAMLET')


def test_xml_re_pattern_tag(tmpdir):
    extractor = XML(tag=re.compile(r'ch.r'))
    reader = make_test_reader(extractor, 'play', 'lines', basic_doc, tmpdir)
    assert_extractor_output(reader, 'HAMLET')


def test_xml_transform(tmpdir):
    extractor = XML(tag='character', transform=str.title)
    reader = make_test_reader(extractor, 'play', 'lines', basic_doc, tmpdir)
    assert_extractor_output(reader, 'Hamlet')


def test_xml_no_tag(tmpdir):
    extractor = XML()
    reader = make_test_reader(extractor, 'play', 'character', basic_doc, tmpdir)
    assert_extractor_output(reader, 'HAMLET')


def test_xml_parent_level(tmpdir):
    extractor = XML('character', parent_level=1)
    reader = make_test_reader(extractor, 'play', 'l', basic_doc, tmpdir)
    assert_extractor_output(reader, 'HAMLET')


doc_with_attribute = '''
<?xml version="1.0" encoding="UTF-8"?>
<play>
    <lines character='HAMLET'>
        <l n="1">Whither wilt thou lead me? Speak, I'll go no further.</l>
    </lines>
</play>
'''


def test_xml_attribute(tmpdir):
    extractor = XML(tag=None, attribute='character')
    reader = make_test_reader(extractor, 'play', 'lines', doc_with_attribute, tmpdir)
    assert_extractor_output(reader, 'HAMLET')

    extractor = XML(tag='l', attribute='n')
    reader = make_test_reader(extractor, 'play', 'lines', doc_with_attribute, tmpdir)
    assert_extractor_output(reader, '1')

doc_multiline = '''
<?xml version="1.0" encoding="UTF-8"?>
<play>
    <lines character="GHOST">
        <l>My hour is almost come,</l>
        <l>When I to sulph'rous and tormenting flames</l>
        <l>Must render up myself.</l>
    </lines>
</play>
'''

def test_xml_flatten(tmpdir):
    extractor = XML(tag=None, flatten=True)
    reader = make_test_reader(extractor, 'play', 'lines', doc_multiline, tmpdir)
    expected = 'My hour is almost come, When I to sulph\'rous and tormenting flames Must render up myself.'
    assert_extractor_output(reader, expected)


def test_xml_multiple(tmpdir):
    extractor = XML(tag='l', multiple=True)
    reader = make_test_reader(extractor, 'play', 'lines', doc_multiline, tmpdir)
    expected = [
        'My hour is almost come,',
        'When I to sulph\'rous and tormenting flames',
        'Must render up myself.'
    ]
    assert_extractor_output(reader, expected)



doc_nested = '''
<?xml version="1.0" encoding="UTF-8"?>
<play>
    <act n="I">
        <scene n="V">
            <location>A more remote part of the Castle.</location>
            <lines character="HAMLET">
                <l>Whither wilt thou lead me? Speak, I'll go no further.</l>
            </lines>
            <lines character="GHOST">
                <l>Mark me.</l>
            </lines>
        </scene>
    </act>
    <act n="III">
        <scene n="I">
            <location>A room in the Castle.</location>
            <lines character="HAMLET">
                <l>To be, or not to be, that is the question.</l>
            </lines>
        </scene>
    </act>
</play>
'''


def test_xml_recursive(tmpdir):
    extractor = XML(tag='l')
    reader = make_test_reader(extractor, 'play', 'scene', doc_nested, tmpdir)
    assert_extractor_output(reader, None)

    extractor = XML(tag='l', recursive=True)
    reader = make_test_reader(extractor, 'play', 'scene', doc_nested, tmpdir)
    assert_extractor_output(reader, 'Whither wilt thou lead me? Speak, I\'ll go no further.')


def test_xml_tag_list(tmpdir):
    extractor = XML(tag=['lines', 'l'])
    reader = make_test_reader(extractor, 'play', 'scene', doc_nested, tmpdir)
    assert_extractor_output(reader, 'Whither wilt thou lead me? Speak, I\'ll go no further.')


def test_xml_transform_soup_func(tmpdir):
    find_location = lambda soup: soup.find_previous_sibling('location')
    extractor = XML(tag=None, transform_soup_func=find_location)
    reader = make_test_reader(extractor, 'play', 'lines', doc_nested, tmpdir)
    assert_extractor_output(reader, 'A more remote part of the Castle.')


def test_xml_extract_soup_func(tmpdir):
    get_scene_number = lambda soup: soup.find_parent('scene')['n']
    extractor = XML(tag=None, extract_soup_func=get_scene_number)
    reader = make_test_reader(extractor, 'play', 'lines', doc_nested, tmpdir)
    assert_extractor_output(reader, 'V')


def test_xml_entry_tag_dict(tmpdir):
    extractor = XML('l')
    entry_tag = {'name': 'lines', 'character': 'GHOST'}
    reader = make_test_reader(extractor, 'play', entry_tag, doc_nested, tmpdir)
    assert_extractor_output(reader, 'Mark me.')


def test_xml_toplevel_tag_dict(tmpdir):
    extractor = XML('l')
    toplevel_tag = {'name': 'act', 'n': 'III'}
    reader = make_test_reader(extractor, toplevel_tag, 'lines', doc_nested, tmpdir)
    assert_extractor_output(reader, 'To be, or not to be, that is the question.')

