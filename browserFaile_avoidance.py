from playwright.sync_api import sync_playwright


'''

# 第一歩はchromeファイルの元に移動  「8899」はカスタマイズしたローカルポート
./Google Chrome --remote-debugging-port=8899 --incognito --start-maximized --user-data-dir="カスタマイズしたディレクトリのパス"

'''


with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://localhost:8899/') # ローカルポート番号と一致する
    page = browser.contexts[0].pages[0]

    # chrome管理権を譲る
    page.locator('//*[@id="kw"]').fill('haha')
    print(page.url)
    print(page.title())
