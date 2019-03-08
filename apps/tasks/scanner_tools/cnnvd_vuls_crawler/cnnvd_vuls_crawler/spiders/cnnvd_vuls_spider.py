import scrapy
from scrapy.http.request import Request
from apps.tasks.scanner_tools.cnnvd_vuls_crawler.cnnvd_vuls_crawler.items import CnnvdVulsCrawlerItem
from urllib.parse import quote
from scrapy_splash import SplashRequest
import re
import logging

# splash lua script1
lua_script_1 = """
function main(splash, args)
    assert(splash:go(args.url))
    assert(splash:wait(args.wait))
    input = splash:select('#qcvCname')
    local search_item = args.search_item
    input:send_text(search_item)
    submit = splash:select('a.bd_b')
    submit:mouse_click()
    assert(splash:wait(args.wait))
    return splash:html()
end
"""

# splash lua script2
lua_script_2 = """
function click_one(splash)
    splash:runjs("click_function = function(){document.querySelector('div.page > a:nth-last-child(2)').click();}")
    splash:wait(1)
    splash:evaljs("click_function()")
    assert(splash:wait(1))
    return splash:html()
end
function reclick(splash, time)
    for i=1,time,1 do
        res = click_one(splash)
    end
    return res
end
function main(splash, args)
    assert(splash:go(args.url))
    assert(splash:wait(args.wait))
    input = splash:select('#qcvCname')
    local search_item = args.search_item
    input:send_text(search_item)
    submit = splash:select('a.bd_b')
    submit:mouse_click()
    assert(splash:wait(args.wait))
    res = reclick(splash,args.click_time)
    return res
end
"""

