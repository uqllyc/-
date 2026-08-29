import asyncio
import random
from playwright.async_api import async_playwright

# --- 投稿・レターメッセージリスト ---
POST_MESSAGES = [
    "ひま〜誰か話さへん？",
    "今日もお疲れ様！何してる？",
    "誰でも通話歓迎〜！",
    "雑談しよ！気軽にレターしてね"
]

LETTER_MESSAGES = [
    "はじめまして！仲良くしてください！",
    "投稿見かけて気になったのでレターしました！",
    "ひまだったら話しませんか〜？"
]

async def human_delay(min_sec=1.0, max_sec=3.0):
    """高速動作用の短いランダム待機"""
    delay = random.uniform(min_sec, max_sec)
    await asyncio.sleep(delay)

async def do_post(page):
    """投稿処理"""
    try:
        post_text = random.choice(POST_MESSAGES)
        print(f"📝 投稿実行: {post_text}")
        # Web版Yay!の投稿操作（必要に応じてセレクター調整）
        await page.goto("https://yay.space/")
        await human_delay(2, 4)
    except Exception as e:
        print("⚠️ 投稿エラー:", e)

async def do_like_and_follow_and_letter(page):
    """タイムラインから『いいね』『フォロー』『レター』を高頻度で実行"""
    try:
        print("🔍 タイムラインを巡回中...")
        await page.goto("https://yay.space/")
        await human_delay(2, 4)

        # いいねボタンの検索と高頻度クリック
        like_buttons = await page.query_selector_all('button[aria-label*="いいね"], button[aria-label*="Like"]')
        print(f"👀 見つかった投稿: {len(like_buttons)}件")

        for btn in like_buttons[:8]:  # 1回の巡回で最大8件いいね
            try:
                await btn.scroll_into_view_if_needed()
                await human_delay(1, 2)
                await btn.click()
                print("❤️ いいね完了")
            except:
                pass

        # フォロー & レター（ユーザー一覧や投稿元から順次処理）
        user_elements = await page.query_selector_all('a[href*="/user/"]')
        for user_elem in user_elements[:3]:  # 1回の巡回で最大3人にアプローチ
            try:
                user_url = await user_elem.get_attribute('href')
                if user_url:
                    print(f"👤 ユーザーにアクセス: {user_url}")

                    # フォロー実行
                    follow_btn = await page.query_selector('button:has-text("フォロー")')
                    if follow_btn:
                        await follow_btn.click()
                        print("➕ フォロー完了！")
                        await human_delay(1, 3)

                    # レター送信
                    letter_btn = await page.query_selector('button:has-text("レター")')
                    if letter_btn:
                        await letter_btn.click()
                        await human_delay(1, 2)
                        letter_text = random.choice(LETTER_MESSAGES)
                        # テキストエリアに入力して送信
                        textarea = await page.query_selector('textarea')
                        if textarea:
                            await textarea.fill(letter_text)
                            send_btn = await page.query_selector('button:has-text("送信")')
                            if send_btn:
                                await send_btn.click()
                                print(f"✉️ レター送信完了: {letter_text}")
                                await human_delay(2, 4)
            except Exception as e:
                print("⚠️ アクション失敗:", e)

    except Exception as e:
        print("⚠️ 巡回エラー:", e)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox", "--single-process"]
        )
        
        try:
            context = await browser.new_context(storage_state="state.json")
            print("✅ state.json 読み込み完了")
        except Exception as e:
            print("❌ state.json がありません:", e)
            await browser.close()
            return

        page = await context.new_page()

        step = 0
        while True:
            step += 1
            print(f"\n--- ⚡ 高速ループ実行中 [{step}回目] ---")

            # 巡回（いいね・フォロー・レター）
            await do_like_and_follow_and_letter(page)

            # 3回に1回のペースで自動投稿
            if step % 3 == 0:
                await do_post(page)

            # 【高頻度設定】次の巡回までわずか 3分〜5分 だけ待機
            wait_time = random.uniform(180, 300)
            print(f"⏳ 次の高速巡回まで {int(wait_time)} 秒（約{int(wait_time/60)}分）待機...")
            await asyncio.sleep(wait_time)

if __name__ == "__main__":
    asyncio.run(main())
