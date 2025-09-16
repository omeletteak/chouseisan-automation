import requests

def get_html_content(url: str) -> str:
    """
    指定されたURLからHTMLコンテンツを取得します。
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTPエラーが発生した場合に例外を発生させる
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"HTMLコンテンツの取得中にエラーが発生しました: {e}")
        return ""

if __name__ == '__main__':
    # テスト用のURL (調整さんのサンプルイベントURLなど)
    # 実際の調整さんのイベントURLに置き換えてください
    test_url = "https://chouseisan.com/s?id=sxxxxxxxxxxxxxxxxxxxx" # 仮のURL
    html = get_html_content(test_url)
    if html:
        print("HTMLコンテンツを正常に取得しました。")
        # 取得したHTMLの一部を表示 (デバッグ用)
        print(html[:500])
    else:
        print("HTMLコンテンツの取得に失敗しました。")
