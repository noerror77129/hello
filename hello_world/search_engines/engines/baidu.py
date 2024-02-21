from ..engine import SearchEngine
from ..config import PROXY, TIMEOUT, FAKE_USER_AGENT
from ..utils import unquote_url,decode_bytes
from bs4 import BeautifulSoup
from .. import output as out
from .. import config as cfg
from time import sleep
from random import uniform as random_uniform
from ..results import SearchResults

class Baidu(SearchEngine):
    '''Searches baidu.com'''
    def __init__(self, proxy=PROXY, timeout=TIMEOUT):
        super(Baidu, self).__init__(proxy, timeout)
        self._base_url = u'http://www.baidu.com'
        self.set_headers({"Accept-Language": "zh-CN,zh;q=0.9,eo;q=0.8,en;q=0.7,is;q=0.6"})
        self._delay = (2, 6)

    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'div.result.c-container.xpath-log.new-pmd[mu]',  # 获取网站URL文本
            'title': 'h3.c-title',  # 获取标题文本
            'text': 'span.content-right_8Zs40',  # 获取正文文本
            'links': 'div.result.c-container.xpath-log.new-pmd',  # 获取特定 div 内的所有链接
            'next': 'a:-soup-contains("下一页")'  # 获取“下一页”的链接

        }

        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and qsuery.'''
        # self._get_page(self._base_url)
        url = u'{}/s?wd={}'.format(self._base_url, self._query)
        print(url)
        return {'url':url, 'data':None}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        next_page = self._get_tag_item(tags.select_one(selector), 'href')
        url = None
        if next_page:
            url = (self._base_url + next_page) 
        return {'url':url, 'data':None}

    def _get_url(self, tag):
        '''Returns the URL of search results items.'''
        selector = self._selectors('url')
        soup = BeautifulSoup(str(tag), 'html.parser')
        url_element = soup.select_one(selector)
        url_value = url_element['mu'] if url_element else None
        return unquote_url(url_value)

    # def search(self, query, pages=20): 
    #     '''Queries the search engine, goes through the pages and collects the results.
        
    #     :param query: str The search query  
    #     :param pages: int Optional, the maximum number of results pages to search  
    #     :returns SearchResults object
    #     '''
    #     out.console('Searching.................. {}'.format(self.__class__.__name__))
    #     self._query = decode_bytes(query)
    #     self.results = SearchResults()
    #     request = self._first_page()
    #     retry = 3
    #     for page in range(1, pages + 1):
    #         try:
    #             response = self._get_page(request['url'], request['data'])
    #             if not self._is_ok(response):
    #                 break
    #             tags = BeautifulSoup(response.html, "html.parser")
    #             items = self._filter_results(tags)
    #             self._collect_results(items)
                
    #             msg = 'page: {:<8} links: {}'.format(page, len(self.results))
    #             out.console(msg, end='')
    #             request = self._next_page(tags)
    #             # print("\nnext:",request['url'])
    #             if not request['url']:
    #                 if retry < 1:
    #                     break
    #                 sleep(random_uniform(*self._delay))
    #                 page = page - 1
    #                 retry = retry - 1
    #                 continue
    #             retry = 3
    #             if page < pages:
    #                 sleep(random_uniform(*self._delay))
    #         except KeyboardInterrupt:
    #             print("error")
    #             break
    #     out.console('', end='')
    #     return self.results