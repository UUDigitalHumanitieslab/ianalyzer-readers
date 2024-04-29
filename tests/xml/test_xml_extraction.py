import os
import re

from ianalyzer_readers.readers.xml import XMLReader
from ianalyzer_readers.extract import XML
from ianalyzer_readers.readers.core import Field
from ianalyzer_readers.utils import XMLTag, ParentTag, FindParentTag, SiblingTag


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
    extractor = XML(XMLTag('character'))
    reader = make_test_reader(extractor, XMLTag('play'), XMLTag('lines'), basic_doc, tmpdir)
    assert_extractor_output(reader, 'HAMLET')


def test_xml_re_pattern_tag(tmpdir):
    extractor = XML(XMLTag(re.compile(r'ch.r')))
    reader = make_test_reader(extractor, XMLTag('play'), XMLTag('lines'), basic_doc, tmpdir)
    assert_extractor_output(reader, 'HAMLET')


def test_xml_transform(tmpdir):
    extractor = XML(XMLTag('character'), transform=str.title)
    reader = make_test_reader(extractor, XMLTag('play'), XMLTag('lines'), basic_doc, tmpdir)
    assert_extractor_output(reader, 'Hamlet')


def test_xml_no_tag(tmpdir):
    extractor = XML(None)
    reader = make_test_reader(extractor, XMLTag('play'), XMLTag('character'), basic_doc, tmpdir)
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
    extractor = XML(None, attribute='character')
    reader = make_test_reader(extractor, XMLTag('play'), XMLTag('lines'), doc_with_attribute, tmpdir)
    assert_extractor_output(reader, 'HAMLET')

    extractor = XML(XMLTag('l'), attribute='n')
    reader = make_test_reader(extractor, XMLTag('play'), XMLTag('lines'), doc_with_attribute, tmpdir)
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
    extractor = XML(None, flatten=True)
    reader = make_test_reader(extractor, XMLTag('play'), XMLTag('lines'), doc_multiline, tmpdir)
    expected = 'My hour is almost come, When I to sulph\'rous and tormenting flames Must render up myself.'
    assert_extractor_output(reader, expected)


def test_xml_multiple(tmpdir):
    extractor = XML(XMLTag('l'), multiple=True)
    reader = make_test_reader(extractor, XMLTag('play'), XMLTag('lines'), doc_multiline, tmpdir)
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


def test_xml_parent_tag(tmpdir):
    extractor = XML(ParentTag(), attribute='n')
    reader = make_test_reader(extractor, XMLTag('play'), XMLTag('lines'), doc_nested, tmpdir)
    assert_extractor_output(reader, 'V')

    extractor = XML(ParentTag(2), attribute='n')
    reader = make_test_reader(extractor, XMLTag('play'), XMLTag('lines'), doc_nested, tmpdir)
    assert_extractor_output(reader, 'I')


def test_xml_find_parent_tag(tmpdir):
    extractor = XML(FindParentTag('act'), attribute='n')
    reader = make_test_reader(extractor, XMLTag('play'), XMLTag('lines'), doc_nested, tmpdir)
    assert_extractor_output(reader, 'I')

    extractor = XML(FindParentTag('scene'), attribute='n')
    reader = make_test_reader(extractor, XMLTag('play'), XMLTag('lines'), doc_nested, tmpdir)
    assert_extractor_output(reader, 'V')


def test_xml_multiple_attributes(tmpdir):
    extractor = XML(XMLTag('lines'), attribute='character', multiple=True)
    reader = make_test_reader(extractor, XMLTag('play'), XMLTag('scene'), doc_nested, tmpdir)
    assert_extractor_output(reader, ['HAMLET', 'GHOST'])


def test_xml_recursive(tmpdir):
    extractor = XML(XMLTag('l', recursive=False))
    reader = make_test_reader(extractor, XMLTag('play'), XMLTag('scene'), doc_nested, tmpdir)
    assert_extractor_output(reader, None)

    extractor = XML(XMLTag('l'))
    reader = make_test_reader(extractor, XMLTag('play'), XMLTag('scene'), doc_nested, tmpdir)
    assert_extractor_output(reader, 'Whither wilt thou lead me? Speak, I\'ll go no further.')


