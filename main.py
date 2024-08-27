#!/usr/bin/python3
# -*- coding: utf-8 -*-
import mastodon # 터미널에 pip install Mastodon.py
import random # 안깔아도 됩니다
from bs4 import BeautifulSoup # 터미널에 pip install beautifulsoup4 
import gspread # pip insatll gspread

def main():
    print('###### main 시작')

    # 시트 연결에 필요한 값
    ## 사용할 시트 전체 주소 중
    ##  https://docs.google.com/spreadsheets/d/1SofGP0vYkR4mWmwEjsx-A9Tnw6enkg-WIEAMlg7z1do/edit?usp=sharing
    ## ~d/ 뒷부분 한 섹션을 사용합니다.
    SHEET_KEY = '1ig8JWYHYkyDnKfB_rzeFAqulMJJUhmedr_XsVMdj4cY' # url 중간부분

    # 스프레드 시트 연결
    gc = gspread.service_account(filename='mysheetkey.json')
    wks = gc.open_by_key(SHEET_KEY)

    # 봇으로 쓸 계정 키값 
    CLIENT_ID = 'EPVqPHWr1IQxB2FqnWg4h5moxjDGfFC9IMiSefEG2Bw' # 클라이언트 키
    CLIENT_SECRET = 'sCGahCqITNBrU1zuibIWGEfX1Ku_D3JCs1s__QCywZk' # 클라이언트 비밀 키
    ACCESS_TOKEN = 'llfVzOUWXu9iFE9StiPG6FgRVACc11qLBMCEETo1Wlc' # 액세스 토큰
    BASE = 'https://cogito.foundation' # 인스턴스(서버) 주소
    

    # 마스토돈 계정 인증!
    try:
        api = mastodon.Mastodon(
            client_id = CLIENT_ID,
            client_secret = CLIENT_SECRET,
            access_token = ACCESS_TOKEN,
            api_base_url = BASE)
        print('auth success')
    except Exception as e:
        print('auth fail')
        print(e)
    
    handler = StreamHandler(api, wks)
    api.stream_user(handler)    




class StreamHandler(mastodon.StreamListener):
    def __init__(self, api: mastodon.Mastodon, wks):
        super().__init__()
        self.api = api
        self.wks = wks
    
    # 마스토돈 툿 내용의 html 태그 제거
    # 마스토돈 api는 툿 내용을 텍스트만 주는게 아니라, html 태그까지 같이 줍니다! 따라서 html 태그 제거가 필요합니다.
    def extract_text_from_html(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        text_content = soup.get_text(separator=' ', strip=True)
        return text_content
    
    def on_notification(self, notification):
        print('###### on_notification 시작')
        if notification.type != 'mention': # 멘션만 받는다.
            return
        
        content = notification['status']['content']
        toot_text = self.extract_text_from_html(content)
        if toot_text.find('[') == -1 or  toot_text.find(']') == -1:
            return # [] 없으면 반응하지 않음
        elif toot_text.find('[') > toot_text.find(']'):
            return # [] 위치 반전이면 반응하지 안음
        
        # [] 안의 내용을 / 기준으로 나눠서 확인 및 여백 제거
        keywords = toot_text[toot_text.find('[')+1:toot_text.find(']')].split('/') 
        for i in range(len(keywords)): 
            keywords[i] = keywords[i].strip()
        
        # 키워드 체크 (76줄로 가세요)
        reply = self.check_keyword(keywords)

        if reply != '': # 답장 할 문자열이 없는게 아니라면
            # 답장(툿) 을 보낸다
            # reply: 답장 내용
            # in_reply_to_id: 답장해야할 원본 툿. 이걸 생략하면 퍼블릭이 올라갑니다.
            # visibility: 공개 범위
            ## visibility='private' 여야 자물쇠 걸린 툿을 합니다!!! 중요!!!
            ## 앞에 @아이디 를 달아야 툿 보낸 사람을 태그하여 답장합니다.
            self.api.status_post('@'+notification.status.account.acct+' '+ reply, in_reply_to_id= notification.status.id, visibility='private')



    def check_keyword(self, keywords):
        print('###### check_keyword 시작:', keywords)
        
        
        if keywords[0] == '1d100' or keywords[0] == '1D100': # 1d100
            dice100 = random.randint(1, 100)
            return str(dice100) # 숫자(int)가 아니라 문자열(str)로 답장

        elif keywords[0] == '1d32' or keywords[0] == '1D32': # 1d32
            dice32 = random.randint(1, 32)
            return str(dice32) # 숫자(int)가 아니라 문자열(str)로 답장
        
        elif keywords[0] == '1d20' or keywords[0] == '1D20': # 1d20
            dice20 = random.randint(1, 20)
            return str(dice20) # 숫자(int)가 아니라 문자열(str)로 답장
        
        elif keywords[0] == '1d3' or keywords[0] == '1D3': # 1d3
            dice3 = random.randint(1, 3)
            return str(dice3) # 숫자(int)가 아니라 문자열(str)로 답장
            
        elif keywords[0] == 'YN' or keywords[0] == 'yn': # YN
            YN = ["예", "아니오"]
            AN = random.choice(YN)
            return str(AN) # 숫자(int)가 아니라 문자열(str)로 답장
            
        elif keywords[0] == '성패': # YN
            PF = ["성공", "실패"]
            AN = random.choice(PF)
            return str(AN) # 숫자(int)가 아니라 문자열(str)로 답장        
            
        elif keywords[0] == '묵찌빠': # 묵찌빠
            RSP = ["가위", "바위", "보"]
            AN = random.choice(RSP)
            return str(AN) # 숫자(int)가 아니라 문자열(str)로 답장
        
        elif keywords[0] == '뽑기':
            worksheet = self.wks.worksheet('뽑기')
            records = worksheet.get_all_records() # 전체 데이터를 가져온다
            RR = random.randint(1, len(records))-1
            print(records) # 리스트 안에 딕셔너리
            print(records[RR]) # 딕셔너리
            randomA = records[RR]['뽑기']
            return randomA

        elif keywords[0] == '운세':
            worksheet = self.wks.worksheet('운세')
            records = worksheet.get_all_records() # 전체 데이터를 가져온다
            RR = random.randint(1, len(records))-1
            print(records) # 리스트 안에 딕셔너리
            print(records[RR]) # 딕셔너리
            randomA = records[RR]['운세']
            return randomA
        

        
        # 이후 키워드를 추가할 경우 elif를 붙여서 나열
        # 예시
        # elif keywords[0] == 'yn': ~ 
        
        else: 
            res = '' # [] 안에 사전 정의되지 않은 키워드가 들어있을 경우 반응하지 않는다.
        return res

    
    

if __name__ == '__main__':
    main()
