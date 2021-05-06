'''' Scrape the Amazon.com using requests and Beautiful Soup. Increasing the speed
using the Threading/Processing/Pool in python'''

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from multiprocessing import Process, Queue, Pool, Manager
import threading
import sys
from itertools import cycle
import traceback
from lxml.html import fromstring
import random 
from collections import OrderedDict

headers_list = [
    # Firefox 77 Mac
     {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    },
    # Firefox 77 Windows
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.geeksforgeeks.org/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    },
    # Chrome 83 Mac
    {
        "Connection": "keep-alive",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://www.google.com/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
    },
    # Chrome 83 Windows 
    {
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://www.geeksforgeeks.org/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9"
    }
]

ordered_headers_list = []
for headers in headers_list:
    h = OrderedDict()
    for header,value in headers.items():
        h[header]=value
    ordered_headers_list.append(h)


def get_proxies():
    url = 'https://free-proxy-list.net/anonymous-proxy.html'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:80]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            #Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies


# use proxies in requests so as to proxy your request via a proxy server
# as some sites may block the IP if traffic generated by an IP is too high
proxies = get_proxies()

startTime = time.time()
qcount = 0
products=[] #List to store name of the product
images=[]
tags=[]
prices=[] #List to store price of the product
ratings=[] #List to store ratings of the product
no_pages = 20

def get_data(pageNo,q):
    proxy_pool = cycle(proxies)  
    headers = random.choice(headers_list)
    url  = 'https://www.amazon.in/s?i=stripbooks&rh=n%3A4149800031&fs=true&page='+ str(pageNo) +'&qid=1612945359&ref=sr_pg_2'
    print(url)
    proxyDict = {
        "http"  : next(proxy_pool),
        "https" : next(proxy_pool)
    }
    # print(url + '  ' + proxy + '   ' + headers)
    try:
        r = requests.get(url, proxies=proxyDict, headers=headers)
        content = r.content
        soup = BeautifulSoup(content, 'lxml')
        #print(soup.encode('utf-8')) # uncomment this in case there is some non UTF-8 character in the content and
                               # you get error
        for d in soup.findAll('div', attrs={'class':'s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col sg-col-12-of-16'}):
            image = d.find('img', attrs={'class':'s-image'})
            name = d.find('span', attrs={'class':'a-size-medium a-color-base a-text-normal'})
            price = d.find('span', attrs={'class':'a-price-whole'})
            rating = d.find('span', attrs={'class':'a-icon-alt'})
            tag = "buy " + name.text + " " +"buy " + name.text + " at cheap price " +"buy " + name.text + " online " +"buy " + name.text + " hardcover " +"buy " + name.text + " pdf " + ", buy exam books" + ", exam preparation books online" + ", ICWA exam books" + ", ICWA preparation exam books" + ", exam books" + ", ICWA exam" + "Finance exams"
            all=[]
        
            if name is not None:
                all.append(name.text)
                all.append(tag)
            else:   
                all.append("unknown-product")
                all.append("unknown-tag")
            if image is not None:
                all.append(image['src'])
            else:
                all.append("no-image")
            if price is not None:
                all.append(price.text)
            else:
                all.append('$0')
            if rating is not None:
                all.append(rating.text)
            else:
                all.append('-1')
            q.put(all)
        #print("---------------------------------------------------------------")
    except:
        print("skipping connection") 
results = []
if __name__ == "__main__":
    m = Manager()
    q = m.Queue() # use this manager Queue instead of multiprocessing Queue as that causes error
    p = {}
    if sys.argv[1] in ['t', 'p']: # user decides which method to invoke: thread, process or pool
        for i in range(1,no_pages):
            if sys.argv[1] in ['t']:
                print("starting thread: ",i)
                p[i] = threading.Thread(target=get_data, args=(i,q))
                p[i].start()
            elif sys.argv[1] in ['p']:
                print("starting process: ",i)
                p[i] = Process(target=get_data, args=(i,q))
                p[i].start()
        # join should be done in seperate for loop 
        # reason being that once we join within previous for loop, join for p1 will start working
        # and hence will not allow the code to run after one iteration till that join is complete, ie.
        # the thread which is started as p1 is completed, so it essentially becomes a serial work instead of 
        # parallel
        for i in range(1,no_pages):
            p[i].join()
    else:
        pool_tuple = [(x,q) for x in range(1,no_pages)]
        with Pool(processes=16) as pool:
            print("in pool")
            results = pool.starmap(get_data, pool_tuple)
    
    while q.empty() is not True:
        qcount = qcount+1
        queue_top = q.get()
        products.append(queue_top[0])
        tags.append(queue_top[1])
        images.append(queue_top[2])
        prices.append(queue_top[3])
        ratings.append(queue_top[4])
        
    print("total time taken: ", str(time.time()-startTime), " qcount: ", qcount)
    # print(q.get())
    df = pd.DataFrame({'Product Name':products, 'Price':prices, 'Ratings':ratings, "Image":images, "Tags":tags})
    print(df)
    df.to_csv('products-exam-fin-ICWA.csv', index=False, encoding='utf-8')

