import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from search_engines.multiple_search_engines import MultipleSearchEngines
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from apscheduler.schedulers.background import BackgroundScheduler
from elasticsearch import Elasticsearch
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from datetime import datetime
import base64
import tarfile
import io
import json
import uuid
from .models import SearchWriteSql,SearchWriteEs
from django.utils import timezone
from time import sleep

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0"
}

# 对requests.get()方法进行封装，设置超时时间、禁止重定向、禁用SSL证书验证
def get(url):
    try:
        requestsget = requests.get(url,timeout=10,allow_redirects=False,verify=False,headers=headers)
    except Exception as e:
        print(f"捕获到异常: {type(e).__name__}")
        print(f"异常信息: {e}")
        return None

    return requestsget

def download_file(url, target_directory):
    if url.startswith("data:image"):
        return 
    response = get(url)
    if response is None:
        return
    filename = os.path.basename(urlparse(url).path)
    if filename == "":
        filename_match = re.search(r'[^/\\&\?]+\.\w{3,4}(?=([\?&].*$|$))', url)
        if filename_match:
            filename = filename_match.group(0)
        else:
            filename = str(uuid.uuid4())
    filepath = os.path.join(target_directory, filename)
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
    print(filepath)
    with open(filepath, "wb") as file:
        file.write(response.content)

    return filepath

