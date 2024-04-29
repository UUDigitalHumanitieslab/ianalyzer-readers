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
    
    def find_in_soup(self, soup: bs4.element.Tag):
        '''
        Search for this tag using `soup.find()`
        '''
        return soup.find(*self.args, **self.kwargs)
    
    def find_all_in_soup(self, soup: bs4.element.Tag):
        '''
        Search for this tag using `soup.find_all()`
        '''
        return soup.find_all(*self.args, **self.kwargs)

class ParentTag(XMLTag):
    '''
    An XMLTag that will select a parent tag based on a fixed level.
    '''

    def __init__(self, level=1):
        self.level = level

    def find_in_soup(self, soup: bs4.element.PageElement):
        count = 0
        while count < self.level:
            soup = soup.parent if soup else None
            count += 1

        return soup
    
    def find_all_in_soup(self, soup: bs4.element.PageElement):
        parent = self.find_in_soup(soup)
        return [parent] if parent else []


class FindParentTag(XMLTag):
    '''
    An XMLTag that will find a parent tag based on query arguments.
    '''

    def find_in_soup(self, soup: bs4.element.PageElement):
        return soup.find_parent(*self.args, **self.kwargs)
    
    def find_all_in_soup(self, soup: bs4.Tag):
        return soup.find_parents(*self.args, **self.kwargs)