def test_xml_tag_list(tmpdir):
    extractor = XML([XMLTag('lines'), XMLTag('l')])
    reader = make_test_reader(extractor, XMLTag('play'), XMLTag('scene'), doc_nested, tmpdir)
    assert_extractor_output(reader, 'Whither wilt thou lead me? Speak, I\'ll go no further.')


def test_xml_transform_soup_func(tmpdir):
    find_location = lambda soup: soup.find_previous_sibling('location')
    extractor = XML(None, transform_soup_func=find_location)
    reader = make_test_reader(extractor, XMLTag('play'), XMLTag('lines'), doc_nested, tmpdir)
    assert_extractor_output(reader, 'A more remote part of the Castle.')


def test_xml_extract_soup_func(tmpdir):
    get_scene_number = lambda soup: soup.find_parent('scene')['n']
    extractor = XML(None, extract_soup_func=get_scene_number)
    reader = make_test_reader(extractor, XMLTag('play'), XMLTag('lines'), doc_nested, tmpdir)
    assert_extractor_output(reader, 'V')


def test_xml_entry_tag_kwargs(tmpdir):
    extractor = XML(XMLTag('l'))
    entry_tag = XMLTag(name='lines', character='GHOST')
    reader = make_test_reader(extractor, XMLTag('play'), entry_tag, doc_nested, tmpdir)
    assert_extractor_output(reader, 'Mark me.')


def test_xml_toplevel_tag_kwargs(tmpdir):
    extractor = XML(XMLTag('l'))
    toplevel_tag = XMLTag(name='act', n='III')
    reader = make_test_reader(extractor, toplevel_tag, XMLTag('lines'), doc_nested, tmpdir)
    assert_extractor_output(reader, 'To be, or not to be, that is the question.')

doc_longer = '''
<?xml version="1.0" encoding="UTF-8"?>
<play>
    <scene>
        <lines>
            <character>HAMLET</character>
            <l>Whither wilt thou lead me? Speak, I'll go no further.</l>
        </lines>
        <lines>
            <character>GHOST</character>
            <l>Mark me.</l>
        </lines>
        <lines>
            <character>HAMLET</character>
            <l>I will.</l>
        </lines>
    </scene>
</play>
'''


def test_xml_sibling_tag(tmpdir):
    extractor = XML(SiblingTag('character'))
    reader = make_test_reader(extractor, XMLTag('play'), XMLTag('l'), doc_longer, tmpdir)
    assert_extractor_output(reader, 'HAMLET')

    extractor = XML([
        XMLTag('character', string='GHOST'),
        SiblingTag('l')
    ])
    reader = make_test_reader(extractor, XMLTag('play'), XMLTag('scene'), doc_longer, tmpdir)
    assert_extractor_output(reader, 'Mark me.')


doc_with_title = '''
<?xml version="1.0" encoding="UTF-8"?>
<play>
    <title>Hamlet</title>
    <lines>
        <character>HAMLET</character>
        <l>Whither wilt thou lead me? Speak, I'll go no further.</l>
    </lines>
</play>
'''


external_doc = '''
<?xml version="1.0" encoding="UTF-8"?>
<bibliography>
    <play>        
        <title>Doctor Faustus</title>
        <author>Christopher Marlowe</author>
    </play>
    <play>
        <title>Hamlet</title>
        <author>William Shakespeare</author>
    </play>
</bibliography>
'''

def test_xml_external_file(tmpdir):
    path = os.path.join(tmpdir, 'test.xml')
    with open(path, 'w') as f:
        f.write(doc_with_title)
    external_path = os.path.join(tmpdir, 'metadata.xml')
    with open(external_path, 'w') as f:
        f.write(external_doc)

    class TestReader(XMLReader):
        data_directory = tmpdir
        tag_toplevel = XMLTag('play')
        tag_entry = XMLTag('lines')

        def sources(self, *args, **kwargs):
            yield path, {'external_file': external_path}
        
        fields = [
            Field(
                name='author',
                extractor=XML(
                    XMLTag('author'),
                    sibling_tag = lambda metadata: XMLTag('title', string=metadata['title']),
                    external_file={'xml_tag_toplevel': XMLTag('bibliography'), 'xml_tag_entry': None}
                )
            ),
            Field(
                name='title',
                extractor=XML(XMLTag('title'), toplevel=True)
            )
        ]
    
    reader = TestReader()
    doc = next(reader.documents())

    assert doc['author'] == 'William Shakespeare'
