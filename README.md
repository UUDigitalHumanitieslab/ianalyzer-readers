# I-analyzer Readers

`ianalyzer-readers` is a python module to extract data from XML, HTML, CSV or XLSX files.

This module was originally created for [I-analyzer](https://github.com/UUDigitalHumanitieslab/I-analyzer), a web application that extracts data from a variety of datasets, indexes them and presents a search interface. To do this, we wanted a way to extract data from source files without having to write a new script "from scratch" for each dataset, and an API that would work the same regardless of the source file type.

The basic usage is that you will use the utilities in this package to create a "reader" class. You specify what your data looks like, and then call the `documents()` method of the reader to get an iterator of documents - where each document is a flat dictionary of key/value pairs.

**State of development:** this module is currently under development and lacks proper unit tests and documentation.

## Prerequisites

Requires Python 3.8 or later.

## Contents

[ianalyzer_readers](./ianalyzer_readers/) contains the source code for the package. [tests](./tests/) contains unit tests.

## When to use this package

This package is *not* a replacement for more general-purpose libraries like `csv` or Beautiful Soup - it is a high-level interface on top of those libraries.

Our primary use for this package is to pre-process data for I-analyzer, but you may find other uses for it.

Using this package makes sense if you want to extract data in the shape that it is designed for (i.e., a list of flat dictionaries).

What we find especially useful is that all subclasses of `Reader` have the same interface - regardless of whether they are processing CSV, XML, HTML, or XLSX data. That common interface is crucial in an application that needs to process corpora from different source types, like I-analyzer.

## Usage

*Usage documentation is not yet complete.*

Typical use is that, for each dataset you want to extract, you create a subclass of `Reader` and define required properties. See the [CSV test corpus](./tests/mock_csv_corpus.py) for an example.

After defining the class for your dataset, you can call the `documents()` method to get a generator of document dictionaries.

## Licence

This code is shared under an MIT licence. See [LICENSE](./LICENSE) for more information.