def BeautifulSoupHTML(html_content,url,target_directory):
    soup = BeautifulSoup(html_content, "html.parser")

    # 下载CSS文件
    for link in soup.find_all("link", rel="stylesheet"):
        css_url = urljoin(url, link["href"])
        css_filepath = download_file(css_url, target_directory)
        if css_filepath is None:
            continue
        link["href"] = os.path.relpath(css_filepath)

    # 下载JavaScript文件
    for script in soup.find_all("script", src=True):
        js_url = urljoin(url, script["src"])
        js_filepath = download_file(js_url, target_directory)
        if js_filepath is None:
            continue
        script["src"] = os.path.relpath(js_filepath)

    # 下载图片文件
    for img in soup.find_all("img", src=True):
        img_url = urljoin(url, img["src"])
        img_filepath = download_file(img_url, target_directory)
        if img_filepath is None:
            continue
        img["src"] = os.path.relpath(img_filepath)

    # 下载内联CSS中的背景图片
    for style_tag in soup.find_all("style"):
        css_content = style_tag.string
        bg_image_urls = re.findall(r'url\((.*?)\)', css_content)
        
        for bg_image_url in bg_image_urls:
            absolute_url = urljoin(url, bg_image_url)
            bg_image_filepath = download_file(absolute_url, target_directory)
            if bg_image_filepath is None:
                continue
            css_content = css_content.replace(bg_image_url, os.path.relpath(bg_image_filepath))

        style_tag.string = css_content

    # 保存修改后的HTML内容
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
    html_filepath = os.path.join(target_directory, "page_source.html")
    with open(html_filepath, "w", encoding="utf-8") as f:
        f.write(str(soup))
    f.close()
    if os.path.exists(html_filepath):
        tar_buffer = io.BytesIO()
        with tarfile.open(fileobj=tar_buffer, mode="w",encoding="UTF-8") as tar:
            # 遍历目录中的文件
            for root, _, files in os.walk(target_directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    # 将文件添加到tar压缩文件中
                    tar.add(file_path, arcname=os.path.relpath(file_path, target_directory))
        tar_buffer.seek(0)
        tar_base64 = base64.b64encode(tar_buffer.getvalue()).decode("utf-8")
        return tar_base64
    else:
        return None

def WriteEs(jsonout):
    esuuid = str(uuid.uuid4())
    current_date = datetime.now().strftime('%Y-%m-%d')
    index_name = f'webpage_{current_date}'
    jsonout["@uuid"] = esuuid
    try:
        response = es.index(index= index_name, body= jsonout)
        # 写入数据库
        new_entry = SearchWriteEs(esuuid=uuid, link=jsonout['result']['link'], host=jsonout['result']['host'])
        new_entry.save()
        print(response)
    except Exception as e:
        print("写入ES失败")
        print(e)
        # 再次尝试写入
        try:
            response = es.index(index= index_name, body= jsonout)
            # 写入数据库
            new_entry = SearchWriteEs(esuuid=uuid, link=jsonout['result']['link'], host=jsonout['result']['host'])
            new_entry.save()
            print(response)
        except Exception as e:
            print("再次写入ES失败,放弃写入")
            print(e)

def requests_save(url, host, target_directory,jsonout,driver,query,enginesearch):
    # 创建目标目录，如果不存在
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    # 访问网站
    print("访问￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥￥",url)
    response = get(url)
    if response is None:
        jsonout['status'] = 'error'
        strjsonout = dicttojson(jsonout)
        with open("output.json","a+",encoding="UTF-8") as file:
            file.write(strjsonout)
        # WriteEs(jsonout)
        print(url,"这个请求无法访问")
        return
    if response.status_code == 302:
        # 捕获重定向的URL
        redirect_url = response.headers.get("Location")
        jsonout['status'] = 'redirect'
        jsonout['redirect_url'] = redirect_url
        # print(f"Redirect URL: {redirect_url}")
        print(url,"这个请求重定向了")
    else:
        # 截图保存html
        try:
            driver.get(url)
            pngout_base64 = driver.get_screenshot_as_base64()
            html_source = driver.page_source
            html_source_base64 = base64.b64encode(html_source.encode("utf-8")).decode("utf-8")
            if pngout_base64 is not None:
                jsonout['status'] = 'success'
                jsonout['screenshotbase64'] = pngout_base64
                # jsonout['htmlbase64'] = html_source_base64
            else:
                jsonout['status'] = 'error'
        except Exception as e:
            print(f"捕获到异常: {type(e).__name__}")
            print(f"异常信息: {e}")
        html_content = response.text
        tar_base64 = BeautifulSoupHTML(html_content,url,target_directory+host+'/raw/')
        # if tar_base64 is not None:
            # jsonout['status'] = 'success'
            # jsonout['tarbase64'] = tar_base64
    strjsonout = dicttojson(jsonout)
    with open("output.json","a+",encoding="UTF-8") as file:
        file.write(strjsonout)
    # 叫机器人通知
    NotifyRobot("搜索语法："+query+"\n"+"搜索引擎"+str(enginesearch)+"\n"+"url:"+url)
    # NotifyRobot("url:"+url)
    with open("downloads/search_result.txt","a+",encoding="UTF-8") as file:
        file.write(url)
        file.write("\n")
    # WriteEs(jsonout)

def dicttojson(jsonout):
    jsonout = json.dumps(jsonout, ensure_ascii=False)
    return jsonout


# 查寻当前link是否已经存在
def checklink(link):
    entries_by_link = SearchWriteSql.objects.filter(link=link)
    if entries_by_link:
        return True
    return False

def checkIs_Is_valid(link):
    return True
    entry_to_modify = SearchWriteSql.objects.filter(link=link).first()
    if entry_to_modify.is_valid:
        return True
    return False
    

def my_function(query,enginesearch,pages,parent_directory,driver):
    global stop_tasks
    stop_tasks = False
    if len(enginesearch) != 0:
        print("使用多引擎搜索",str(enginesearch))
        engine = MultipleSearchEngines(engines=enginesearch)
    else:
        print("输入引擎有误")
        return
    results = engine.search(query,pages=pages)
    # 为每次搜索创建一个文件夹
    now = datetime.now()
    folder_name = now.strftime("%Y-%m-%d-%H-%M-%S")
    folder_path = os.path.join(parent_directory, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    print("搜索到结果数为：@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",len(results))
    t = 1
    for result in results:
        print("开始域名第个域名",t,"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",result['link'])
        t=t+1
        if stop_tasks:
            print("停止任务")
            return
        link = result['link']
        host = result['host']            
        jsonout = {}
        jsonout['query'] = query
        jsonout['result'] = {}
        jsonout['result']['link'] = link
        jsonout['result']['host'] = host
        jsonout['result']['title'] = result['title']
        jsonout['result']['text'] = result['text']
        jsonout['@timestamp'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        # print(jsonout)
        # # 创建一个json保存搜索结果和爬取结果
        # if checklink(link) == False:
        #     # 保存到数据库
        #     new_entry = SearchWriteSql(host=host, link=link,is_valid=True ,pub_date=timezone.now())
        #     new_entry.save()
        # 读取数据,当is_valid为trues是，进入requests_save
        if checkIs_Is_valid(link) == True:
            print("开始爬取")
            requests_save(link,host,os.path.join(folder_path, host),jsonout,driver,query,enginesearch)
    print("处理完成")
    sleep(2)


scheduler = BackgroundScheduler()
es = Elasticsearch(
    [{'host': '10.67.29.200', 'port': 9200,'scheme':'https'}],
    http_auth=('elastic', 'ueKnH7rW+IFOa*li6j6L'),
    verify_certs=False
)
def SearchEsdata(uuid):
    index = f"webpage_*"
    query_body = {
        "query": {
            "match": {
                "@uuid": uuid
            }
        }
    }
    res = es.search(index=index, body=query_body)
    print(res)

def TimingSearch(params):
    global global_pages
    random_uuid = str(uuid.uuid4())
    target_url = params['target_url']
    keyword = params['keyword']
    after = params['after']
    before = params['before']
    query = dealInput(target_url,keyword=keyword,before=before,after=after)
    print("搜索语法为^^^^^^^^^^^^^^^^^^^^^"+query)
    enginesearch = params['enginesearch']
    pages = params['pages']
    minutes = params['minutes']
    parent_directory = params['parent_directory']
    print("random_uuid",random_uuid,"\t","enginesearch",enginesearch,"\t","pages",pages,"\t","minutes",minutes)
    # 初始化浏览器
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')
    options.add_argument('--lang=zh-CN')
    options.add_argument('--disable-gpu')
    download_directory = os.path.join(parent_directory, "downloads")
    if not os.path.exists(download_directory):
        os.makedirs(download_directory)
    prefs = {
        "download.default_directory": download_directory,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True  # 用于自动下载PDF文件
    }
    options.add_experimental_option("prefs", prefs)
    service = Service(executable_path='./tools/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1920, 1080)
    # 创建一个调度器
    print("调度器启动")
    if not scheduler.running:
        scheduler.start()
    # 添加调度任务
    scheduler.add_job(my_function, 'interval', minutes=minutes ,next_run_time=datetime.now(),kwargs={'query': query,'enginesearch':enginesearch, 'pages': pages,'parent_directory': parent_directory, 'driver': driver},id = random_uuid)
    # 启动调度器
    # scheduler.start()
    print("调度器创建结束")
    return random_uuid

def TimingSearchStop(random_uuid):
    print("调度器停止")
    global stop_tasks
    stop_tasks = True
    scheduler.remove_job(random_uuid)
    print("调度器停止结束")
    return True

def NotifyRobot(mes):
    # URL = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=160505dc-156e-4d81-ad5e-273041ad31f8' #正式

    URL = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=8675749b-4d33-492e-992a-330f2b318775' #测试

    mHeader = {'Content-Type': 'application/json; charset=UTF-8'}
    mBody = {
    "msgtype": "text",
    "text": {
        "content": mes,
        "mentioned_list":["shenyuguo"],
        }
    }
    requests.post(url=URL, json=mBody, headers=mHeader)

def dealInput(target_url,keyword,before,after):
    query = "site:"+target_url
    if keyword != "":
        query = query +" "+"\""+keyword+"\""
    if before != "":
        query = query +" "+"before:"+before
    if after != "":
        query = query +" "+"after:"+after
    return query