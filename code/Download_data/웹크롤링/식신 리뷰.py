from bs4 import BeautifulSoup
from selenium import webdriver
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import numpy as np
from pathlib import Path

lists = pd.read_csv('links3.csv', delimiter=',', lineterminator='\n', header=None)
names = lists.iloc[:, 0]
links = lists.iloc[:, 1]

'''
리뷰 개수, 감성분석 결과 -> 긍정/부정 퍼센트, 별점

각 지표값마다 추천/비추천 경우
예: 리뷰개수 많음, 부정 많음, 별점 낮음 -> 추천 점수가 높다 (더 높음)
예: 리뷰개수 적음, 긍정 많음, 별점 높음 -> 추천 점수가 높다

클러스터링
집단이 생긴다? -> 공통점 찾아서 기준을 찾아서 정해야한다.
안생긴다? -> 가게 매출은 알 수 없음, 리뷰개수/별점-> 정답지로 해서 오피니언 분석(점수)만 진행
'''


for i in range(links.size):
    # webdriver 불러오기
    driver = webdriver.Chrome(ChromeDriverManager().install())

    # list 부르기
    l = links.iloc[i]
    link = f'{l}'.strip()
    print('link : ', link)

    driver.get(link)

    body = driver.find_element_by_tag_name("body")

    # driver.maximize_window()

    num_of_pagedowns = 50
    while num_of_pagedowns:
        # 원하는 위치로 이동하기
        # sMore = "//a[@class='btn_sMore']"
        # #//*[@id="siksin_review"]/div[3]/a/span

        num_of_pagedowns -= 1
        try:
            sMore = '//*[@id="siksin_review"]/div[3]/a/span'
            element = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, sMore)))
            loc = element.location['y']
            driver.execute_script(f"window.scrollTo(0, {loc - 100})")
            time.sleep(0.5)

            driver.find_element_by_xpath(sMore).click()
            time.sleep(0.5)
            # driver.find_element_by_xpath("/html/body/div/div/div/div[1]/div/div/div/div[5]/div[1]/div/div[5]/div[3]/a/span").click()
        except:
            break

    html = driver.page_source
    result = BeautifulSoup(html, 'html.parser')

    body = result.find("body")
    review = body.select("div > div[class~=cnt] > div[class~=score_story] > p:last-child")  # 댓글 불러오는거 수정
    ##siksin_review > div.rList > ul > li:nth-child(_) > div > div.cnt > div.score_story > p
    ###siksin_review > div.rList > ul > li:nth-child(53) > div > div.reply_write_list > div > div.list > ul > li:nth-child(4) > div > div > div.score_story > p

    score = body.select(
        "div.score_story > div > span > strong")  # siksin_review > div.rList > ul > li:nth-child(36) > div > div.cnt > div.score_story > div > span > strong
    kind = body.select_one(
        '#contents > div > div > div.content > div.sec_left > div > div:nth-child(1) > div:nth-child(1) > p').get_text().strip()

    for ptag in review:
        txt = ptag.get_text().strip().replace('\n', ' ').replace(';','')
        with open(f'review/review_{link.split("/")[-1]}.txt', 'a', encoding='UTF-8') as f:
            f.write(txt + ';' + '\n')

    for s in score:
        sc = s.get_text().strip()
        with open(f'score/score_{link.split("/")[-1]}.txt', 'a', encoding='UTF-8') as f:
            f.write(sc + ';' + '\n')

    # 데이터 불러와서 csv로 만든다.
    data_review = pd.read_csv(f'review/review_{link.split("/")[-1]}.txt', encoding='utf8', delimiter=';',
                              lineterminator='\n').iloc[:, 0]
    data_score = pd.read_csv(f'score/score_{link.split("/")[-1]}.txt', encoding='utf8', delimiter=';',
                             lineterminator='\n').iloc[:, 0]

    # file name
    file_name = f'./data/{names.iloc[i]}_{kind.split(">")[-1].strip().replace("/","")}_{link.split("/")[-1]}.csv'
    print(file_name)
    file_name_dir = Path('./data')
    file_name_dir.mkdir(parents=True, exist_ok=True)

    data = pd.DataFrame({'review': data_review, 'score': data_score}).replace(r'', np.NaN)
    data.to_csv(file_name, mode='w', header=False)



