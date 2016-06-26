'''
Created on 2016年6月26日
@author: zhangxun
'''

from html.parser import HTMLParser
class MyHtmlParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        return None
    def handle_starttag(self, tag, attrs):
        for someTuple in attrs:
            if "tableData_1243" in someTuple:
                xxx=0
                xxx+=1
        return None
    def handle_startendtag(self, tag, attrs):
        return None
    def handle_endtag(self, tag):
        if tag=="div":
            xxx=0
            xxx+=1
        return None
    
if __name__ == "__main__":
    ff = open("D:/list.txt", "rb")
    htmlCode = ff.read()
    ff.close()
    htmlCode = htmlCode.decode("utf8")
    xx = MyHtmlParser()
    xx.feed(htmlCode)
    xx.close()
    exit(0)
