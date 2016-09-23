# -*- coding: utf-8 -*-
"""
    ondemandkorea.com

    /includes/latest.php?cat=<name>
    /includes/episode_page.php?cat=<name>&id=<num>&page=<num>
"""
import urllib, urllib2
import re
import json
from bs4 import BeautifulSoup
import xml.etree.ElementTree as etree

root_url = "http://www.ondemandkorea.com"
img_base = "http://max.ondemandkorea.com/includes/timthumb.php?w=175&h=100&src="
default_UA = "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)"
tablet_UA = "Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Safari/535.19"

eplist_url = "/includes/episode_page.php?cat={program:s}&id={videoid:s}&page={page:d}"
genre_url = "http://www.ondemandkorea.com/includes/categories/"
forThumb = "http://lime2.ondemandkorea.com"

#웹사이트 데이터 불러오기
def getWebSite(action_url):
    req  = urllib2.Request(action_url)
    req.add_header('User-Agent', default_UA)
    req.add_header('Accept-Langauge', 'ko')
    req.add_header('Cookie', 'language=kr')
    html = urllib2.urlopen(req).read().decode("utf-8")
    return html


def parseGenrePage(genre):
    action_url = genre_url + genre + "_kr.json"
    htmlContent = getWebSite(action_url)
    jsonData = json.loads(htmlContent)    
    items = []
    for node in jsonData:
        items.append({'title':node['title'], 'url':node['post_name'], 'thumbnail':node['img']})
    return items



def parseEpisodePage(action_url, page=1):
    htmlContent = getWebSite(action_url)
    program = re.compile('"program" *: *"(.*?)"').search(htmlContent).group(1)
    videoid = re.compile('"videoid" *: *(\d+)').search(htmlContent).group(1)
    jsonData_url = root_url+eplist_url.format(program=program, videoid=videoid, page=page)
    #json data 위치를 찾아 데이터를 가지고 온다.
    htmlContent = getWebSite(jsonData_url)
    obj = json.loads(htmlContent)
    result = {'episode':[]}
    for item in obj['list']:
        if item["thumbnail"].split('/', 2 )[1] == "thumbnails":
            item["thumbnail"] = forThumb + item["thumbnail"]
        result['episode'].append({'title':item['title'], 'broad_date':item['on_air_date'], 'url':root_url+"/"+item['url'], 'thumbnail':img_base+item["thumbnail"]})
    if obj['cur_page'] > 1:
        result['prevpage'] = page-1
    if obj['cur_page'] < obj['num_pages']:
        result['nextpage'] = page+1
    return result


def extractVideoUrl(page_url, resolution):
    htmlContent = getWebSite(page_url)
    vid_title = re.compile('<div id="title">(.*?)</div>', re.S).search(htmlContent).group(1).strip()
    video_url = re.compile("""(http[^'"]*m3u8)""").search(htmlContent).group(1).strip()
    videoUrl_root  = video_url[0: video_url.rfind("/")]
    mainfestContent = getWebSite(video_url)
    match_url = re.compile("(.*m3u8)").findall(mainfestContent)
    
    comp = re.compile("RESOLUTION=(\\d{1,5}x\\d{1,5}).*\n(.*m3u8)",re.MULTILINE).findall(mainfestContent)
    video_url = None
    list = []
    for item in comp:
        list.append(item[1]) 
        if item[0] == "640x360":
            video_url = item[1]
            break
    
    if video_url == None:
        video_url = item[0]

    video_url = videoUrl_root + "/" + video_url
    return {'title':vid_title, 'video_url':video_url}


#일반 소스
def extractVideoUrl3(page_url):
    htmlContent = getWebSite(page_url)
    vid_title = re.compile('<div id="title">(.*?)</div>', re.S).search(htmlContent).group(1).strip()
    video_url = re.compile("""(http[^'"]*m3u8)""").search(htmlContent).group(1).strip()
    videoUrl_root  = video_url[0: video_url.rfind("/")]
    mainfestContent = getWebSite(video_url)
    match = re.compile("(.*m3u8)").findall(mainfestContent)
    video_url = videoUrl_root + "/" + match[len(match) -2]
    return {'title':vid_title, 'video_url':video_url}



if __name__ == "__main__":
    
    #print parseGenrePage("variety" )
    #print parseGenrePage2( root_url+"/variety" )
    #print parseEpisodePage( root_url+"/infinite-challenge-366.html" )
    #print parseEpisodePage( root_url+"/infinite-challenge-366.html", page=1 )
    #print extractStreamUrl( root_url+"/infinite-challenge-366.html" )
    print extractVideoUrl( root_url+"/monster-drama-e50.html" )

# vim:sw=4:sts=4:et
