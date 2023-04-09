from bs4 import BeautifulSoup
import requests


def translate(input_data):
    url = "https://translate.kakao.com/translator/translate.json"
    
    data = {
            "queryLanguage": "auto",
            "resultLanguage": "kr",
            "q": input_data
            }
    
    headers={
            "Referer": "https://translate.kakao.com/",
            "User-Agent": "Mozilla/5.0"
            }
    
    resp = requests.post(url, data=data, headers=headers)
    data = resp.json()  # {}모양의 json text를 딕셔너리로 변환해줌

    result = ''
    if len(data['result']['output']) > 1:
        for i in data['result']['output']:
            result = result + ''.join(i[0]) + ' '
    else:
        for i in data['result']['output'][0]:
            result += i + ' '
    return result

for i in range(1):
    print(i, translate('''TV에서 자주나오는 장소 특히 무한도전
서울의 중심이고 코시국때문인지 사람이 없음
해결해줬으면 함
'''))
    print(i, translate('this is the korea'))