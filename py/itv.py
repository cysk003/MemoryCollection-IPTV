import time
import os
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import re

# 将URL和文件名提取为变量，以便于管理和修改
URLS_FILE = "py/urls.txt"
RESULTS_FILE = "py/results.txt"

def get_urls_from_file(file):
    with open(file, 'r') as f:
        return [line.strip() for line in f]

def write_results_to_file(file, results):
    with open(file, 'w') as f:
        for result in results:
            f.write(result + "\n")

def get_page_content(url):
    # 创建一个Chrome WebDriver实例
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    with webdriver.Chrome(options=chrome_options) as driver:
        # 使用WebDriver访问网页
        driver.get(url)
        time.sleep(10)
        # 获取网页内容
        return driver.page_source

def get_urls_from_content(content):
    # 查找所有符合指定格式的网址
    pattern = r"http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"
    return set(re.findall(pattern, content))

def is_url_accessible(url):
    try:
        response = requests.get(url, timeout=0.5)
        if response.status_code == 200:
            return url
    except requests.exceptions.RequestException:
        pass
    return None

def get_valid_urls(urls):
    valid_urls = []
    # 使用并发处理来提高效率
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(is_url_accessible, url) for url in urls]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                valid_urls.append(result)
    return valid_urls

def main():
    urls = get_urls_from_file(URLS_FILE)
    results = []
    for url in urls:
        try:
            content = get_page_content(url)
            urls_from_content = get_urls_from_content(content)
            valid_urls = get_valid_urls(urls_from_content)
            results.extend(valid_urls)
        except Exception as e:
            print(f"Error processing url {url}: {e}")
    write_results_to_file(RESULTS_FILE, results)

if __name__ == "__main__":
    main()