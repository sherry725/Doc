from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep
from lxml import etree
import csv,re
from pyquery import PyQuery as pq
import pandas as pd
import time


class Tmall_Product_Spider():
    def __init__(self):
        self.keyword = input("请输入要采集商品的关键字：")  # 商品的关键字
        option = ChromeOptions()
        option.add_experimental_option('excludeSwitches', ['enable-automation'])  # 开启实验性功能
        option.add_experimental_option('prefs',{'profile.managed_default_content_settings.images': 2}) #禁止图片加载
        option.add_argument('--proxy-server=http://127.0.0.1:9000')
        self.bro = webdriver.Chrome(options=option)
        self.wait = WebDriverWait(self.bro, 10)

    # 翻页操作
    def next_page(self, page_number):
        try:
            self.bro.find_element_by_class_name('logo').click()
            sleep(20)
            input_search = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, 's-combobox-input')))
            input_search.send_keys(self.keyword)
            sleep(20)
        except:
            print("not blocked")
        # 等待该页面input输入框加载完毕
        next_wait = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ui-page > div.ui-page-wrap > b.ui-page-skip > form > input.ui-page-skipTo')))
        # 等待该页面的确定按钮加载完毕
        submit = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ui-page > div.ui-page-wrap > b.ui-page-skip > form > button.ui-btn-s')))
        # 清除里面的数字
        next_wait.clear()
        # 重新输入数字
        next_wait.send_keys(page_number)
        # 强制延迟1秒，防止被识别成机器人
        sleep(1)
        # 点击确定按钮
        submit.click()


    # 模拟向下滑动浏览
    def swipe_down(self,second):
        for i in range(int(second/0.1)):
            js = "var q=document.documentElement.scrollTop=" + str(300+200*i)
            self.bro.execute_script(js)
            sleep(0.1)
        js = "var q=document.documentElement.scrollTop=100000"
        self.bro.execute_script(js)
        sleep(0.2)

    def Get_Product_Data(self):
        self.bro.maximize_window()
        self.bro.get("https://list.tmall.com/search_product.htm?s=0&q=%s"%(self.keyword))
        print("-" * 30 + "扫码登录" + "-" * 30)
        sleep(20)
        try:
            self.bro.find_element_by_class_name('logo').click()
            sleep(20)
            input_search = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, 's-combobox-input')))
            input_search.send_keys(self.keyword)
            sleep(20)
            # 使用Keys的ENTER,相当于.click()函数
            input_search.send_keys(Keys.ENTER)
        except:
            print("not blocked")
        #page = self.bro.find_element_by_xpath('//form[@name="filterPageForm"]').text
        #page=int(re.findall('(\d+)',page)[0])
        # 获取天猫商品总共的页数
        # 等待本页面全部天猫商品数据加载完毕
        #self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#J_ItemList > div.product > div.product-iWrap')))
        sleep(20)
        # 获取天猫商品总共页数
        number_total = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.ui-page > div.ui-page-wrap > b.ui-page-skip > form')))
        page_total = number_total.text.replace("共", "").replace("页，到第页 确定", "").replace("，", "")
        print("%s共检索到%s页数据" % (self.keyword,page_total))

        #self.start_page=input("请输入起始页数：")
        #self.end_page=input("请输入结束页数：")

        product_title = []
        product_status = []
        product_price = []
        product_url = []


        for page in range(2, int(page_total)+2):

            # 等待该页面全部商品数据加载完毕
            #self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#J_ItemList > div.product > div.product-iWrap')))

            # 等待该页面input输入框加载完毕
            input_wait = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '.ui-page > div.ui-page-wrap > b.ui-page-skip > form > input.ui-page-skipTo')))
            # 获取当前页
            now_page = input_wait.get_attribute('value')
            print("当前页数" + now_page + ",总共页数" + page_total)
            # 获取本页面源代码
            html = self.bro.page_source
            # pq模块解析网页源代码
            doc = pq(html)
            # 存储天猫商品数据
            good_items = doc('#J_ItemList .product').items()
            # 遍历该页的所有商品
            for item in good_items:
                good_title = item.find('.productTitle').text().replace('\n', "").replace('\r', "")
                product_title.append(good_title)
                good_status = item.find('.productStatus').text().replace(" ", "").replace("笔", "").replace('\n',"").replace('\r', "")
                product_status.append(good_status)
                good_price = item.find('.productPrice').text().replace("¥", "").replace(" ", "").replace('\n',"").replace('\r', "")
                product_price.append(good_price)
                good_url = item.find('.productImg').attr('href')
                product_url.append(good_url)
                # print(good_title + "   " + good_status + "   " + good_price + "   " + good_url + '\n')

            # 精髓之处，大部分人被检测为机器人就是因为进一步模拟人工操作
            # 模拟人工向下浏览商品，即进行模拟下滑操作，防止被识别出是机器人
            self.swipe_down(2)

            if int(now_page)<int(page_total):
            # 翻页，下一页
                self.next_page(page)

            # 等待滑动验证码出现,超时时间为5秒，每0.5秒检查一次
            # 大部分情况不会出现滑动验证码，所以如果有需要可以注释掉下面的代码
            sleep(5)
            # WebDriverWait(self.bro, 5, 0.5).until(EC.presence_of_element_located((By.ID, "nc_1_n1z")))  # 等待滑动拖动控件出现
        #self.bro.quit()
        return product_title,product_status,product_price,product_url

    def Page_Slider_Slide(self):
        Slider = self.bro.find_element_by_xpath('//*[@id="nc_1_n1z"]')
        # 动作链
        action = ActionChains(self.bro)
        # 点击长按指定的标签
        action.click_and_hold(Slider).perform()
        action.move_by_offset(xoffset=260, yoffset=0).perform()
        action.release()


if __name__ == '__main__':
    Spider=Tmall_Product_Spider()
    product_title, product_status, product_price, product_url = Spider.Get_Product_Data()
    df=pd.DataFrame({'product_title':product_title,
                     'product_status': product_status,
                     'product_price': product_price,
                     'product_url': product_url})
    df.to_excel("olly.xlsx", index=False)
