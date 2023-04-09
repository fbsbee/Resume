from selenium import webdriver
import pandas as pd
import numpy as np

import os
import time
import threading
from multiprocessing import Process

class Crawling_homework(Process):
    '''

    생성자 :
    chromedriver_path = 크롬드라이버 경로 exe파일까지. 맨 앞에 r을 붙이길 권장. ex) r"C:/... .exe"
    url_name = 크롤링할 사이트 주소.
    searching_page = 얼만큼 크롤링 할건지. 게시글 개수. default = 3
    wait_time = 지연 시간. default = 3
    csv_save_folder_path = csv 파일 저장할 디렉토리 생성. 뒤에 '/' 붙여주어야함 default = "./community_crawling/"

    함수 :
    run() 만 해주면 됨.

    '''
    def __init__(self, chromedriver_path, url_name, searching_page=3,
                wait_time=3, csv_save_folder_path='datasets/before/[2020_01_05]NLP/'):
                
        # threading.Thread.__init__(self)
        super(Crawling_homework, self).__init__()

        self.csv_save_folder_path = csv_save_folder_path
        if not os.path.exists(self.csv_save_folder_path):
            os.mkdir(self.csv_save_folder_path)

        self.chromedriver_path = chromedriver_path
        self.url_name = url_name
        self.wait_time = wait_time
        self.searching_page = searching_page

    # 실행 함수
    def run(self,):
        if self.url_name =='ppom':
            self.ppom_crawl(self.wait_time, self.searching_page)

        elif self.url_name =='fm':
            self.fm_crawl(self.wait_time, self.searching_page)

        elif self.url_name == 'dc':
            self.dc_crawl(self.wait_time, self.searching_page)

        elif self.url_name == 'dogdrip':
            self.dogdrip_crawl(self.wait_time, self.searching_page)

        elif self.url_name == 'theqoo':
            self.theqoo_crawl(self.wait_time, self.searching_page)
        else :
            print('안만들었지롱')
    
    # ppom 사이트 크롤링하는 함수 
    def ppom_crawl(self, wait_time, searching_page):
        categories = {
                    # 'ppom_soccer.csv' : 'http://www.ppomppu.co.kr/zboard/zboard.php?id=soccer&page=1&divpage=28',
                    # 'ppom_health.csv' : 'http://www.ppomppu.co.kr/zboard/zboard.php?id=health&page=1&divpage=22',
                    # 'ppom_fashion.csv' : 'http://www.ppomppu.co.kr/zboard/zboard.php?id=style&page=1&divpage=22',
                    'ppom_humor.csv' : 'http://www.ppomppu.co.kr/zboard/zboard.php?id=humor',
                    'ppom_music.csv' : 'http://www.ppomppu.co.kr/zboard/zboard.php?id=music',

                    }

        before_data = {
                    # 'ppom_fashion.csv' : None,
                    # 'ppom_soccer.csv' : None,
                    # 'ppom_health.csv' : None,
                    'ppom_humor.csv' : None,
                    'ppom_music.csv' : None,
                    }

        driver = webdriver.Chrome(executable_path=self.chromedriver_path)
        driver.implicitly_wait(wait_time)

        def inner(number):
            try:
                title = driver.find_element_by_xpath('//td[@class="han"]/font[@class="view_title2"]')
                body = driver.find_element_by_xpath('//td[@class="board-contents"]')
                head = driver.find_element_by_xpath('/html/body/div/div[2]/div[4]/div/table[2]\
                                                    /tbody/tr[3]/td/table/tbody/tr/td[5]')

                head_text = head.text
                start_num = head_text.rfind('등록일:')
                end_num = start_num + 21

                date = head_text[start_num+5:end_num]

                data = np.array([[number, title.text, body.text, date]])
                np.reshape(data, (1, 4))

                return data

            except:
                pass

        for csv_file_name, category in categories.items():

            driver.get(category)
            first_title = driver.find_element_by_xpath('//tr[@class="list0"]//font[@class="list_title"]\
                                                        | //tr[@class="list1"]//font[@class="list_title"]' )
            #다 문자열로 들어가 있음. 배열에 넣어진게 아니라 엔터까지 문자열로 넣어짐.
            first_title.click()

            url = driver.current_url
            start = url.rfind('no=')
            
            number = int(url[start+3:])

            # 전의 데이터가 있으면 url 새로 불러옴
            before_data[csv_file_name] = self.confirm_before_data(csv_file_name)
            if before_data[csv_file_name] is not None:
                number = int(before_data[csv_file_name]) - 1
                url = url[:start+3]+str(number)
                driver.get(url)

            for _ in range(searching_page):
                data = inner(number)
                self.input_csv(csv_file_name, data)
                #다음 페이지 넘어가기 첫페이지는 그냥 버리자
                number -= 1
                url = url[:start+3]+str(number)
                driver.get(url)
                #데이터 추출
                time.sleep(wait_time)
            else:
                data = inner(number)
                self.input_csv(csv_file_name, data)
                
        driver.quit()

    # fm 사이트 크롤링하는 함수
    def fm_crawl(self, wait_time, searching_page):
        categories = {
                    # 'fm_soccer.csv' : 'https://www.fmkorea.com/football_world',
                    # 'fm_health.csv' : 'https://www.fmkorea.com/assapig',
                    # 'fm_fashion.csv' : 'https://www.fmkorea.com/fashion',
                    'fm_humor.csv' : 'https://www.fmkorea.com/humor',
                    'fm_music.csv' : 'https://www.fmkorea.com/music',
                    }

        before_data = {
                    # 'fm_soccer.csv' : None,
                    # 'fm_health.csv' : None,
                    # 'fm_fashion.csv' : None,
                    'fm_humor.csv' : None,
                    'fm_music.csv' : None,
                    }

        driver = webdriver.Chrome(executable_path=self.chromedriver_path)
        driver.implicitly_wait(wait_time)

        def inner(number):
            try:
                title = driver.find_element_by_xpath('//span[@class="np_18px_span"]')
                date = driver.find_element_by_xpath('//span[@class="date m_no"]')
                body = driver.find_element_by_xpath('//div[@class="rd_body clear"]/article')

                data = np.array([[number, title.text, body.text, date.text]])
                np.reshape(data, (1, 4))

                return data
            except:
                pass

        for csv_file_name, category in categories.items():

            driver.get(category)
            title = driver.find_element_by_xpath('//td[contains(@class, "title")\
                                                and contains(@class, "hotdeal_var8")]/a')
            title.click()

            # 전의 데이터가 있으면 url 새로 불러옴
            before_data[csv_file_name] = self.confirm_before_data(csv_file_name)
            if before_data[csv_file_name] is not None:
                url = driver.current_url
                number = before_data[csv_file_name]
                url = url[:url.rfind('/')+1]+str(number)
                driver.get(url)

                # 번호는 넘어가는걸 확인했는데, 내용은 두번 읽혀서 그냥 두번 넘겨버렸음. 제대로 나옴.
                next_page = driver.find_element_by_xpath('//span[contains(@class, "btn_pack")\
                                                        and contains(@class, "next")]/a')
                driver.execute_script("arguments[0].click();", next_page)

                next_page = driver.find_element_by_xpath('//span[contains(@class, "btn_pack")\
                                                        and contains(@class, "next")]/a')
                driver.execute_script("arguments[0].click();", next_page)
                

            for _ in range(searching_page+1):
                url = driver.current_url
                number = url[url.rfind('/')+1:]
                #내용 추출 및 저장
                data = inner(number)
                self.input_csv(csv_file_name, data)
                #다음페이지 넘어가기
                next_page = driver.find_element_by_xpath('//span[contains(@class, "btn_pack")\
                                                        and contains(@class, "next")]/a')
                driver.execute_script("arguments[0].click();", next_page)
                time.sleep(wait_time)
                
            else:
                data = inner(number)
                self.input_csv(csv_file_name, data)
                

        driver.quit()

    # dc 사이트 크롤링하는 함수
    def dc_crawl(self, wait_time, searching_page):
        categories = {
                    # 'dc_soccer.csv' : 'https://gall.dcinside.com/board/lists/?id=football_new6',
                    # 'dc_health.csv' : 'https://gall.dcinside.com/board/lists/?id=extra',
                    # 'dc_fashion.csv' : 'https://gall.dcinside.com/board/lists/?id=fashion70',
                    'dc_humor.csv' : 'https://gall.dcinside.com/board/lists/?id=smile',
                    'dc_music.csv' : 'https://gall.dcinside.com/board/lists/?id=music',
                    }

        before_data = {
                    # 'dc_soccer.csv' : None,
                    # 'dc_health.csv' : None,
                    # 'dc_fashion.csv' : None,
                    'dc_humor.csv' : None,
                    'dc_music.csv' : None,
                    }

        driver = webdriver.Chrome(executable_path=self.chromedriver_path)
        driver.implicitly_wait(wait_time)

        def inner(number):
                try:
                    title = driver.find_element_by_xpath('//span[@class="title_subject"]')
                    date = driver.find_element_by_xpath('//span[@class="gall_date"]')
                    body = driver.find_element_by_xpath('//div[@class="writing_view_box"]')
      
                    body_text = body.text
                    find_dc = body_text.rfind('- dc')
                    if find_dc != -1:
                        body_text = body_text[:find_dc]
                    
                    data = np.array([[number, title.text, body_text, date.text]])
                    np.reshape(data, (1, 4))
                    
                    return data
                except:
                    pass

        for csv_file_name, category in categories.items():

            driver.get(category)
            title = driver.find_element_by_xpath('//tr[contains(@class, "ub-content") and contains(@class, "us-post") \
                                                and (contains(@data-type, "icon_pic") or contains(@data-type, "icon_txt"))]\
                                                /td[contains(@class, "gall_tit") and contains(@class, "ub-word")]/a')
            title.click()

            url = driver.current_url
            start = url.rfind('no=')
            end = url.rfind('&')
            number = int(url[start+3:end])

            # 전의 데이터가 있으면 url 새로 불러옴
            before_data[csv_file_name] = self.confirm_before_data(csv_file_name)
            if before_data[csv_file_name] is not None:
                number = int(before_data[csv_file_name]) - 1
                url = url[:start+3]+str(number)
                driver.get(url)
            
            for _ in range(searching_page):
                #데이터 추출
                data = inner(number)
                self.input_csv(csv_file_name, data)
                #다음 페이지 넘어가기
                number -= 1
                url = url[:start+3]+str(number)
                driver.get(url)
                time.sleep(wait_time)
            else:
                data = inner(number)
                self.input_csv(csv_file_name, data)

        driver.quit()

    # 개드립 사이트 크롤링하는 함수
    # 한 페이지당 20개의 게시글이 있음
    def dogdrip_crawl(self, wait_time, searching_page):
        categories = {
                    'dogdrip_humor.csv': 'https://www.dogdrip.net/index.php?mid=userdog&page=1',
                    'dogdrip_music.csv': 'https://www.dogdrip.net/index.php?mid=music&page=1',
                    }

        before_data = {
                    'dogdrip_humor.csv': None,
                    'dogdrip_music.csv': None,
                    }

        driver = webdriver.Chrome(executable_path=self.chromedriver_path)
        driver.implicitly_wait(wait_time)

        def inner(number):
            try:
                title = driver.find_element_by_xpath('//div[@class="ed"]/div/h4/a[contains(@class, "ed") and \
                                                    contains(@class, "link") and contains(@class, "text-bold")]')
                date = driver.find_element_by_xpath('//*[@id="main"]/div/div[2]/div/div[3]/div[1]/div[1]/div[1]/div[1]/span[2]/span[2]')
                body = driver.find_element_by_xpath(f'//div[contains(@class, "document_{str(number)}_0") and contains(@class, "xe_content")]')

                body_text = body.text[:body.text.rfind('개드립으로')]
                
                data = np.array([[number, title.text, body_text, date.text]])
                np.reshape(data, (1, 4))
                
                return data
            except:
                pass

        def doit():
            titles = driver.find_elements_by_xpath('//td[@class="title"]/a')
            notices = driver.find_elements_by_xpath('//tr[@class="notice"]/td[@class="title"]/a')
            
            titles_href = set([title.get_attribute('href') for title in titles])
            notices_href = set([notice.get_attribute('href') for notice in notices])
            
            titles_href -= notices_href
            
            for page in titles_href:
                driver.get(page)

                number = page[page.rfind('/')+1:]
                data = inner(number)
                self.input_csv(csv_file_name, data)
                time.sleep(wait_time)

        for csv_file_name, category in categories.items():

            driver.get(category)
            
            print(csv_file_name)

            number_of_page = category.rfind('=')+1
            page_num = int(category[number_of_page:])

            for i in range(page_num+1, searching_page+1):
                doit()
                    
                url = category[:number_of_page]+str(i)
                driver.get(url)
            else:
                doit()
            
        driver.quit()
    
    # 더쿠 사이트 크롤링하는 함수
    def theqoo_crawl(self, wait_time, searching_page):
        categories = {

                    'theqoo_humor.csv' : 'https://theqoo.net/index.php?mid=square&filter_mode=normal&category=512000937&page=1',
                    'theqoo_music.csv' : 'https://theqoo.net/index.php?mid=music&page=1',
                    }

        before_data = {
                    
                    'theqoo_humor.csv' : None,
                    'theqoo_music.csv' : None,
                    }

        driver = webdriver.Chrome(executable_path=self.chromedriver_path)
        driver.implicitly_wait(wait_time)

        # 제목, 날짜, 본문 긁는 함수
        def inner(number):
            try:
                title = driver.find_element_by_xpath('//span[@class="title"]/span')
                date = driver.find_element_by_xpath('//div[contains(@class,"side") and contains(@class, "fr")]')
                body = driver.find_element_by_xpath(f'//div[contains(@class, "document_{str(number)}_0") and contains(@class, "xe_content")]')

                data = np.array([[number, title.text, body.text, date.text]])
                np.reshape(data, (1, 4))
                
                return data
            except:
                pass

        def doit():
            titles = driver.find_elements_by_xpath('//td[@class="title"]/a')
            titles_href = [title.get_attribute('href') for title in titles]

            # 각 게시글에 들어가서 크롤링 하는 루프
            for page in titles_href:
                if page.rfind('comment') > 0 or page.rfind('index') < 0:
                    continue
                driver.get(page)

                number = page[page.rfind('=')+1:]
                data = inner(number)
                self.input_csv(csv_file_name, data)
                time.sleep(wait_time)

        for csv_file_name, category in categories.items():

            driver.get(category)
            
            print(csv_file_name)

            number_of_page = category.rfind('=')+1
            page_num = int(category[number_of_page:])

            # 전의 데이터가 있으면 url 새로 불러옴
            # 이거는 before data 로 number를 찾은 다음에 페이지에 있는 게시글 리스트를 불러와서 number를 find 해야함
            # 해당 페이지에 number가 없으면 다음 페이지로 넘어가서 찾음 - > 찾을 때 까지 계속 페이지 넘어감

            # before_data[csv_file_name] = self.confirm_before_data(csv_file_name)
            # if before_data[csv_file_name] is not None:
            #     number = int(before_data[csv_file_name]) - 1
            #     url = url[:start+3]+str(number)
            #     driver.get(url)

            # 한 페이지에 있는 게시글 목록 a 태그 긁고 다음 페이지로 넘어가는 루프
            for i in range(page_num+1, searching_page+1):
                doit()

                url = category[:number_of_page]+str(i)
                driver.get(url)
            else:
                doit()

        driver.quit()
    # 루리웹 사이트 크롤링하는 함수
    def ruliweb_crawl(self, wait_time, searching_page):
        categories = {
                    'ruliweb_social.csv' : 'https://bbs.ruliweb.com/community/board/300148?page=1&cate=527',
                    }

        before_data = {
                    'ruliweb_social.csv' : None,
                    }

        driver = webdriver.Chrome(executable_path=self.chromedriver_path)
        driver.implicitly_wait(wait_time)

        # 제목, 날짜, 본문 긁는 함수
        def inner(number):
            try:
                title = driver.find_element_by_xpath('//span[@class="subject_text"]')
                date = driver.find_element_by_xpath('//div[contains(@class,"side") and contains(@class, "fr")]')
                body = driver.find_element_by_xpath('//div[@class="view_content"]')

                data = np.array([[number, title.text, body.text, date.text]])
                np.reshape(data, (1, 4))
                
                return data
            except:
                pass

        def doit():
            titles = driver.find_elements_by_xpath('//tr[@class="table_body"]/td[@class="subject"]/div[@class="relative"]/a')
            titles_href = [title.get_attribute('href') for title in titles]

            # 각 게시글에 들어가서 크롤링 하는 루프
            for page in titles_href:
                
                driver.get(page)
                social = page.rfind('&')
                number = page[page.rfind('page=')+1:social]

                social = page[social+1:]
                data = inner(number)
                self.input_csv(csv_file_name, data)
                time.sleep(wait_time)

        for csv_file_name, category in categories.items():

            driver.get(category)
            
            print(csv_file_name)

            number_of_page = category.rfind('=')+1
            page_num = int(category[number_of_page:category.rfind('&')])

            # 전의 데이터가 있으면 url 새로 불러옴
            # 이거는 before data 로 number를 찾은 다음에 페이지에 있는 게시글 리스트를 불러와서 number를 find 해야함
            # 해당 페이지에 number가 없으면 다음 페이지로 넘어가서 찾음 - > 찾을 때 까지 계속 페이지 넘어감

            # before_data[csv_file_name] = self.confirm_before_data(csv_file_name)
            # if before_data[csv_file_name] is not None:
            #     number = int(before_data[csv_file_name]) - 1
            #     url = url[:start+3]+str(number)
            #     driver.get(url)

            # 한 페이지에 있는 게시글 목록 a 태그 긁고 다음 페이지로 넘어가는 루프
            for i in range(page_num+1, searching_page+1):
                doit()

                url = category[:number_of_page]+str(i)
                driver.get(url)
            else:
                doit()

        driver.quit()

