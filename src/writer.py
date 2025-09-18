import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def register_attendance_semi_auto(event_url: str, name: str, comment: str, attendances: dict[int, str]):
    """
    Seleniumを使用して、ユーザーの操作を補助する形で出欠を登録します。
    ブラウザが起動し、フォームが自動入力された後、ユーザーが手動で送信します。
    """
    driver = None
    try:
        options = uc.ChromeOptions()
        print("ブラウザを起動しています...")
        driver = uc.Chrome(options=options)
        wait = WebDriverWait(driver, 10)
        
        print(f"イベントページにアクセス中: {event_url}")
        driver.get(event_url)
        time.sleep(2) # ページ描画を待つ

        # 1. 初期状態のスクリーンショットを撮り、オーバーレイを確認
        initial_screenshot_path = "debug_screenshot_initial.png"
        driver.save_screenshot(initial_screenshot_path)
        print(f"初期スクリーンショットを保存しました: {initial_screenshot_path}")

        # 2. Cookieバナーなどがあれば閉じる試み (失敗しても続行)
        try:
            # Cookieバナーでよく使われるボタンのテキストやID/クラスで探す
            cookie_button = driver.find_element(By.XPATH, "//button[contains(text(),'同意') or contains(text(),'OK') or contains(text(),'Accept')]")
            print("Cookie同意ボタンらしきものが見つかりました。クリックします。")
            cookie_button.click()
            time.sleep(1) # クリック後の描画を待つ
        except Exception as e:
            print(f"Cookie同意ボタンは見つかりませんでした: {e}")

        # 3. 「出欠を入力する」ボタンをクリック
        print("「出欠を入力する」ボタンをクリックします...")
        add_button = wait.until(EC.element_to_be_clickable((By.ID, "add_btn")))
        add_button.click()

        # 4. クリック後の状態で再度デバッグ情報を取得
        print("フォームが表示されるのを待っています...")
        time.sleep(3)
        
        after_click_screenshot_path = "debug_screenshot_after_click.png"
        driver.save_screenshot(after_click_screenshot_path)
        print(f"クリック後のスクリーンショットを保存しました: {after_click_screenshot_path}")

        print("\n--- ボタンクリック後のページソース ---")
        print(driver.page_source)
        print("--- ページソース終わり---\n")

        # 5. フォーム入力処理
        print("フォームに入力しています...")
        name_input = wait.until(EC.presence_of_element_located((By.NAME, "name")))
        name_input.clear()
        name_input.send_keys(name)

        comment_input = driver.find_element(By.NAME, "comment")
        comment_input.clear()
        comment_input.send_keys(comment)

        attendance_map = {'○': '1', '△': '2', '×': '3'}
        for choice_num, status in attendances.items():
            status_value = attendance_map.get(status)
            if status_value:
                radio_button_selector = f"input[name='kouho[{choice_num}]'][value='{status_value}']"
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, radio_button_selector))).click()

        print("\nフォームへの自動入力を完了しました。")
        input("ブラウザで内容を確認し、問題がなければ「入力する」ボタンを押してください。\n操作が完了したら、このコンソールでEnterキーを押すとブラウザが閉じます。")

    except Exception as e:
        print(f"処理中にエラーが発生しました: {e}")
    finally:
        if driver:
            print("ブラウザを終了します。")
            driver.quit()

def main():
    event_url = "https://chouseisan.com/s?h=2cce651578f3462aab8ff7a256e4c4a9"
    print("\n--- 半自動出欠登録テスト (最終デバッグ) ---")
    register_attendance_semi_auto(
        event_url=event_url,
        name="Gemini Agent (Debug)",
        comment="最終デバッグ実行",
        attendances={
            1: '○', 
            2: '△', 
            3: '×'
        }
    )

if __name__ == '__main__':
    main()
