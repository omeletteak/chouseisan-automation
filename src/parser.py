import json
import re
from bs4 import BeautifulSoup
from src.models import Event, Schedule, Participant, Attendance

def parse_chouseisan_html(html_content: str) -> Event:
    """
    調整さんのHTMLコンテンツを解析し、埋め込まれたJSONデータからEventオブジェクトを返します。
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # window.Chouseisan オブジェクトを含む script タグを検索
    script_tag = soup.find('script', string=re.compile(r'window\.Chouseisan\s*=\s*'))
    if not script_tag:
        raise ValueError("HTML内に調整さんのイベントデータが見つかりませんでした。")

    # scriptタグのテキストからJSON部分を抽出
    script_content = script_tag.string
    json_match = re.search(r'window\.Chouseisan\s*=\s*({.*?});', script_content, re.DOTALL)
    if not json_match:
        raise ValueError("イベントデータのJSON形式の抽出に失敗しました。")
    
    json_str = json_match.group(1)

    # JavaScriptオブジェクトリテラルを厳密なJSON形式に変換
    # 1. キーをダブルクォートで囲む (例: { key: val } -> { "key": val })
    json_str = re.sub(r'([{\s,])([a-zA-Z0-9_]+):_([^{"\s])', r'\1"\2":\3', json_str)
    # 2. 末尾のカンマを削除 (例: { "key": val, } -> { "key": val })
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        # デバッグ用にエラーと問題の文字列を表示
        print(f"JSONパースエラー: {e}")
        print("問題のJSON文字列:", json_str)
        raise

    event_data = data.get('event', {})

    # イベント情報の抽出
    event_title = event_data.get('name', 'タイトル不明')
    event_description = event_data.get('detail', '説明なし') or '説明なし'

    # 日程の抽出
    schedules_data = event_data.get('choices', [])
    schedules = [Schedule(datetime=s['choice']) for s in schedules_data]

    # 参加者と出欠の抽出
    participants_data = event_data.get('members', [])
    participants = []
    
    # 出欠ステータスのマッピング (JSONの値 -> Enum)
    attendance_map = {
        '1': Attendance.ATTENDING, # ○
        '2': Attendance.MAYBE,     # △
        '3': Attendance.ABSENT,    # ×
    }

    for p_data in participants_data:
        participant = Participant(
            name=p_data.get('name', '名無し'),
            comment=p_data.get('comment', '') or ''
        )
        
        attend_str_list = p_data.get('attend', '').split(',')
        
        for i, attend_status_key in enumerate(attend_str_list):
            if i < len(schedules):
                schedule = schedules[i]
                attendance_enum = attendance_map.get(attend_status_key, Attendance.UNKNOWN)
                participant.attendances[schedule] = attendance_enum
        
        participants.append(participant)

    return Event(
        title=event_title,
        description=event_description,
        schedules=schedules,
        participants=participants
    )

if __name__ == '__main__':
    print("このパーサーはHTML埋め込みのJSONデータを解析します。テスト実行には main.py を使用してください。")
