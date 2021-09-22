import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

chrome_path='chromedriver'
option = webdriver.ChromeOptions()
option.add_argument('--headless')
browser = webdriver.Chrome(options = option, executable_path=chrome_path)
#cdp - chrome developer protocol
browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
    'source':'Object.defineProperty(navigator,"webdriver",{get:() => undefined})'
})
query_text = 'ingredient for sleep'
browser.get('https://www.google.com.sg/')
kw_input = browser.find_element_by_name('q')
kw_input.send_keys(query_text)
kw_input.send_keys(Keys.RETURN)
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


result = pd.DataFrame({
    "URL": url
})

result['Keyword']= query_text
result.to_excel("google_search_article.xlsx", index=False)




