import asyncio
import random
from datetime import datetime
from playwright.async_api import async_playwright

POST_MESSAGES = [
    "ひま〜誰か話さへん？",
    "今日もお疲れ様！みんな何してる？",
    "誰でも通話歓迎〜！",
    "雑談しよ！気軽にレターしてね"
]

async def human_delay(min_sec=3.0, max_sec=8.0):
    delay = random.uniform(min_sec, max_sec)
    print(f"⏱️ 待機中... ({delay:.1f}秒)")
    await asyncio.sleep(delay)

async def main():
    async with async_playwright() as p:
        # 無料枠のメモリ溢れ（クラッシュ）を防ぐ設定
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--single-process"
            ]
        )
        
        try:
            context = await browser.new_context(storage_state="state.json")
            print("✅ state.json の読み込み成功")
        except Exception as e:
            print("❌ state.json が見つかりません:", e)
            await browser.close()
            return

        page = await context.new_page()

        while True:
            print("🚀 Yay! へアクセス中...")
            await page.goto("https://yay.space/")
            await human_delay(5, 10)

            post_text = random.choice(POST_MESSAGES)
            print(f"📝 投稿予定: {post_text}")

            # 投稿処理の待機（15分〜30分のランダム）
            wait_time = random.uniform(900, 1800)
            print(f"⏳ 次の処理まで {int(wait_time/60)} 分待機...")
            await asyncio.sleep(wait_time)

if __name__ == "__main__":
    asyncio.run(main())
