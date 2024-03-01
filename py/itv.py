import time

import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import re



urls = [
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iSGViZWki",  # Hebei (河北)
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iYmVpamluZyI%3D",  # Beijing (北京)
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0iZ3Vhbmdkb25nIg%3D%3D",  # Guangdong (广东)

    ]


def modify_urls(url):
    """修改URL中的IP地址，生成新的URL列表"""
    modified_urls = []
    ip_start_index = url.find("//") + 2
    ip_end_index = url.find(":", ip_start_index)
    base_url = url[:ip_start_index]  # http:// or https://
    ip_address = url[ip_start_index:ip_end_index]
    port = url[ip_end_index:]
    ip_end = "/iptv/live/1000.json?key=txiptv"
    for i in range(1, 256):
        modified_ip = f"{ip_address[:-1]}{i}"
        modified_url = f"{base_url}{modified_ip}{port}{ip_end}"
        modified_urls.append(modified_url)
    return modified_urls

def is_url_accessible(url):
    """检查URL是否可访问"""
    try:
        response = requests.get(url, timeout=0.5)
        if response.status_code == 200:
            return url
    except requests.exceptions.RequestException:
        pass
    return None

def process_url(url):
    """处理单个URL"""
    try:
        print(f"Processing URL: {url}")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(10)
        page_content = driver.page_source  # 修正此处
        driver.quit()  # 记得关闭 WebDriver
        
        pattern = re.compile(r"http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+")
        urls_all = pattern.findall(page_content)
        urls = set(urls_all)
        
        x_urls = [f"{url[:url.find(':', url.find('//') + 2)]}1" for url in urls]
        valid_urls = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(is_url_accessible, modified_url) for url in x_urls for modified_url in modify_urls(url)]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    valid_urls.append(result)
                    
        for url in valid_urls:
            ip_start_index = url.find("//") + 2
            ip_dot_start = url.find(".") + 1
            ip_index_second = url.find("/", ip_dot_start)
            base_url = url[:ip_start_index]  # http:// or https://
            ip_address = url[ip_start_index:ip_index_second]
            url_x = f"{base_url}{ip_address}"
            
            json_url = f"{url}"
            response = requests.get(json_url, timeout=0.5)
            json_data = response.json()
            
            for item in json_data.get('data', []):
                name = item.get('name')
                urlx = item.get('url')
                if ',' in urlx:
                    urlx = "aaaaaaaa"
                if 'http' in urlx:
                    urld = f"{urlx}"
                else:
                    urld = f"{url_x}{urlx}"
                    replacements = {
                        "cctv": "CCTV",
                        "中央": "CCTV",
                        "央视": "CCTV",
                        "高清": "",
                        "超高": "",
                        "HD": "",
                        "标清": "",
                        "频道": "",
                        "纪录": "",
                        "-": "",
                        " ": "",
                        "PLUS": "+",
                        "＋": "+",
                        "(": "",
                        ")": "",
                        "CCTV1综合": "CCTV1",
                        "CCTV2财经": "CCTV2",
                        "CCTV17农业": "CCTV17",
                        "CCTV5+体育赛视": "CCTV5+",
                        "CCTV5+体育赛事": "CCTV5+",
                        "CCTV5+体育": "CCTV5+",
                        "上海卫视": "东方卫视",
                        "内蒙古": "内蒙",
                        "CMIPTV": "",
                        "山东教育卫视": "山东教育",
                        "吉林怀视": "吉林卫视",
                        "CHC": ""
                    }

                    if name and urld:
                        for old, new in replacements.items():
                            name = name.replace(old, new)
                        name = re.sub(r"CCTV(\d+)台", r"CCTV\1", name)
                        if 'udp' not in urld or 'rtp' not in urld:
                            results.append(f"{name},{urld}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    """主函数"""
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_url, url) for url in urls]
        for future in concurrent.futures.as_completed(futures):
            results.extend(future.result())
                    
    results = set(results)
    results = sorted(results)

    with open("tv/itv.txt", 'w', encoding='utf-8') as file:
        for result in results:
            file.write(result + "\n")
            print(result)

if __name__ == "__main__":
    main()
