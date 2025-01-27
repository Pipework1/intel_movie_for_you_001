from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import pandas as pd
import re
import time
import datetime

options = ChromeOptions()
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.57'
options.add_argument('user-agent='+user_agent)
options.add_argument('lang=ko_KR')
# options.add_argument('window-size=1920x1080')
# options.add_argument('disable-gpu')
# options.add_argument('--no-sandbox')

service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

years = [2021, 2022, 2023]
titles = ['소울','극장판 귀멸의 칼날: 무한열차편','세자매','명탐정 코난: 진홍의 수학여행','나는 나를 해고하지 않는다','화양연화','미션 파서블','카오스 워킹','톰과 제리','고백','퍼펙트 케어','고질라 VS. 콩','미나리','더 박스',
          '라야와 마지막 드래곤','최면']

for year in years[1:]:
    for month in range(1,13):
        df_movies = pd.DataFrame()
        url = 'https://movie.daum.net/ranking/boxoffice/monthly?date='
        date = str(year)+str('%02d'%month)
        url = url+date
        driver.get(url)
        time.sleep(5)

        for movie in range(1, 31):
            reviews = []
            movie_title = driver.find_element('xpath','//*[@id="mainContent"]/div/div[2]/ol/li[{}]/div/div[2]/strong/a'.format(movie))
            title = movie_title.text
            if title in titles:
                continue
            else:
                try:
                    titles.append(title)
                    movie_title.click()
                    time.sleep(2)
                    movie_review = driver.find_element('xpath','//*[@id="mainContent"]/div/div[2]/div[1]/ul/li[4]/a/span').click()
                    time.sleep(2)

                    button_cnt = driver.find_element('xpath','//*[@id="mainContent"]/div/div[2]/div[2]/div/strong/span').text
                    button_cnt = re.sub(r'[^0-9]','',button_cnt)
                    button_cnt = 1+(int(button_cnt)-10)//30 if 1+(int(button_cnt)-10)//30 < 5 else 5 # 총 리뷰 개수를 찾아서 리뷰 더보기 누를 횟수 계산

                    for i in range(button_cnt):
                        review_button = driver.find_element('xpath','//*[@id="alex-area"]/div/div/div/div[3]/div[1]/button').click()
                        time.sleep(1)
                    for r in range(1,161):
                        try:
                            review = driver.find_element('xpath','/html/body/div[2]/main/article/div/div[2]/div[2]/div/div/div[2]/div/div/div/div[3]/ul[2]/li[{}]/div/p'.format(r)).text
                            if review != '':
                                review = re.compile('[^가-힣]').sub(' ',review)
                                reviews.append(review)
                        except:
                            print('Error %d%02d movie %d %dth review'%(year,month, movie, r))
                    df_movie_review = pd.DataFrame(reviews, columns=['review'])
                    df_movie_review['title'] = title
                    df_movies = pd.concat([df_movies, df_movie_review], ignore_index=True)
                    df_movies = df_movies.reindex(['title','review'],axis=1)
                except:
                    driver.back()
                    time.sleep(2)
                    continue
            if movie % 5 == 0:
                df_movies.to_csv('./crawling_data/movie_reviews_%d%02d_%d.csv'%(year,month,movie),index=False)

            driver.back()
            time.sleep(2)
            driver.back()
            time.sleep(2)
