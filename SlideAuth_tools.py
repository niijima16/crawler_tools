from playwright.sync_api import sync_playwright
import cv2
from urllib import request


# Slide距離をもらう
def get_distance(background, gap):
    # バッググラウンドイメージを取得
    background = cv2.imread(background, 0)
    # 穴埋めイメージを取得
    gap = cv2.imread(gap, 0)
    res = cv2.matchTemplate(background, gap, cv2.TM_CCOEFF_NORMED)
    # valueの値は移動距離のドット数を表すもの
    value = cv2.minMaxLoc(res)[2][0]

    # Don't touch・固定単位換算
    return value * 278 / 360


# 人間の動きを模倣する計算
def get_track(distance):  # distanceトータル距離
    # 移動の軌跡を小分けしてリストにまとめる
    track = []
    # 現在位置
    current = 0
    # 減速関数
    mid = distance * 4 / 5
    # 間隔の生産
    t = 0.2
    # 初速度
    v = 1
    while current < distance:
        if current < mid:
            # 加速度・2
            a = 4
        else:
            # 加速度・-2
            a = -3
        v0 = v
        # 現在速度
        v = v0 + a * t
        # 移動距離
        move = v0 * t + 1 / 2 * a * t * t
        # 現在位置
        current += move
        # 軌跡を追加
        track.append(round(move))
    return track


with sync_playwright() as p:
    bro = p.chromium.launch(headless=False)
    page = bro.new_page()
    # スライドターゲットのURL
    page.goto('https://passport.jd.com/new/login.aspx?')

    # ID&PWD入力
    page.locator('//*[@id="loginname"]').fill('abc@exemle.com')
    page.wait_for_timeout(1000)
    page.locator('//*[@id="nloginpwd"]').fill('abc@exemle.com')
    page.wait_for_timeout(1000)
    page.locator('//*[@id="loginsubmit"]').click()

    page.wait_for_timeout(2000)

    # スライド認証のイメージを取得
    bg_img_src = page.locator('.JDJRV-bigimg > img').get_attribute('src')
    small_img_src = page.locator('.JDJRV-smallimg > img').get_attribute('src')

    # イメージの保存
    request.urlretrieve(bg_img_src, "background.png")
    request.urlretrieve(small_img_src, "gap.png")

    # イメージを分析して距離を取得
    distance = int(get_distance("background.png", "gap.png"))

    # web側のスライドをキャッチ
    slide = page.locator('//*[@id="JDJRV-wrap-loginsubmit"]/div/div/div/div[2]/div[3]') # 必要に応じて変更
    # パズルの位置を検索（辞書の4桁数字を返す）
    # {'x': 858, 'y': 339.9921875, 'width': 55, 'height': 55}
    box = slide.bounding_box()

    # マウスの動きを模倣
    page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    # マウスのクリックを模倣
    page.mouse.down()
    # パズルのｘの座標を確定
    x = box["x"] + 12  # 誤差を設定
    # パズル距離の小分け
    tracks = get_track(distance)  # [1,5,8,9]
    for track in tracks:
        # マウス動き模倣の循環
        page.mouse.move(x + track, 0)
        x += track
    # マウス動きを止める
    page.mouse.up()

    page.wait_for_timeout(5000)
    page.close()
    bro.close()
