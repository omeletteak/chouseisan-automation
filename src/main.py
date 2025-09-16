from src.parser import parse_chouseisan_html
from src.models import Event
from src.database import init_db, save_event
from src.reader import get_html_content

def print_event_details(event: Event):
    """Eventオブジェクトの内容を分かりやすく表示する"""
    print("--- Event ---")
    print(f"Title: {event.title}")
    print(f"Description: {event.description}")
    
    print("\n--- Schedules ---")
    for schedule in event.schedules:
        print(schedule.datetime)
    
    print("\n--- Participants ---")
    for participant in event.participants:
        print(f"Name: {participant.name}")
        print(f"  Comment: {participant.comment}")
        for schedule, attendance in participant.attendances.items():
            print(f"    - {schedule.datetime}: {attendance.value}")
        print("-" * 10)

def main():
    """
    データベースを初期化し、指定されたURLからHTMLを取得して解析し、
    結果を表示してからデータベースに保存するメイン関数。
    """
    # 対象のURL
    target_url = "https://chouseisan.com/s?h=aa76f52234794d2889004a5ce6ba2153"

    # 1. データベースの初期化
    init_db()

    # 2. URLからHTMLコンテンツを取得
    print(f"\nURLからHTMLコンテンツを取得中: {target_url}")
    html_content = get_html_content(target_url)

    # 3. HTMLの解析と結果表示
    if html_content:
        print("HTMLコンテンツの取得に成功しました。解析を開始します。")
        parsed_event = parse_chouseisan_html(html_content)
        
        print("\n--- 解析結果 ---")
        print_event_details(parsed_event)
        
        # 4. データベースへの保存
        # 注意: 同じイベントを何度も実行すると、同じ内容がデータベースに重複して保存されます。
        print("\n--- データベースへの保存 ---")
        save_event(parsed_event)
    else:
        print("HTMLコンテンツの取得に失敗したため、解析をスキップします。")

if __name__ == '__main__':
    main()