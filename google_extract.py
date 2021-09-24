import time
import pandas as pd
from selenium import webdriver
#from selenium.webdriver.common.keys import Keys

chrome_path='chromedriver'
option = webdriver.ChromeOptions()
option.add_argument('--headless')
browser = webdriver.Chrome(options = option, executable_path=chrome_path)
#cdp - chrome developer protocol
browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
    'source':'Object.defineProperty(navigator,"webdriver",{get:() => undefined})'
})
query_text ='+'.join('ingredient for sleep'.split())
market = 'US'
query_url = 'https://www.google.com/search?q='+query_text+'&cr=country'+market

browser.get(query_url)
#kw_input = browser.find_element_by_name('q')
#kw_input.send_keys(query_text)
#kw_input.send_keys(Keys.RETURN)
time.sleep(2)

def get_url():
    links = browser.find_elements_by_css_selector('div > div > div > div.yuRUbf > a')
    url_list = []
    for link in links:
        url_list.append(link.get_attribute("href"))
    return url_list

url = get_url()

pages = browser.find_elements_by_xpath('//*[@id="xjs"]/table/tbody/tr/td/a')
page_lst = []
for page in pages:
    page_lst.append(page.get_attribute("href"))

for link in page_lst[:4]:
    print(f"we are going to {link}")
    browser.get(link)
    time.sleep(2)
    new_url = get_url()
    url.extend(new_url)
    print(f"get {len(url)} links")

browser.close()
"""
text_result = []
for web in url:
    text = []
    browser.get(web)
    time.sleep(1)
    t = browser.find_elements_by_tag_name('p')
    for w in t:
        text.append(w.text)
    text_result.append(' '.join(text))
    
def get_summary():
    summaries = browser.find_elements_by_css_selector('#rso > div')
    for summary in summaries:
        print(summary.text)
"""

result = pd.DataFrame({
    "URL": url
    #"text": text_result
})
result['Query'] = query_text
result['Market'] = market

result.to_excel("google_search_url.xlsx", index=False)



