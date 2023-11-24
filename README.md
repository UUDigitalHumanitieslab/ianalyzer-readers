# I-analyzer extractors

`i-analyzer-extractors` is a python module to extract data from XML, HTML or CSV files.

This system was original created for I-analyzer, a web application that extracts data from source files, indexes them and presents a search interface. To do this, we wanted a way to extract data from source files without having to write a new script "from scratch" for each dataset.

The basic usage is that you will use the utilities in this package to create a "reader" class. You specify what your data looks like, and then call the `documents()` method of the reader to get an iterator of documents - where each document is a flat dictionary of key/value pairs.

## Prerequisites

Required Python 3.8 or later. You can install dependencies with `pip install -r requirements.txt`

## Contents

[src](./src/) contains the source code for the package. [src/tests](./src/tests/) contains unit tests.

## Usage

This package is *not* a replacement for more low-level libraries like `csv` or Beautiful Soup - it is a high-level layer on top of those libraries.

Our primary use for this package is to pre-process data for I-analyzer, but you may find other uses for it.

Using this package makes sense if you want to extract data in the shape that it is designed for (i.e., a list of flat dictionaries).

What we find especially useful is that all subclasses of `Reader` have the same interface - regardless of whether they are processing CSV, XML or HTML data. That common interface is crucial in an application that needs to process corpora from different source types, like I-analyzer.

## Licence

This code is shared under an MIT licence. See [LICENSE](./LICENSE) for more information.