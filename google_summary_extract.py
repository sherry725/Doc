import time
import pandas as pd
from selenium import webdriver

links = pd.read_excel("google_search_url.xlsx")
webs = links['URL']

chrome_path = 'chromedriver'
option = webdriver.ChromeOptions()
option.add_argument('--headless')

title_result = []
description_result = []
keyword_result = []

#webs = ['https://www.healthline.com/health/healthy-sleep/natural-sleep-aids']
for web in webs:
    browser = webdriver.Chrome(options=option, executable_path=chrome_path)
    # cdp - chrome developer protocol
    browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator,"webdriver",{get:() => undefined})'
    })
    print(web)
    try:
        browser.get(web)
    except:
        print("Web not found")

    time.sleep(5)
    try:
        ttl = browser.find_element_by_tag_name('title')
    except:
        print("title not found")
        title_result.append(" ")
    else:
        print(ttl.get_attribute('innerText'))
        title_result.append(ttl.get_attribute('innerText').strip())

    try:
        dcrip = browser.find_element_by_css_selector('meta[name="description"]')
    except:
        print("description not found")
        description_result.append(" ")
    else:
        print(dcrip.get_attribute("content"))
        description_result.append(dcrip.get_attribute("content").strip())

    try:
        kw = browser.find_element_by_css_selector('meta[name="keywords"]')
    except:
        print("keyword not found")
        keyword_result.append(" ")
    else:
        print(kw.get_attribute("content"))
        keyword_result.append(kw.get_attribute("content").strip())

    browser.close()

links['Title'] = title_result
links['Description'] = description_result
links['Keyword'] = keyword_result
links.to_excel("google_search_summary.xlsx", index=False)