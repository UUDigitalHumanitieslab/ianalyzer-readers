from typing import Iterable, Optional
import bs4

class XMLTag:
    '''
    Describes a tag in an XML tree.

    Parameters:
        *args: positional arguments to pass on to BeautifulSoup.find() (and similar methods)
        **kwargs: named arguments to pass on to BeautifulSoup.find() (and similar methods)
    '''
    
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
    
    def find_next_in_soup(self, soup: bs4.element.PageElement) -> Optional[bs4.PageElement]:
        return next((tag for tag in self.find_in_soup(soup)), None)

    def find_in_soup(self, soup: bs4.element.PageElement) -> Iterable[bs4.PageElement]:
        return soup.find_all(*self.args, **self.kwargs)


class ParentTag(XMLTag):
    '''
    An XMLTag that will select a parent tag based on a fixed level.
    '''

    def __init__(self, level=1):
        self.level = level

    def find_in_soup(self, soup: bs4.PageElement):
        count = 0
        while count < self.level:
            soup = soup.parent if soup else None
            count += 1

        yield soup


class FindParentTag(XMLTag):
    '''
    An XMLTag that will find a parent tag based on query arguments.
    '''

    def find_in_soup(self, soup: bs4.PageElement):
        return soup.find_parents(*self.args, **self.kwargs)
    

class SiblingTag(XMLTag):
    '''
    An XMLTag that will look in an element's siblings.
    '''

    def find_in_soup(self, soup: bs4.PageElement):
        for tag in soup.find_next_siblings(*self.args, **self.kwargs):
            yield tag
        
        for tag in soup.find_previous_siblings(*self.args, **self.kwargs):
            yield tag
