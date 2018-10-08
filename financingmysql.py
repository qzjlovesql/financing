import time
from multiprocessing import Pool
import json
import requests
from urllib.parse import urlencode
import pymysql
from config import *

conn = pymysql.connect(
    host="localhost",
    port=3306,
    database="financing",
    user="root",
    password="123",
    charset="utf8",  # 不要加-
)
cursor = conn.cursor()


proxy_pool_url = 'http://127.0.0.1:5000/get'
headers = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.6756.400 QQBrowser/10.3.2473.400'

# 获取代理ip
def get_proxy():
    try:
        response = requests.get(proxy_pool_url)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None


def get_page(page):
    data = {
        'token': '70f12f2f4f091e459a279469fe49eca5',
        'st': 'tdate',
        'sr': -1,
        'p': page,
        'ps': 50,
        'js': 'var XhfdqNBv={pages:(tp),data: (x)}',
        'type': 'RZRQ_LSTOTAL_NJ',
        'mk_time': 1,
    }
    url = 'http://dcfm.eastmoney.com//EM_MutiSvcExpandInterface/api/js/get?' + urlencode(data)
    response = requests.get(url, headers)
    try:
        if response.status_code == 200:
            return response.text
        if response.status_code == 302:
            print('302')
            proxy = get_proxy()
            if proxy:
                print('Using Proxy', proxy)
                return get_page(page)
            else:
                print('Get Proxy Failed')
                return None
    except Exception:
        print("请求失败，未获取数据")

def parse_page(html):
    try:
        results = html.split('data: ')[1][:-1] #列表包字典
        results = json.loads(results)
        return results
    except Exception:
        print("未获取results")

def save_to_mongo(results, page):
    try:
        if results:
            for result in results:
                rzrqye = [result.get("tdate")[:10], round(result.get("rzrqye")/10**8, 2)]
                print(rzrqye)
                sql = "insert into ftb (tdate,rzrqye) values(%s,%s) "
                cursor.execute(sql, rzrqye)
                conn.commit()
            s = requests.session()
            s.keep_alive = False
            print('存储第{}页'.format(page))
            return True
        return False
    except Exception:
        print("存储失败")

def main(page):
    html = get_page(page)
    results = parse_page(html)
    save_to_mongo(results, page)

if __name__ == '__main__':
    try:
        pool = Pool()
        # 第一个参数是函数，第二个参数是一个迭代器，将迭代器中的数字作为参数依次传入函数中
        pool.map(main,[page for page in range(1, 43)])
    except requests.exceptions.ConnectionError:
        print("退出连接")
