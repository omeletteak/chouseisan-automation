from reader import get_html_content
from parser import parse_chouseisan_html

def main():
    # 実際の調整さんのイベントURLに置き換えてください
    # 例: https://chouseisan.com/s?id=sxxxxxxxxxxxxxxxxxxxx
    chouseisan_url = "https://chouseisan.com/s?id=sxxxxxxxxxxxxxxxxxxxx" # 仮のURL

    print(f"URLからHTMLコンテンツを取得中: {chouseisan_url}")
    html_content = get_html_content(chouseisan_url)

    if html_content:
        print("HTMLコンテンツの取得に成功しました。解析を開始します。")
        parsed_data = parse_chouseisan_html(html_content)
        print("解析結果:")
        print(parsed_data)
    else:
        print("HTMLコンテンツの取得に失敗したため、解析をスキップします。")

if __name__ == '__main__':
    main()
