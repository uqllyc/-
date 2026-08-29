import asyncio
import random
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from playwright.async_api import async_playwright

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
    delay = random.uniform(min_sec, max_sec)
    await asyncio.sleep(delay)

async def safe_goto(page, url):
    try:
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await human_delay(2, 4)
    except Exception as e:
        print(f"⚠️ ページ遷移警告: {e}")

async def do_post(page):
    try:
        post_text = random.choice(POST_MESSAGES)
        print(f"📝 投稿実行試行: {post_text}")
        await safe_goto(page, "https://yay.space/")
    except Exception as e:
        print("⚠️ 投稿エラー:", e)

async def do_like_and_follow_and_letter(page):
    try:
        print("🔍 タイムラインを巡回中...")
        await safe_goto(page, "https://yay.space/")

        # ページのレンダリング待ちとスクロール（動的読み込み用）
        await asyncio.sleep(3)
        await page.mouse.wheel(0, 500)
        await asyncio.sleep(2)

        # 広範囲の判定でボタン・クリック可能要素を取得
        # 1. buttonタグ全般 2. svgを含む要素 3. 特定のクラスや属性を持つ要素
        all_buttons = await page.query_selector_all('button, div[role="button"], a[role="button"]')
        print(f"👀 見つかったボタン・操作要素数: {len(all_buttons)}件")

        # いいねボタン候補を抽出してクリック
        like_count = 0
        for btn in all_buttons:
            try:
                # 非表示のものはスキップ
                if not await btn.is_visible():
                    continue

                # ボタンのHTMLやテキストを取得して判定
                aria = await btn.get_attribute("aria-label") or ""
                text = await btn.inner_text() or ""
                html = await btn.inner_html() or ""

                # いいね/リアクション系の要素か、もしくはタイムライン上のアクションボタンかを判定
                is_like_target = (
                    "いいね" in aria or "Like" in aria or
                    "いいね" in text or "Like" in text or
                    "<svg" in html.lower()
                )

                if is_like_target:
                    await btn.scroll_into_view_if_needed()
                    await human_delay(1, 2)
                    await btn.click()
                    like_count += 1
                    print(f"❤️ [{like_count}] アクション実行完了")

                    if like_count >= 8:
                        break
            except Exception:
                pass

        # ユーザーリンクの取得とフォロー・レター処理
        user_elements = await page.query_selector_all('a[href*="/user/"]')
        found_users = []
        for elem in user_elements:
            href = await elem.get_attribute('href')
            if href and href not in found_users and href != "/user/":
                found_users.append(href)

        print(f"👤 見つかったユーザー数: {len(found_users)}人")

        for user_path in found_users[:3]:
            try:
                full_url = user_path if user_path.startswith("http") else f"https://yay.space{user_path}"
                print(f"👤 ユーザーページへ移動: {full_url}")
                await safe_goto(page, full_url)

                # フォロー処理
                follow_btn = await page.query_selector('button:has-text("フォロー"), button:has-text("Follow")')
                if follow_btn and await follow_btn.is_visible():
                    await follow_btn.click()
                    print("➕ フォロー完了！")
                    await human_delay(1, 2)

                # レター処理
                letter_btn = await page.query_selector('button:has-text("レター"), button:has-text("Letter")')
                if letter_btn and await letter_btn.is_visible():
                    await letter_btn.click()
                    await human_delay(1, 2)

                    textarea = await page.query_selector('textarea')
                    if textarea and await textarea.is_visible():
                        letter_text = random.choice(LETTER_MESSAGES)
                        await textarea.fill(letter_text)

                        send_btn = await page.query_selector('button:has-text("送信"), button:has-text("Send")')
                        if send_btn and await send_btn.is_visible():
                            await send_btn.click()
                            print(f"✉️ レター送信完了: {letter_text}")
                            await human_delay(2, 3)
            except Exception as e:
                print("⚠️ ユーザー操作エラー:", e)

    except Exception as e:
        print("⚠️ 巡回エラー:", e)

async def bot_loop():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--single-process",
                "--disable-setuid-sandbox",
                "--no-zygote"
            ]
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
            await do_like_and_follow_and_letter(page)

            if step % 3 == 0:
                await do_post(page)

            wait_time = random.uniform(180, 300)
            print(f"⏳ 次の高速巡回まで {int(wait_time)} 秒待機...")
            await asyncio.sleep(wait_time)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.task = asyncio.create_task(bot_loop())
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"status": "ok", "bot": "running"}
