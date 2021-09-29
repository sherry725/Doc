import time
import pandas as pd
from selenium import webdriver
#from selenium.webdriver.common.keys import Keys

def extract_content(browser):
    try:
        list_div = browser.find_elements_by_xpath('//div[@class="review-container"]')
    except:
        print("cannot find any review")
        return None
    title = []
    rating = []
    review_content = []
    date_of_review = []
    date_of_visit = []
    for item in list_div:
        try:
            quote = item.find_element_by_xpath('.//span[@class="noQuotes"]').text
            #restant_name = item.find_element_by_xpath('./span/div/div/div/div/span/a').text
        except:
            print("cannot find review title")
            title.append(" ")
        else:
            print(quote)
            title.append(quote)

        try:
            rate = item.find_element_by_xpath('.//span[contains(@class, "ui_bubble_rating")]').get_attribute("class")
        except:
            print("cannot find rating")
            rating.append(" ")
        else:
            print(rate)
            rating.append(rate)

        try:
            review = item.find_element_by_xpath('.//p[@class="partial_entry"]').text
        except:
            print("cannot find review")
            review_content.append(" ")
        else:
            print(review)
            review_content.append(review)

        try:
            revDate = item.find_element_by_xpath('.//span[@class="ratingDate"]').get_attribute("title")
        except:
            print("cannot find review date")
            date_of_review.append(" ")
        else:
            print(revDate)
            date_of_review.append(revDate)

        try:
            visDate = item.find_element_by_xpath('.//div[contains(@class,"prw_reviews_stay_date")]').text
        except:
            print("cannot find visit date")
            date_of_visit.append(" ")
        else:
            print(visDate)
            date_of_visit.append(visDate)

    return title, rating, review_content, date_of_review, date_of_visit

def extract_pageUrl(browser):
    page_dict = {}
    try:
        page_urls = browser.find_elements_by_css_selector('.pageNumbers > a')
    except:
        print("cannot find page url")
    else:
        for url in page_urls:
            page_dict[url.get_attribute("data-page-number")] = url.get_attribute("href")
    return page_dict

def main():
    df = pd.read_excel("rest_url.xlsx")
    print(df.shape)
    chrome_path = 'chromedriver'
    option = webdriver.ChromeOptions()
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    option.add_experimental_option('useAutomationExtension', False)
    option.add_argument('--headless')
    new_df = False
    for i, row in df.iterrows():
        browser = webdriver.Chrome(options=option, executable_path=chrome_path)
        # cdp - chrome developer protocol
        browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator,"webdriver",{get:() => undefined})'
        })
        page_url = []
        query_url = row['RestUrl']
        try:
            browser.get(query_url)
        except:
            break
        time.sleep(5)
        page_root = extract_pageUrl(browser)
        title, rating, review_content, date_of_review, date_of_visit = extract_content(browser)
        page_url.extend([query_url]*len(title))
        browser.close()

        for i in range(2,11):
            driver = webdriver.Chrome(options=option, executable_path=chrome_path)
            # cdp - chrome developer protocol
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': 'Object.defineProperty(navigator,"webdriver",{get:() => undefined})'
            })
            try:
                driver.get(page_root[str(i)])
            except:
                break
            time.sleep(5)
            sub_title, sub_rating, sub_review, sub_date_review, sub_date_visit = extract_content(driver)
            page_sub = extract_pageUrl(driver)
            page_root.update(page_sub)
            title.extend(sub_title)
            rating.extend(sub_rating)
            review_content.extend(sub_review)
            date_of_review.extend(sub_date_review)
            date_of_visit.extend(sub_date_visit)
            page_url.extend([page_root[str(i)]]*len(sub_title))
            driver.close()

        result = pd.DataFrame({
            "title": title,
            "rating": rating,
            "reviews": review_content,
            "date_of_review": date_of_review,
            "date_of_visit": date_of_visit,
            "pageUrl": page_url
        })
        result['Restaurant'] = row['name']
        if new_df is False:
            new_df = result.copy()
        else:
            new_df = pd.concat([new_df, result])

    new_df.to_excel("ta_review.xlsx", index=False)

if __name__ == "__main__":
    main()