class CnnvdGithubSpider(scrapy.Spider):
    """
    this spider used to crawl the github vulnerability in cnnvd
    """

    name = 'cnnvd_vuls_spider'

    def __init__(self, module_name=None, module_id=None, module_type= None, latest=False, *args, **kwargs):
        super(CnnvdGithubSpider, self).__init__(*args, **kwargs)
        self.module_id = module_id
        self.module_name = module_name
        self.module_type = module_type
        self.latest = latest

    #  allowed to crawl, if not in this domain ,will forbidden
    allowed_domains = 'cnnvd.org.cn'

    # url information
    start_url = 'http://cnnvd.org.cn/web/vulnerability/querylist.tag'
    detail_url = 'http://www.cnnvd.org.cn/web/xxk/ldxqById.tag?CNNVD='
    # start url： http://www.cnnvd.org.cn/web/vulnerability/querylist.tag
    # after search url： http://www.cnnvd.org.cn/web/vulnerability/queryLds.tag
    # detail vul url： http://www.cnnvd.org.cn/web/xxk/ldxqById.tag?CNNVD=CNNVD-201807-2028
    # url after click next button: http://www.cnnvd.org.cn/web/vulnerability/querylist.tag?pageno=1&repairLd=

    # use lua_script_1 script to search , will give the result to callback function self.parse
    def start_requests(self):
        """
        start a request to splash
        :return: splash request
        """
        # use args to pass the render arguments to SplashRequest object ：
        # lua_source used to defined Lua script
        # wait defined the waiting time
        logging.info("[+] Crawl [%s] vuls now ..." % self.module_name)
        yield SplashRequest(self.start_url,
                            callback=self.parse,
                            endpoint='execute',
                            args={'lua_source': lua_script_1, 'wait': str(5), 'search_item': self.module_name},
                            dont_filter=True
                            )

    def parse(self, response):
        """
        parse the response of the vulnerability result
        :param response:
        :return: item
        """
        # navigate to the detail vul page , then crawl the vuls
        if "CNNVD=CNNVD" in response.url:
            item = CnnvdVulsCrawlerItem()
            details = response.xpath('//div[contains(@class,"detail_xq")]')
            item['vul_name'] = details[0].xpath('./h2//text()').extract_first().strip()
            item['vul_cve'] = details[0].xpath('./ul/li[3]/a//text()').extract_first().strip()
            item['vul_time'] = details[0].xpath('./ul/li[5]/a//text()').extract_first().strip()
            item['vul_level'] = details[0].xpath('./ul/li[2]/a//text()').extract_first().strip()
            # software_name = details[0].xpath('./h2//text()').extract_first().strip()
            # software_name = software_name.split()
            # software_name.pop()
            # item['software_name'] = " ".join(software_name)
            # cve_vul_source = details[0].xpath('./ul/li[last()]/a//text()').extract_first()
            # if cve_vul_source:
            #     item['cve_vul_source'] = cve_vul_source.strip()
            # else:
            #     item['cve_vul_source'] = None
            item['vul_source'] = response.url

            vul_description = response.xpath('//div[contains(@class,"d_ldjj")][1]/p//text()').extract()
            if len(vul_description) >= 1:
                item['vul_description'] = ' '.join([des.strip() for des in vul_description])
                vul_version = vul_description[-1].strip()
                item['software_version'] = self.parse_vul_version(vul_version)
            else:
                item['vul_description'] = None
                item['software_version'] = None

            vul_solution = response.xpath('//div[contains(@class,"d_ldjj") and contains(@class,"m_t_20")][1]/p//text()').extract()
            item['solution'] = ''.join([solution.strip() for solution in vul_solution])

            vul_reference = response.xpath('//div[contains(@class,"d_ldjj") and contains(@class,"m_t_20")][2]/p//text()').extract()
            item['reference'] = ''.join([reference.strip() for reference in vul_reference])

            item['vul_approved'] = '1'
            item['s_name_id'] = self.module_id
            item['vul_type'] = self.module_type
            item['vul_status'] = 'no_poc'

            #  cannot crawl these data. so set them default as None
            item['vul_assets_num'] = None

            search_string = r'\b' + self.module_name.lower() + r'\b'
            if item['vul_cve'] and re.search(search_string, item['vul_name'].lower()):
                yield item

        #  page after search
        if "querylist.tag" in response.url:
            cnnvd_ids = response.xpath('//div[@class="list_list"]/ul/li/div[1]/p/a[1]//text()').extract()

            vul_count = response.xpath('//div[@class="page"]/a[1]//text()').extract_first().strip()
            vul_count = vul_count.split("：")[1]
            vul_count = "".join(vul_count.split(","))
            vul_page_count = int(vul_count)//10 + 1

            # handle only one page
            if vul_page_count == 1:
                for cnnvd_id in cnnvd_ids:
                    #  traverse each vul in the page , give the response to callback function self.parse
                    url = self.detail_url + quote(cnnvd_id)
                    yield Request(url, callback=self.parse, dont_filter=True)

            # handle multiple pages
            else:
                # handle current vuls in the current page
                for cnnvd_id in cnnvd_ids:
                    # traverse each vul in the page , give the response to callback function self.parse
                    url = self.detail_url + quote(cnnvd_id)
                    yield Request(url, callback=self.parse, dont_filter=True)

                # crawl only current page or all pages
                if self.latest == 'False':
                    # handle next page if it exist
                    next_button_text = response.xpath('//div[@class="page"]/a[last()-1]//text()').extract_first()
                    if "下一页" in next_button_text:
                        #  use lua_script_2 script to handle next, give the result to callback function self.parse
                        click_time = response.xpath('//div[@class="page"]//a[@class="page_a"]//text()').extract_first().strip()
                        yield SplashRequest(self.start_url, callback=self.parse, endpoint='execute',
                                            args={
                                                'lua_source': lua_script_2,
                                                'wait': str(5),
                                                'search_item': self.module_name,
                                                'click_time': click_time
                                            },
                                            dont_filter=True
                                            )

    @staticmethod
    def parse_vul_version(vul_string):
        """
        parse the software version
        :param vul_string:
        :return:
        """
        vul_string = re.sub(r'[:-]', '.', vul_string)
        p1 = re.compile(r'[0-9]\d*[.\d]+[^版本]*版本至[0-9]\d*[.\d]+[^版本]*版本|[0-9]\d*[.\d]+[^版本]*版本')
        p2 = re.compile(r'(?P<version>[a-zA-Z.\d]+)[^版本]*版本')
        p3 = re.compile(r'(?P<version1>[a-zA-Z.\d]+)之前的?(?P<version2>[a-zA-Z.\d]+)版本')
        p4 = re.compile(r'(?P<version1>[a-zA-Z.\d]+)(版本)?至(?P<version2>[a-zA-Z.\d]+)版本')
        p5 = re.compile(r'(?P<version1>[a-zA-Z.\d]+)和(?P<version2>[a-zA-Z.\d]+)版本')
    
        version_string_list = p1.findall(vul_string)
        version_list = []
        if version_string_list:
            for version_string in version_string_list:
                if '及之前' in version_string:
                    version = "0<=" + p2.sub(r'\g<version>', version_string)
                    version_list.append(version)
                elif '之前' in version_string:
                    if p3.search(version_string):
                        version_start = p3.sub(r'\g<version2>', version_string)
                        version_end = p3.sub(r'\g<version1>', version_string)
                        if version_start[-1] == 'x' or version_start[-1] == 'X':
                            version_start = version_start[0:-1] + '0'
                        version = version_start + "--" + version_end
                    else:
                        version = "0<" + p2.sub(r'\g<version>', version_string)
                    version_list.append(version)
                elif '至' in version_string:
                    version_start = p4.sub(r'\g<version1>', version_string)
                    if version_start[-1] == 'x' or version_start[-1] == 'X':
                        version_start = version_start[0:-1] + '0'
    
                    version_end = p4.sub(r'\g<version2>', version_string)
                    if version_end[-1] == 'x' or version_end[-1] == 'X':
                        version_end = version_end[0:-1] + '9'
    
                    version = version_start + "--" + version_end
                    version_list.append(version)
                elif '和' in version_string:
                    version_1 = p5.sub(r'\g<version1>', version_string)
                    version_2 = p5.sub(r'\g<version2>', version_string)
                    for version in [version_1, version_2]:
                        if version[-1] == 'x' or version[-1] == 'X':
                            version = version[0:-1] + '0--' + version[0:-1] + '9'
                        version_list.append(version)
                else:
                    version = p2.sub(r'\g<version>', version_string)
                    if version[-1] == 'x' or version[-1] == 'X':
                        version = version[0:-1] + '0--' + version[0:-1] + '9'
                    version_list.append(version)
    
            version_result = ';'.join(version_list)
            return version_result
        else:
            return None

