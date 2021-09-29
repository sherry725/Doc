import time
import pandas as pd
from selenium import webdriver
#from selenium.webdriver.common.keys import Keys

def extract_restUrl(browser):
    try:
        list_div = browser.find_elements_by_xpath('//div[@data-test-target="restaurants-list"]/div[contains(@data-test,"list_item") and @data-test != "SL_list_item"]')
    except:
        print("cannot find root")
        return None
    name = []
    url = []
    for item in list_div:
        try:
            restant_name = item.find_element_by_css_selector('span > div > div > div > div > span > a').text
        except:
            print("cannot find restaurant name")
            name.append(" ")
        else:
            #print(restant_name)
            name.append(restant_name)

        try:
            restant_url = item.find_element_by_css_selector('span > div > div > div > div > span > a').get_attribute("href")
        except:
            print("cannot find restaurant url")
            url.append(" ")
        else:
            #print(restant_url)
            url.append(restant_url)

    return name, url

def main():
    chrome_path = 'chromedriver'
    option = webdriver.ChromeOptions()
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    option.add_experimental_option('useAutomationExtension', False)
    option.add_argument('--headless')
    browser = webdriver.Chrome(options=option, executable_path=chrome_path)
    # cdp - chrome developer protocol
    browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator,"webdriver",{get:() => undefined})'
    })
    query_url = 'https://www.tripadvisor.co.uk/Restaurants-g190479-c6-Oslo_Eastern_Norway.html'

    browser.get(query_url)
    time.sleep(5)
    name, url = extract_restUrl(browser)
    browser.close()

    result = pd.DataFrame({
        "name": name,
        "RestUrl": url
    })
    df = result.loc[:9, :]
    df.to_excel("rest_url.xlsx", index=False)

if __name__ == "__main__":
    main()
