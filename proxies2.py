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
        "Referer": "https://www.google.com/",
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
        "Referer": "https://www.google.com/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9"
    }
]
ordered_headers_list = []
for headers in headers_list:
    h = OrderedDict()
    for header, value in headers.items():
        h[header] = value
    ordered_headers_list.append(h)


def get_proxies():
    url = 'https://free-proxy-list.net/anonymous-proxy.html'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:80]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            # Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0],
                              i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies


proxies = get_proxies()
print(proxies)

proxy_pool = cycle(proxies)
proxyLength = len(proxies)


url = 'https://www.amazon.in/s?i=stripbooks&rh=n%3A1318157031&fs=true&page=2&qid=1612295000&ref=sr_pg_2'
for i in range(1, 20):
    # Get a proxy from the pool
    proxy = next(proxy_pool)
    headers = random.choice(headers_list)
    requests.headers = headers
    print("Request #%d" % i)
    try:
        response = requests.get(url, proxies={"http": proxy, "https": proxy})
        content = response.content
        soup = BeautifulSoup(content, 'lxml')
        for d in soup.findAll('div', attrs={'class': 's-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col sg-col-12-of-16'}):
            image = d.find('img', attrs={'class': 's-image'})
            name = d.find(
                'span', attrs={'class': 'a-size-medium a-color-base a-text-normal'})
            price = d.find('span', attrs={'class': 'a-price-whole'})
            rating = d.find('span', attrs={'class': 'a-size-base'})
            all = []
            if name is not None:
                all.append(name.text)
            else:
                all.append("unknown-product")
            if image is not None:
                all.append(image.text)
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
    except:
        # Most free proxies will often get connection errors. You will have retry the entire request using another proxy to work.
        # We will just skip retries as its beyond the scope of this tutorial and we are only downloading a single url
        print("Skipping. Connnection error")
print(all)
