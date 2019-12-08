# -*- coding: utf-8 -*-

from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import datetime as dt
import codecs

#トップページのURL
topPageUrl = "https://www.bloomberg.co.jp"

###引数で受け取ったURLのHTMLについてのBeautifulSoupオブジェクトを返す関数###
def getBsObj(url):
    html = urlopen(url)
    return BeautifulSoup(html, "html.parser")

def getPrintBody(bsObj):
    divs = bsObj.find("div", class_="article-body__content").find_all("p")

    #この記事が出力対象であるか｡
    toPrint = False

    #出力用の文字列を初期化する
    body = ""

    for d in divs:
        text = d.get_text()
        if target in text:
            toPrint = True

        body = body + "\n" + text

    if toPrint:
        return body
    else:
        print("This word is not included in this article:" + bsObj.find("title").get_text())
        return ""

def main():
    try:
        bsObjTop = getBsObj(topPageUrl)

        articleLinks = [] #個々のページのリンクを格納するためのリスト

        articleTags = bsObjTop.findAll("article")
        for t in articleTags:
            link = t.find("a").attrs["href"]
            articleLinks.append(link)

        #検索対象の文字列 TODO 検索対象の文字列は､外から与えたい
        target = "トランプ"

        file = codecs.open("C:\\Users\\ahiiro\\Desktop\\python_webscraping" + str(dt.date.today()) +".txt", "w", "utf-8")
        for link in articleLinks:
            targetUrl = topPageUrl + link
            bsObj = getBsObj(targetUrl)
            #出力する文字列を取得する
            printBody = getPrintBody(bsObj)
            #何も返ってこなければ､この記事は無視
            if len(printBody) != 0:
                file.write("Title:" + bsObj.find("title").get_text() + "\n")
                file.write("body:"+printBody+ "\n")
                file.write("---------------------------------------------------------------------------------\n")

        print("Done!!!")

    except requests.TimeoutError as err:
        print("Error happens:Timeout -> " + err.message)

    finally:
        file.close()

#main関数
if __name__ == '__main__':
    main()