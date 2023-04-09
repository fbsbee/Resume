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

    # 문제점
    1. before data 가져 오는것. -> 페이지에서 긁고 글번호가 있는지 ... 시작하는 페이지를 모르겠는데. 
                                  글번호가 시작하는 페이지를 가져올 수가 없음. 계속 변동 됨.
    2. 그 다음 페이지가 없어도 페이지 값이 증가하면 계속 마지막 페이지에 머무름. -> 페이지 수 확인. 말고 

    # 해야할 것
    1. 페이지 글 목록 읽을 때, 글번호까지 같이 읽어서 저장
    
    '''

    def __init__(self, chromedriver_path, searching_page=3,
                wait_time=3, csv_save_folder_path='datasets/before/[2020_01_05]NLP/'):
                
        # threading.Thread.__init__(self)
        
        # class 별로 사이트를 나누어서 다른 페이지 개수를 크롤링 할 수도 있게 Process 상속.
        super(Crawling_homework, self).__init__()
        # Process.__init__(self)

        self.csv_save_folder_path = csv_save_folder_path
        if not os.path.exists(self.csv_save_folder_path):
            os.mkdir(self.csv_save_folder_path)

        self.chromedriver_path = chromedriver_path
        self.wait_time = wait_time
        self.searching_page = searching_page

        # 그 다음 페이지가 없어도 페이지 값이 증가하면 계속 마지막 페이지에 머무름. 맨 첫번째 게시글 저장할 변수
        self.titles_href = None

    # 실행 함수
    def run(self, *url_name):
        func_name = {'ppom' : self.ppom_crawl, 'fm' : self.fm_crawl, 'dc' : self.dc_crawl,
            'dogdrip' : self.dogdrip_crawl, 'theqoo' : self.theqoo_crawl,
            'ruliweb' : self.ruliweb_crawl, 'bobaedream' : self.bobaedream_crawl,
            }

        a = [Process(target=func_name[name], args=(self.wait_time, self.searching_page)) for name in url_name]

        for pc in a:
            pc.start()
        for pc in a:
            pc.join()

    # ppom 사이트 크롤링하는 함수 
    def ppom_crawl(self, wait_time, searching_page):
        categories = {
                    # 'ppom_soccer.csv' : 'http://www.ppomppu.co.kr/zboard/zboard.php?id=soccer&page=1&divpage=28',
                    # 'ppom_fashion.csv' : 'http://www.ppomppu.co.kr/zboard/zboard.php?id=style&page=1&divpage=22',
                    # 'ppom_health.csv' : 'http://www.ppomppu.co.kr/zboard/zboard.php?id=health&page=1&divpage=22',
                    'ppom_humor.csv' : 'http://www.ppomppu.co.kr/zboard/zboard.php?id=humor&page=1&divpage=66',
                    'ppom_music.csv' : 'http://www.ppomppu.co.kr/zboard/zboard.php?id=music&page=1&divpage=7',
                    }

        before_data = {a : None for a in categories.keys()}

        driver = webdriver.Chrome(executable_path=self.chromedriver_path)
        driver.implicitly_wait(wait_time)
        
        def crawled_data(number):
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

        def doit(before_data=None):
            
            titles = driver.find_elements_by_xpath('//tr[@class="list0"]/td[@class="list_vspace"]/a \
                                                        | //tr[@class="list1"]/td[@class="list_vspace"]/a' )

            titles_href = [title.get_attribute('href') for title in titles]
            
            #첫번째 게시글 링크 저장
            if self.titles_href in titles_href:
                return False

            self.titles_href = titles_href[0]
            
            for page in titles_href:
                driver.get(page)

                number_name = 'no='

                # 글번호
                number = page[page.rfind(number_name)+len(number_name):]

                data = crawled_data(number)
                self.input_csv(csv_file_name, data)
                time.sleep(wait_time)
            return True

        for csv_file_name, category in categories.items():

            driver.get(category)
            
            print(csv_file_name)

            start = '&page='
            end = '&'
            start_number_of_page = category.rfind(start)+len(start)
            end_number_of_page = category.rfind(end)

            page_num = int(category[start_number_of_page:end_number_of_page])

            # before_data[csv_file_name] = self.confirm_before_data(csv_file_name)
            
            # end_category = doit(before_data[csv_file_name])
            # if end_category == False:
            #     break
            
            doit()
            for i in range(page_num+1, searching_page):
                
                url = category[:start_number_of_page]+str(i)+ category[end_number_of_page:]
                driver.get(url)
                end_category = doit()
                if end_category == False:
                    break
            # else:
            #     doit()
            
        driver.quit()
        print('finish', categories.keys())
        
    # fm 사이트 크롤링하는 함수
    def fm_crawl(self, wait_time, searching_page):
        categories = {
                    # 'fm_soccer.csv' : 'https://www.fmkorea.com/football_world',
                    # 'fm_fashion.csv' : 'https://www.fmkorea.com/fashion',
                    # 'fm_health.csv' : 'https://www.fmkorea.com/assapig',
                    'fm_humor.csv' : 'https://www.fmkorea.com/index.php?mid=humor&page=1',
                    'fm_music.csv' : 'https://www.fmkorea.com/index.php?mid=music&page=1',
                    }

        before_data = {a : None for a in categories.keys()}

        driver = webdriver.Chrome(executable_path=self.chromedriver_path)
        driver.implicitly_wait(wait_time)

        def crawled_data(number):
            try:
                title = driver.find_element_by_xpath('//span[@class="np_18px_span"]')
                date = driver.find_element_by_xpath('//span[@class="date m_no"]')
                body = driver.find_element_by_xpath('//div[@class="rd_body clear"]/article')

                data = np.array([[number, title.text, body.text, date.text]])
                np.reshape(data, (1, 4))

                return data
            except:
                pass

        def doit():
            
            titles = driver.find_elements_by_xpath('//tbody/tr/td[@class="title hotdeal_var8"]/a[1]' )
            
            titles_href = [title.get_attribute('href') for title in titles]
            #첫번째 게시글 링크 저장
            if self.titles_href in titles_href:
                return False

            self.titles_href = titles_href[0]

            print(titles_href)

            for page in titles_href:
                driver.get(page)

                number_name = '/'

                # 글번호
                number = page[page.rfind(number_name)+len(number_name):]

                data = crawled_data(number)
                self.input_csv(csv_file_name, data)
                time.sleep(wait_time)
            return True

        for csv_file_name, category in categories.items():

            driver.get(category)
            
            print(csv_file_name)

            start = '='
            # end = '&'
            start_number_of_page = category.rfind(start)+len(start)
            # end_number_of_page = category.rfind(end)

            page_num = int(category[start_number_of_page:])
            doit()
            
            for i in range(page_num+1, searching_page):
                
                url = category[:start_number_of_page]+str(i)
                driver.get(url)
                end_category = doit()
                if end_category == False:
                    break
            
        driver.quit()
        print('finish', categories.keys())

    # dc 사이트 크롤링하는 함수
    def dc_crawl(self, wait_time, searching_page):
        categories = {
                    # 'dc_soccer.csv' : 'https://gall.dcinside.com/board/lists/?id=football_new6',
                    # 'dc_fashion.csv' : 'https://gall.dcinside.com/board/lists/?id=fashion70',
                    # 'dc_health.csv' : 'https://gall.dcinside.com/board/lists/?id=extra',
                    'dc_humor.csv' : 'https://gall.dcinside.com/board/lists/?id=smile&page=1',
                    'dc_music.csv' : 'https://gall.dcinside.com/board/lists/?id=music&page=1',
                    }

        before_data = {a : None for a in categories.keys()}

        driver = webdriver.Chrome(executable_path=self.chromedriver_path)
        driver.implicitly_wait(wait_time)

        def crawled_data(number):
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
        def doit():
            
            titles = driver.find_elements_by_xpath('//tbody/tr[@data-type="icon_pic"]/td[@class="gall_tit ub-word"]/a[1]\
                                                    | //tbody/tr[@data-type="icon_txt"]/td[@class="gall_tit ub-word"]/a[1]' )
            
            titles_href = [title.get_attribute('href') for title in titles]
            #첫번째 게시글 링크 저장
            if self.titles_href in titles_href:
                return False

            self.titles_href = titles_href[0]

            print(titles_href, len(titles_href))

            for page in titles_href:
                driver.get(page)

                number_name = 'no='
                end = page.rfind('&')
                number = int(page[page.rfind(number_name)+len(number_name):end])

                # 글번호
                # number = page[page.rfind(number_name)+len(number_name):]

                data = crawled_data(number)
                self.input_csv(csv_file_name, data)
                time.sleep(wait_time)
            return True

        for csv_file_name, category in categories.items():

            driver.get(category)
            
            print(csv_file_name)

            start = '='
            # end = '&'
            start_number_of_page = category.rfind(start)+len(start)
            # end_number_of_page = category.rfind(end)
            print('page_num', category[start_number_of_page:])
            page_num = int(category[start_number_of_page:])
            
            doit()
            
            for i in range(page_num+1, searching_page):
                
                url = category[:start_number_of_page]+str(i)
                driver.get(url)
                end_category = doit()
                if end_category == False:
                    break
                print('page number = ', i)
            
        driver.quit()
        print('finish', categories.keys())

    # 개드립 사이트 크롤링하는 함수
    # 한 페이지당 20개의 게시글이 있음
    def dogdrip_crawl(self, wait_time, searching_page):
        categories = {
                    'dogdrip_humor.csv': 'https://www.dogdrip.net/index.php?mid=userdog&page=1',
                    'dogdrip_music.csv': 'https://www.dogdrip.net/index.php?mid=music&page=1',
                    }

        before_data = {a : None for a in categories.keys()}

        driver = webdriver.Chrome(executable_path=self.chromedriver_path)
        driver.implicitly_wait(wait_time)

        def crawled_data(number):
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
                data = crawled_data(number)
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
        print('finish', categories.keys())
    
    # 더쿠 사이트 크롤링하는 함수
    def theqoo_crawl(self, wait_time, searching_page):
        categories = {
                    'theqoo_humor.csv' : 'https://theqoo.net/index.php?mid=square&filter_mode=normal&category=512000937&page=1',
                    'theqoo_music.csv' : 'https://theqoo.net/index.php?mid=music&page=1',
                    }

        before_data = {a : None for a in categories.keys()}

        driver = webdriver.Chrome(executable_path=self.chromedriver_path)
        driver.implicitly_wait(wait_time)

        # 제목, 날짜, 본문 긁는 함수
        def crawled_data(number):
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
                data = crawled_data(number)
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
        print('finish', categories.keys())
    # 루리웹 사이트 크롤링하는 함수
    def ruliweb_crawl(self, wait_time, searching_page):
        categories = {
                    'ruliweb_social.csv' : 'https://bbs.ruliweb.com/community/board/300148?page=1&cate=527',
                    }

        before_data = {a : None for a in categories.keys()}

        driver = webdriver.Chrome(executable_path=self.chromedriver_path)
        driver.implicitly_wait(wait_time)

        # 제목, 날짜, 본문 긁는 함수
        def crawled_data(number):
            try:
                title = driver.find_element_by_xpath('//span[@class="subject_text"]')
                date = driver.find_element_by_xpath('//span[@class="regdate"]')
                body = driver.find_element_by_xpath('//div[@class="view_content"]')

                data = np.array([[number, title.text, body.text, date.text[:10]]])
                np.reshape(data, (1, 4))
                
                return data
            except:
                pass

        def comment_data(number):
            try:
                comments = driver.find_elements_by_xpath('//tr[contains(@class, "comment_element") and contains(@class, "normal")]\
                                                      /td[@class="comment"]/div[@class="text_wrapper"]/span[@class="text"]')
                
                for comment in comments:
                    comment_data = np.array([[number, comment.text]])
                    np.reshape(comment_data, (1, 2))
                    self.comment_input_csv(csv_file_name, comment_data)
            except:
                pass

        def doit():
            titles = driver.find_elements_by_xpath('//tr[@class="table_body"]/td[@class="subject"]/div[@class="relative"]/a')
            titles_href = [title.get_attribute('href') for title in titles]

            # 각 게시글에 들어가서 크롤링 하는 루프
            for page in titles_href:
                
                driver.get(page)
                number = int(page[page.rfind('/')+len('/'):page.rfind('?')])
                data = crawled_data(number)
                comment_data(number)
                self.input_csv(csv_file_name, data)
                print('where : ', data)
                time.sleep(wait_time)

        for csv_file_name, category in categories.items():

            driver.get(category)
            
            print(csv_file_name)

            number_of_page = category.rfind('page=')
            
            page_num = int(category[number_of_page+len('page='):category.rfind('&')])

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
        print('finish', categories.keys())

    # 보배드림 사이트 크롤링하는 함수
    def bobaedream_crawl(self, wait_time, searching_page):
        categories = {
                    'bobaedream_social.csv' : 'https://www.bobaedream.co.kr/list?code=politic&s_cate=&maker_no=&model_no=&or_gu=10&or_se=desc&s_selday=&pagescale=30&info3=&noticeShow=&s_select=&s_key=&level_no=&vdate=&type=list&page=1',
                    }

        before_data = {a : None for a in categories.keys()}

        driver = webdriver.Chrome(executable_path=self.chromedriver_path)
        driver.implicitly_wait(wait_time)

        # 제목, 날짜, 본문 긁는 함수
        def crawled_data(number):
            try:
                title = driver.find_element_by_xpath('//strong[@itemprop="name"]')
                date = driver.find_element_by_xpath('//span[@class="countGroup"]')
                body = driver.find_element_by_xpath('//div[@class="bodyCont"]')

                date = date.text
                date = date[date.rfind('| ')+len('| ') : date.rfind(' (')]
                # print('날짜 :', date)
                data = np.array([[number, title.text, body.text, date]])
                np.reshape(data, (1, 4))
                
                return data
            except:
                pass
        def comment_data(number):
            try:
                comments = driver.find_elements_by_xpath('//div[@class="commentlistbox"]/ul[@class="basiclist"]/li/dl/dd')
                
                for comment in comments:
                    comment_data = np.array([[number, comment.text]])
                    np.reshape(comment_data, (1, 2))
                    self.comment_input_csv(csv_file_name, comment_data)
            except:
                pass
        def doit():
            titles = driver.find_elements_by_xpath('//td[@class="pl14"]/a[@class="bsubject"]')
            titles_href = [title.get_attribute('href') for title in titles]
            print(titles_href)
            # 각 게시글에 들어가서 크롤링 하는 루프
            for page in titles_href:
                
                driver.get(page)
                number = int(page[page.rfind('No=')+len('No='):page.rfind('&')])
                
                comment_data(number)
                print('===========================')

                data = crawled_data(number)
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
        print('finish', categories.keys())

    # 에펨이랑 dc는 utf-8이 아니라면 간혹 오류 뜨는게 있고 뽐뿌는 무조건 utf-8로 읽어야 함.
    def input_csv(self, csv_file_name, data):
        # encoding = 'cp949'
        # encoding = 'euc-kr'
        encoding = 'utf-8'
        community_csv = pd.DataFrame(data)
        community_csv.to_csv(self.csv_save_folder_path + csv_file_name, sep='\t', mode='a', header=False, encoding=encoding)
    
    # 댓글 저장하는 함수
    def comment_input_csv(self, csv_file_name, data):
        if not os.path.isdir(self.csv_save_folder_path+'comment/'):
            os.mkdir(self.csv_save_folder_path+'comment/')
        encoding = 'utf-8'
        community_csv = pd.DataFrame(data)
        community_csv.to_csv(self.csv_save_folder_path+'comment/comment_'+csv_file_name, sep='\t', mode='a', header=False, encoding=encoding)

    # 전 데이터 확인하는 함수
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
    searching_page = 1
    wait_time = 0

    a = Crawling_homework(chromedriver_path, searching_page=searching_page, wait_time=wait_time)
    a.run(
        # 'ppom',
        'fm',
        # 'dc',
        # 'dogdrip',
        # 'theqoo',
        # 'ruliweb',
        # 'bobaedream',
    )
