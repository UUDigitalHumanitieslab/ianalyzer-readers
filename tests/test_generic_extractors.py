import pytest
from ianalyzer_readers.extract import (
    Constant, Combined, Backup, Choice, Metadata, Pass, Order
)

def test_constant_extractor():
    extractor = Constant('test')
    output = extractor.apply()
    assert output == 'test'


def test_combined_extractor():
    extractor = Combined(
        Constant(1),
        Constant(2),
        Constant(3)
    )
    output = extractor.apply()
    assert output == (1, 2, 3)


def test_backup_extractor():
    extractor = Backup(
        Constant(None),
        Constant(''),
        Constant('test')
    )
    output = extractor.apply()
    assert output == 'test'


def test_choice_extractor():
    extractor = Choice(
        Constant(
            'first',
            applicable=Metadata('check'),
        ),
        Constant(
            'second'
        )
    )

    output = extractor.apply(metadata={'check': True})
    assert output == 'first'
    output = extractor.apply(metadata={'check': False})
    assert output == 'second'


def test_metadata_extractor():
    extractor = Metadata('test')
    output = extractor.apply(metadata={'test': 'testing'})
    assert output == 'testing'


def test_pass_extractor():
    extractor = Pass(
        Constant('test'),
    )
    output = extractor.apply()
    assert output == 'test'
    
    # typical usage with transform argument
    extractor = Pass(
        Constant('test'),
        transform=str.upper,
    )
    output = extractor.apply()
    assert output == 'TEST'


def test_order_extractor():
    extractor = Order()
    output = extractor.apply(index=1)
    assert output == 1


def test_extractor_applicable_extractor():
    extractor = Constant('test', applicable=Metadata('testing'))
    assert extractor.apply(metadata={'testing': True}) == 'test'
    assert extractor.apply(metadata={'testing': False}) == None


def test_extractor_applicable_callable():
    with pytest.warns(DeprecationWarning):
        extractor = Constant('test', applicable=lambda metadata: metadata['testing'])
    assert extractor.apply(metadata={'testing': True}) == 'test'
    assert extractor.apply(metadata={'testing': False}) == None
