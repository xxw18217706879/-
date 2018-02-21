import requests
import time
import pymongo
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from config import *

client=pymongo.MongoClient(MONGO_URL)
db=client[MONGO_DB]
table=db[MONGO_TABLE]

page=0

headers={
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
}

def page_index(url,pagenow):
    data={
        'poiID':13412802,
        'districtId':571,
        'districtEName':'Chongming',
        'pagenow':pagenow,
        'order':3.0,
        'star':0.0,
        'tourist':0.0,
        'resourceId':107380,
        'resourcetype':2
    }
    try:
        response=requests.post(url,data=data,headers=headers)
        if response .status_code ==200:
            return response.text
        return None
    except RequestException :
        print("请求网页失败")
        return None

def parse_page_detail(html,pagenow):
    global page
    page+=1
    index=0
    soup=BeautifulSoup(html,'lxml')
    results=soup.find_all("div",itemtype="http://schema.org/Review")
    print("crawing page{}".format(str(pagenow)))
    result_list=[]
    for result in results:
        srcs=result.find("img",height="60")
        nicknames=result.find("span",class_="ellipsis")
        scores=result.find("span", class_="sblockline")
        dates=result.find("em", itemprop="datePublished")
        uses=result.find("span", class_="useful")
        texts=result.find("span",class_="heightbox")
        images=result.find("li", class_="comment_piclist cf")


        #找出没有评论中不含图片的，用None代替
        if images!=None:
            total_image=[]
            image_list=images.find_all("a")
            comment_pics=[]
            for item in image_list:
                comment_pics.append((item['data-commentimg']))
            total_image.append(comment_pics)
        else:
            total_image=[]
            total_image.append("None")
        for image in total_image:
            #找出不含score的内容，用None代替
            if scores!=None:
                scores=scores.get_text().replace("\u2003\n",'').replace(" ",'').strip()
            else:
                scores=str(scores)
            index+=1
            dic={}
            dic['index']='{}({})'.format(str(page),str(index))
            dic["src"]=srcs["src"]
            dic['nickname']=nicknames.get_text()
            dic['date']=dates.get_text().strip()
            dic['use']=uses.get_text().strip()
            dic['score']=scores
            dic['text']=texts.get_text().strip()
            dic['image']=image
            result_list.append(dic)
    return result_list


def save_to_mongo(result):
    try:
        if table.insert(result):
            print("save to mongo successfully",result)
    except Exception as e:
        print(e.args)



def main(pagenow):
    url='http://you.ctrip.com/destinationsite/TTDSecond/SharedView/AsynCommentView'
    html=page_index(url,pagenow)
    for item in (parse_page_detail(html,pagenow)):
        save_to_mongo(item)
    time.sleep(1)


if __name__=='__main__':
    if table:#若表存在则删除
        table.drop()
    for pagenow in range(1,68):
        main(pagenow)
