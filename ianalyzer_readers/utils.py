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
    
    def find_in_soup(self, soup: bs4.BeautifulSoup):
        '''
        Search for this tag using `soup.find()`
        '''
        return soup.find(*self.args, **self.kwargs)
    
    def find_all_in_soup(self, soup: bs4.BeautifulSoup):
        '''
        Search for this tag using `soup.find_all()`
        '''
        return soup.find_all(*self.args, **self.kwargs)
