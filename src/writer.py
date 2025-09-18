import re
import time
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

def update_chouseisan_attendance(event_url: str, name: str, comment: str, attendances: dict[int, str]) -> bool:
    """
    requestsを使用して、既存の調整さんイベントに出欠を登録・更新します。
    """
    try:
        print(f"イベントページにアクセス中: {event_url}")
        response = requests.get(event_url)
        response.raise_for_status()
        html_content = response.text

        # デバッグ用にHTMLコンテンツを出力
        # print(html_content)

        # CSRFトークンを抽出 (正規表現を修正)
        csrf_match = re.search(r'name="_token" value="(.*?)"', html_content)
        if not csrf_match:
            # 別のパターンも試す (Vueコンポーネントの属性など)
            csrf_match = re.search(r':csrf="(.*?)"' , html_content)
        
        if not csrf_match:
            print("エラー: CSRFトークンが見つかりませんでした。")
            return False
        csrf_token = csrf_match.group(1)
        print(f"CSRFトークンを取得しました: {csrf_token}")

        # 日程情報を抽出
        soup = BeautifulSoup(html_content, 'html.parser')
        script_tag = soup.find('script', string=re.compile(r'window.Chouseisan'))
        if not script_tag:
            raise ValueError("イベントデータが見つかりませんでした。")
        json_match = re.search(r'"choices"
    :
    (\[.*?\])', script_tag.string)
        if not json_match:
            raise ValueError("日程情報(choices)が見つかりませんでした。")
        import json
        choices = json.loads(json_match.group(1))

        # 送信先URLを修正
        action_url = "https://chouseisan.com/schedule/List/addRes"
        event_hash = event_url.split('h=')[-1]
        
        attendance_map = {'○': '1', '△': '2', '×': '3'}
        form_data = {
            '_token': csrf_token,
            'h': event_hash,
            'id': '',
            'name': name,
            'comment': comment,
        }
        for choice in choices:
            choice_num = choice['num']
            status_char = attendances.get(choice_num, '×')
            form_data[f'kouho[{choice_num}]'] = attendance_map.get(status_char, '3')

        print(f"送信データ: {form_data}")
        print(f"出欠情報をPOSTしています: {action_url}")
        post_response = requests.post(action_url, data=form_data, headers={'Referer': event_url}, allow_redirects=True)
        post_response.raise_for_status()

        # レスポンスURLや内容で成功を判断
        if name in post_response.text and event_hash in post_response.url:
            print(f"出欠の登録に成功しました: {name}")
            return True
        else:
            print("エラー: 出欠の登録に失敗しました。")
            return False

    except Exception as e:
        print(f"出欠の登録中にエラーが発生しました: {e}")
        return False

def main():
    event_url = "https://chouseisan.com/s?h=2cce651578f3462aab8ff7a256e4c4a9"
    print("\n--- 出欠登録テスト --- ")
    update_chouseisan_attendance(
        event_url=event_url,
        name="Gemini Agent (requests)",
        comment="requests経由で再挑戦",
        attendances={
            1: '○', 
            2: '○', 
            3: '△'  
        }
    )

if __name__ == '__main__':
    main()