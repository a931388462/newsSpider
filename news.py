#用作定义新闻
class News(object):
    # 初始化中给对象属性赋值
    def __init__(self,date,url,title, summary, text):
        # 日期
        self.date = date
        #网站
        self.url = url
        # 标题
        self.title = title
        # 摘要
        self.summary = summary
        # 正文
        self.text = text
