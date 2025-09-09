from bs4 import BeautifulSoup

def parse_chouseisan_html(html_content: str) -> dict:
    """
    調整さんのHTMLコンテンツを解析し、必要な情報を抽出します。
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    event_info = {}
    
    # イベントタイトルを抽出
    event_title_tag = soup.find('h1', class_='event-title')
    if event_title_tag:
        event_info['title'] = event_title_tag.get_text(strip=True)
    else:
        event_info['title'] = 'タイトル不明'
        
    # イベント説明を抽出
    event_description_tag = soup.find('p', class_='event-description')
    if event_description_tag:
        event_info['description'] = event_description_tag.get_text(strip=True)
    else:
        event_info['description'] = '説明なし'

    # 日程を抽出
    dates = []
    # <thead>内の<th>タグで、user-nameクラスを持たないものを日程と仮定
    date_headers = soup.select('#tbl-sch thead th:not(.user-name)')
    for header in date_headers:
        date_text = header.get_text(strip=True)
        if date_text and date_text != '名前' and date_text != 'コメント': # 名前とコメントの列を除外
            dates.append(date_text)
    event_info['dates'] = dates

    # 参加者と出欠状況、コメントを抽出
    participants = []
    user_rows = soup.select('#tbl-sch tbody tr.user-row')
    for row in user_rows:
        participant = {}
        participant['name'] = row.find('td', class_='user-name').get_text(strip=True) if row.find('td', class_='user-name') else '名無し'
        
        # 各日程の出欠状況
        attendances = []
        # user-nameとuser-commentクラスを持たない<td>タグが出欠状況
        sch_cells = row.select('td:not(.user-name):not(.user-comment)')
        for cell in sch_cells:
            attendances.append(cell.get_text(strip=True))
        participant['attendances'] = attendances

        participant['comment'] = row.find('td', class_='user-comment').get_text(strip=True) if row.find('td', class_='user-comment') else ''
        participants.append(participant)
    event_info['participants'] = participants
    
    return event_info

if __name__ == '__main__':
    # data/sample.html の内容を読み込んでテスト
    try:
        with open('../data/sample.html', 'r', encoding='utf-8') as f:
            sample_html_content = f.read()
        
        parsed_data = parse_chouseisan_html(sample_html_content)
        print(parsed_data)
    except FileNotFoundError:
        print("Error: ../data/sample.html not found. Please create it with sample HTML content.")