# 루리웹 사이트 크롤링하는 함수
    def bobaedream_crawl(self, wait_time, searching_page):
        categories = {
                    'bobaedream_social.csv' : 'https://www.bobaedream.co.kr/list?code=politic&s_cate=&maker_no=&model_no=&or_gu=10&or_se=desc&s_selday=&pagescale=30&info3=&noticeShow=&s_select=&s_key=&level_no=&vdate=&type=list&page=1',
                    }

        before_data = {
                    'bobaedream_social.csv' : None,
                    }

        driver = webdriver.Chrome(executable_path=self.chromedriver_path)
        driver.implicitly_wait(wait_time)

        # 제목, 날짜, 본문 긁는 함수
        def inner(number):
            try:
                title = driver.find_element_by_xpath('//span[@class="subject_text"]')
                date = driver.find_element_by_xpath('//div[contains(@class,"side") and contains(@class, "fr")]')
                body = driver.find_element_by_xpath('//div[@class="view_content"]')

                data = np.array([[number, title.text, body.text, date.text]])
                np.reshape(data, (1, 4))
                
                return data
            except:
                pass

        def doit():
            titles = driver.find_elements_by_xpath('//td[@class="pl14"]/a[@class="bsubject"]')
            titles_href = [title.get_attribute('href') for title in titles]

            # 각 게시글에 들어가서 크롤링 하는 루프
            for page in titles_href:
                
                driver.get(page)
                number = page[page.rfind('=')+1:]

                data = inner(number)
                self.input_csv(csv_file_name, data)
                time.sleep(wait_time)

        for csv_file_name, category in categories.items():

            driver.get(category)
            
            print(csv_file_name)

            number_of_page = category.rfind('=')+1
            page_num = int(category[number_of_page:])

            # 전의 데이터가 있으면 url 새로 불러옴
            # 이거는 before data 로 number를 찾은 다음에 페이지에 있는 게시글 리스트를 불러와서 number를 find 해야함
            # 해당 페이지에 number가 없으면 다음 페이지로 넘어가서 찾음 - > 찾을 때 까지 계속 페이지 넘어감

            # before_data[csv_file_name] = self.confirm_before_data(csv_file_name)
            # if before_data[csv_file_name] is not None:
            #     number = int(before_data[csv_file_name]) - 1
            #     url = url[:start+3]+str(number)
            #     driver.get(url)

            # 한 페이지에 있는 게시글 목록 a 태그 긁고 다음 페이지로 넘어가는 루프
            for i in range(page_num+1, searching_page+1):
                doit()

                url = category[:number_of_page]+str(i)
                driver.get(url)
            else:
                doit()

        driver.quit()

    # 에펨이랑 dc는 utf-8이 아니라면 간혹 오류 뜨는게 있고 뽐뿌는 무조건 utf-8로 읽어야 함.
    def input_csv(self, csv_file_name, data):
        # encoding = 'cp949'
        # encoding = 'euc-kr'
        encoding = 'utf-8'
        community_csv = pd.DataFrame(data)
        community_csv.to_csv(self.csv_save_folder_path + csv_file_name, sep='\t', mode='a', header=False, encoding=encoding)
    
    # 댓글 저장하는 함수
    def comment_input_csv(self, csv_file_name, data):
        encoding = 'utf-8'
        community_csv = pd.DataFrame(data)
        community_csv.to_csv(self.csv_save_folder_path+'comment/'+csv_file_name, sep='\t', mode='a', header=False, encoding=encoding)

    def confirm_before_data(self, csv_file_name):
        # encoding = 'cp949'
        # encoding = 'euc-kr'
        encoding = 'utf-8'
        if not os.path.exists(self.csv_save_folder_path+csv_file_name):
            community_csv = pd.DataFrame(columns=['글번호', '제목', '내용', '날짜'])
            community_csv.to_csv(self.csv_save_folder_path + csv_file_name, sep='\t', mode='a', header=True, encoding=encoding)
            before_data = None
        else :
            dataset = pd.read_csv(self.csv_save_folder_path + csv_file_name, encoding=encoding)
            try:
                before_data = dataset.tail(1)['글번호'].item()
            except:
                before_data = None
                
        return before_data


if __name__ == "__main__":

    chromedriver_path = r'C:/Chromedriver/chromedriver.exe'
    searching_page = 2
    wait_time = 3

    ppom = Crawling_homework(chromedriver_path, 'ppom', searching_page=searching_page, wait_time=wait_time)
    fm = Crawling_homework(chromedriver_path, 'fm', searching_page=searching_page, wait_time=wait_time)
    dc = Crawling_homework(chromedriver_path, 'dc', searching_page=searching_page, wait_time=wait_time)
    dogdrip = Crawling_homework(chromedriver_path, 'dogdrip', searching_page=searching_page, wait_time=wait_time)
    theqoo = Crawling_homework(chromedriver_path, 'theqoo', searching_page=searching_page, wait_time=wait_time)

    # ppom.start()
    # fm.start()
    # dc.start()
    dogdrip.start()
    # theqoo.start()
