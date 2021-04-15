import time

import requests
from lxml import etree
from selenium.webdriver import Chrome, ActionChains
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.select import Select

from dateUtils import dateConver, checkDateRange, dateConver2
from news import News

chrome_options = ChromeOptions()
# 修改windows.navigator.webdriver，防机器人识别机制，selenium自动登陆判别机制
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
# 隐藏"Chrome正在受到自动软件的控制"
chrome_options.add_argument('disable-infobars')

driver = Chrome(chrome_options=chrome_options)
#窗口最大化
driver.maximize_window()
#隐式等待
#driver.set_page_load_timeout (15)

# CDP执行JavaScript 代码  重定义windows.navigator.webdriver的值
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
        Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined
        })
      """
})

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"}

#爬虫1
def spider1(startDate,endDate):
    # 起始页面
    start_url = """https://www.adb.org/search?page=1&facet_query=ola_collection_name%3Anews%7CNews%20Release%2Bphoto_essay%7CPhoto%20Essay%2Bfeature%7CMultimedia&facet_query=ds_field_date_content%3A{}T00%3A00%3A00.000Z%2B{}T16%3A00%3A00.000Z
    """.format(startDate, endDate)
    # 结果
    results = []
    driver.get(start_url)
    time.sleep(0.5)

    while True:
        html = etree.HTML(driver.page_source)
        dates = dateConver(html.xpath("//span[@class='ola-flex-content']/text()"))
        links = html.xpath("//div[@class='jsx-2785347796 ola-results']//div[@class='ola-field ola-field-button']/a/@href")
        titles = html.xpath("//div[@class='jsx-2785347796 ola-results']//div[@class='ola-field ola-field-button']/a/span/text()")
        summarys = html.xpath("//div[@class='ola-field-value']/p/text()")

        for i in range(len(titles)) :
            news = News(dates[i],links[i], titles[i], summarys[i], "")
            results.append(news)
        # 下一页DOM
        try:
            next_page_btn = driver.find_element_by_xpath("//nav[@class='ola-pagination']/button[last()]")
        except:
            if len(results)==0 :
                results.append(News("没有找到新闻","", "", "", ""))
            return results
            # 是否是最后一页
        if "ola-page-disabled" in next_page_btn.get_attribute("class"):
            break
        next_page_btn.click()
        time.sleep(5)

    return results


#爬虫2
def spider2(startDate,endDate):
    startDateArray = startDate.split("-")
    endDateArray = endDate.split("-")
    #要查询的年份
    years = list(set((startDateArray[0],endDateArray[0])))
    # 起始页面
    start_urls = ["https://www.ids.ac.uk/news-and-opinion/news/?select-year%5B0%5D={}&hidden-current-page=1&hidden-sort-by=ndate&current-page=1#listing".format(years[0])]
    if len(years)>1:
        start_urls.append("https://www.ids.ac.uk/news-and-opinion/news/?select-year%5B0%5D={}&hidden-current-page=1&hidden-sort-by=ndate&current-page=1#listing".format(years[1]))
    # 结果
    results = []
    for start_url in start_urls:
        driver.get(start_url)
        time.sleep(0.5)
        #日期不满足要求
        dateFlag = False
        while True:
            html = etree.HTML(driver.page_source)
            dates = dateConver(html.xpath("//article[@class='c-content-item c-content-item--news c-listing__item']//p[@class='c-content-item__date ts-caption']/text()"))
            links = html.xpath("//article[@class='c-content-item c-content-item--news c-listing__item']//a/@href")
            titles = html.xpath("//article[@class='c-content-item c-content-item--news c-listing__item']//a/text()")
            summarys = html.xpath("//article[@class='c-content-item c-content-item--news c-listing__item']//p[@class='c-content-item__description ts-body ts-body--small']/text()")
            for i in range(len(links)) :
                #日期在范围内
                if checkDateRange(startDate,endDate,dates[i]):
                    news = News(dates[i],links[i], titles[i].strip(), summarys[i].strip(), "")
                    print(news.date)
                    results.append(news)
                elif dates[i]<startDate:
                    dateFlag = True
                    break;
            #日期不满足要求
            if dateFlag:
                break
            # 下一页DOM
            try:
                next_page_btn = driver.find_element_by_xpath("//a[@title='Next page']")
            except:
                #最后一页
                break
            driver.execute_script("arguments[0].click();", next_page_btn)
            time.sleep(5)
    return results

#爬虫3
def spider3(startDate,endDate):
    startDateArray = startDate.split("-")
    endDateArray = endDate.split("-")
    #要查询的年份
    years = list(set((startDateArray[0],endDateArray[0])))
    # 起始页面
    start_urls = "https://www.sipri.org/news/past?page="
    # 结果
    results = []
    page = 0;
    # 日期不满足要求
    dateFlag = False
    while True:
        print(start_urls+str(page))
        response = requests.get(start_urls+str(page), headers=headers)
        html = etree.HTML(response.text)
        dates = dateConver(html.xpath("//div[@class='field-content']/time/text()"))
        links = html.xpath("//div[@class='field-content']/h3/a/@href")
        titles = html.xpath("//div[@class='field-content']/h3/a/text()")
        summarys = html.xpath("//div[@class='field-content']/p/text()|//div[@class='field-content']/p//span/text()")
        for i in range(len(links)):
            # 日期在范围内
            if checkDateRange(startDate, endDate, dates[i]):
                news = News(dates[i], "https://www.sipri.org/"+links[i], titles[i].strip(), summarys[i].strip(), "")
                results.append(news)
            elif dates[i] < startDate:
                dateFlag = True
                break;
        # 日期不满足要求
        if dateFlag:
            break
        page+=1
    return results

#爬虫4
def spider4(startDate,endDate):
    startDateArray = startDate.split("-")
    endDateArray = endDate.split("-")
    #要查询的年份
    years = list(set((startDateArray[0],endDateArray[0])))
    # 起始页面
    start_url = "https://rusi.org/publication/rusi-journal"
    driver.get(start_url)
    for nian in years:
        time.sleep(1)
        opt = driver.find_element_by_xpath("//select[@class='date-year form-select']")
        time.sleep(1)
        Select(opt).select_by_value(nian)
        time.sleep(1)
        search_btn = driver.find_element_by_xpath("//input[@id='edit-submit-related-content']")
        driver.execute_script("arguments[0].click();", search_btn)
        time.sleep(1)
        # 结果
        results = []
        # 日期不满足要求
        dateFlag = False
        while True:
            html = etree.HTML(driver.page_source)
            dates = dateConver(html.xpath("//div[@class='tab-internal']//span[@class='date-display-single']/text()"))
            links = html.xpath("//div[@class='tab-internal']/h3/a/@href")
            titles = html.xpath("//div[@class='tab-internal']/h3/a/text()")
            summarys = html.xpath("//div[@class='tab-internal']//p/text()")
            for i in range(len(links)):
                # 日期在范围内
                if checkDateRange(startDate, endDate, dates[i]):
                    news = News(dates[i], 'https://rusi.org/'+links[i], titles[i].strip(), summarys[i].strip(), "")
                    print(news.date)
                    results.append(news)
            # 下一页DOM
            try:
                next_page_btn = driver.find_element_by_xpath("//a[@title='Go to next page']")
            except:
                # 最后一页
                break
            driver.execute_script("arguments[0].click();", next_page_btn)
            time.sleep(5)
    return results

#爬虫5
def spider5(startDate,endDate):
    startDateArray = startDate.split("-")
    endDateArray = endDate.split("-")
    #要查询的年份
    years = list(set((startDateArray[0],endDateArray[0])))
    # 起始页面
    start_urls = []
    for year in years:
        start_urls.append("https://www.ifri.org/en/publications?"
                          "title=&field_contenugen_fc_auteur_int_target_id=All&field_themes_associes_tid=All&field_date_de_publication_value%5Bvalue%5D%5Byear%5D={}&term_node_tid_depth_1=All&sort_by=field_date_de_publication_value&sort_order=DESC".format(year))
        # 结果
    results = []
    for start_url in start_urls:
        driver.get(start_url)
        time.sleep(0.5)
        # 日期不满足要求
        dateFlag = False
        while True:
            html = etree.HTML(driver.page_source)
            dates = dateConver2(html.xpath("//div[@class='date-vignette']/span/text()"))
            links = html.xpath("//div[@class='title-vignette-search']/a/@href")
            titles = html.xpath("//div[@class='title-vignette-search']/a/@title")
            summarys = html.xpath("//div[@class='content-vignette']//p/text()")
            for i in range(len(links)):
                # 日期在范围内
                if checkDateRange(startDate, endDate, dates[i]):
                    news = News(dates[i], 'https://www.ifri.org'+links[i], titles[i].strip(), summarys[i].strip(), "")
                    print(news.date)
                    results.append(news)
                elif dates[i] < startDate:
                    dateFlag = True
                    break;
            # 日期不满足要求
            if dateFlag:
                break
            # 下一页DOM
            try:
                next_page_btn = driver.find_element_by_xpath("//ul[@class='pagination']/li[@class='next last']/a")
            except:
                # 最后一页
                break
            driver.execute_script("arguments[0].click();", next_page_btn)
            time.sleep(5)
    return results


#取得正文内容
def getNewstext1(url):
    # 伪装成浏览器发起请求
    try:
        response = requests.get(url, headers=headers)
        html = etree.HTML(response.text)
        s_text = ''
        texts = html.xpath("//main[@class='adb-main column ']/article/p/text()")
        for text in texts: s_text += text
    except:
        s_text = '正文取得失败'
    return s_text.strip()

#取得正文内容
def getNewstext2(url):
    # 伪装成浏览器发起请求
    try:
        response = requests.get(url, headers=headers)
        html = etree.HTML(response.text)
        s_text = ''
        texts = html.xpath("//div[@class='o-content-from-editor']//text()")
        for text in texts: s_text += text
    except:
        s_text = '正文取得失败'
    return s_text

#取得正文内容
def getNewstext3(url):
    # 伪装成浏览器发起请求
    try:
        response = requests.get(url, headers=headers)
        html = etree.HTML(response.text)
        s_text = ''
        texts = html.xpath("//div[@class='content']//div[@class='field-item']//p//text()")
        for text in texts: s_text += text
        print(s_text)
    except:
        s_text = '正文取得失败'
    return s_text

#取得正文内容
def getNewstext4(url):
    # 伪装成浏览器发起请求
    try:
        response = requests.get(url, headers=headers)
        html = etree.HTML(response.text)
        s_text = ''
        texts = html.xpath("//div[@class='inside']//div[@class='field__items']//span/text()|//div[@class='inside']//div[@class='field__items']//p/text()|//div[@class='inside']//div[@class='field__items']/div[@class='field__item even']/text()")
        for text in texts: s_text += text
        print(s_text)
    except:
        s_text = '正文取得失败'
    return s_text

#取得正文内容
def getNewstext5(url):
    # 伪装成浏览器发起请求
    try:
        response = requests.get(url, headers=headers)
        html = etree.HTML(response.text)
        s_text = ''
        texts = html.xpath("//div[@class='chapo']//p/text()|//div[@class='main-content']//div[@class='row']//div[@class='field-item even']/p/text()")
        for text in texts: s_text += text
        print(s_text)
    except:
        s_text = '正文取得失败'
    return s_text

#spider5('2019-12-01','2020-07-26')
#spider2('2020-06-01','2020-07-26')
#spider1('2020-06-24','2020-06-26')

