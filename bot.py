import os
import aiohttp
from aiohttp import web
import asyncio
import yt_dlp
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto,
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery,
    LabeledPrice, PreCheckoutQuery, BufferedInputFile
)
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
log = logging.getLogger("tiktok-bot")

TIKTOK_TOKEN = "8695837050:AAGtGtmr8kCUfE1N1DMnsa89lHBG1y7BRBI"
CHANNELS = ["@azkar201", "@Sermon10"]

bot = Bot(TIKTOK_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌟 إرسال هدية (نجوم) 🌟")],
        [KeyboardButton(text="ℹ️ نبذة عن البوت"), KeyboardButton(text="📞 تواصل مع المطور")],
    ],
    resize_keyboard=True,
    input_field_placeholder="أرسل رابط تيك توك للتحميل",
)

STARS_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⭐️ 10 نجوم", callback_data="gift_stars_10")],
        [InlineKeyboardButton(text="🌟 50 نجمة", callback_data="gift_stars_50")],
        [InlineKeyboardButton(text="🚀 100 نجمة", callback_data="gift_stars_100")],
        [InlineKeyboardButton(text="👑 500 نجمة", callback_data="gift_stars_500")],
    ]
)

def get_subscription_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 قناة azkar201", url="https://t.me/azkar201")],
            [InlineKeyboardButton(text="🚀 قناة Sermon10", url="https://t.me/Sermon10")],
            [InlineKeyboardButton(text="✅ تحقق من الاشتراك", callback_data="check_sub")]
        ]
    )

async def is_subscribed(user_id: int) -> bool:
    try:
        for channel in CHANNELS:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in ("member", "administrator", "creator"):
                return False
        return True
    except Exception as e:
        log.error(f"Error checking subscription: {e}")
        return False

def get_welcome_text():
    return (
        "أهلاً بك في بوت تحميل تيك توك 🚀\n\n"
        "🤖 <b>مميزات البوت:</b>\n"
        "• تحميل المقاطع والصور بدون علامة مائية.\n"
        "• جلب الوصف (الكابشن) الأصلي للفيديو.\n"
        "• سرعة فائقة في التحميل (مدعوم بـ 3 سيرفرات).\n\n"
        "🔗 <b>أرسل أي رابط تيك توك الآن للبدء!</b>"
    )

@dp.message(Command("start"))
async def start_cmd(message: Message):
    if not message.from_user:
        return
    if not await is_subscribed(message.from_user.id):
        sub_text = "❌ <b>عذراً عزيزي!</b>\nلا يمكنك استخدام البوت إلا بعد الاشتراك في قنواتنا. يرجى الاشتراك من الأزرار بالأسفل ثم الضغط على 'تحقق من الاشتراك'."
        await message.answer(sub_text, reply_markup=get_subscription_keyboard())
        return
    
    await message.answer(get_welcome_text(), reply_markup=MAIN_MENU)

@dp.callback_query(F.data == "check_sub")
async def check_subscription_callback(callback: CallbackQuery):
    if await is_subscribed(callback.from_user.id):
        await callback.message.delete()
        await callback.message.answer("✅ <b>تم التحقق بنجاح! شكراً لاشتراكك.</b>")
        await callback.message.answer(get_welcome_text(), reply_markup=MAIN_MENU)
    else:
        await callback.answer("❌ لم تقم بالاشتراك في جميع القنوات، اشترك ثم حاول مجدداً!", show_alert=True)

@dp.message(F.text == "ℹ️ نبذة عن البوت")
async def show_about(message: Message):
    about_text = (
        "ماذا يمكن لهذا البوت فعله؟\n"
        "• تحميل مقاطع وصور تيك توك بجودة عالية.\n"
        "• التحميل بدون علامة مائية نهائياً.\n"
        "• جلب الوصف (الكابشن) الأصلي المرفق مع المقطع.\n"
        "• سرعة فائقة في التحميل وإرسال الفيديو."
    )
    await message.answer(about_text)

@dp.message(F.text == "📞 تواصل مع المطور")
async def contact_developer(message: Message):
    dev_text = (
        "👨‍💻 <b>للتواصل مع مطور البوت:</b>\n\n"
        "لأي استفسارات، اقتراحات، أو الإبلاغ عن مشكلة، يمكنك مراسلتي عبر المعرف التالي:\n"
        "👉 @no3zzz" 
    )
    await message.answer(dev_text)

@dp.message(F.text == "🌟 إرسال هدية (نجوم) 🌟")
async def show_stars_options(message: Message):
    await message.answer("اختر عدد النجوم التي ترغب بإهدائها لدعم البوت والمطور 🎁:", reply_markup=STARS_KEYBOARD)

@dp.callback_query(F.data.startswith("gift_stars_"))
async def process_gift_stars(callback: CallbackQuery):
    stars_amount = int(callback.data.split("_")[-1])
    prices = [LabeledPrice(label=f"هدية {stars_amount} نجمة", amount=stars_amount)]
    
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=f"إرسال {stars_amount} نجمة 🌟",
        description=f"دعم البوت والمطور بـ {stars_amount} من نجوم تيليجرام!",
        payload=f"tiktok_gift_{stars_amount}_stars",
        currency="XTR",
        prices=prices,
    )
    await callback.answer()

@dp.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    await message.answer("❤️ شكراً جزيلاً لك على دعمك وهديتك القيمة!")

# محرك احتياطي باستخدام yt-dlp في حال حظر السيرفر
def download_with_ytdlp(url: str, filename: str):
    ydl_opts = {
        'outtmpl': filename,
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return info.get('description') or info.get('title') or "تحميل ناجح 🚀"

@dp.message(F.text)
async def download_tiktok(message: Message):
    if not await is_subscribed(message.from_user.id):
        sub_text = "❌ <b>عذراً!</b> لا يمكنك التحميل قبل الاشتراك في القنوات:"
        await message.answer(sub_text, reply_markup=get_subscription_keyboard())
        return

    url = (message.text or "").strip()
    if url.startswith("/"):
        return
    if "tiktok.com" not in url.lower():
        await message.answer("⚠️ يرجى إرسال رابط تيك توك صحيح.", reply_markup=MAIN_MENU)
        return

    status = await message.answer("⏳ جارٍ التحميل...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    # المحاولة الأولى: عبر TikWM API
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post("https://www.tikwm.com/api/", data={"url": url, "hd": 1}, timeout=20) as resp:
                data = await resp.json(content_type=None)

            if data and data.get("code") == 0 and data.get("data"):
                item = data["data"]
                title = item.get("title") or "تحميل ناجح 🚀"
                images = item.get("images", [])
                video_url = item.get("play") or item.get("wmplay") or ""
                music_url = item.get("music") or ""

                if video_url.startswith("/"):
                    video_url = f"https://www.tikwm.com{video_url}"
                if music_url.startswith("/"):
                    music_url = f"https://www.tikwm.com{music_url}"

                if images:
                    await status.edit_text("📸 جارٍ إرسال الصور...")
                    media_group = [
                        InputMediaPhoto(media=img, caption=title[:1024] if i == 0 else None, parse_mode=None)
                        for i, img in enumerate(images[:10])
                    ]
                    await message.answer_media_group(media_group)
                    if music_url:
                        async with session.get(music_url, timeout=30) as m_resp:
                            if m_resp.status == 200:
                                audio_bytes = await m_resp.read()
                                await message.answer_audio(
                                    audio=BufferedInputFile(audio_bytes, filename="audio.mp3"),
                                    caption="🎵 الصوت المصاحب للصور"
                                )
                    await status.delete()
                    return

                elif video_url:
                    await status.edit_text("🎥 جارٍ رفع الفيديو...")
                    async with session.get(video_url, timeout=45) as v_resp:
                        if v_resp.status == 200:
                            video_bytes = await v_resp.read()
                            await message.answer_video(
                                video=BufferedInputFile(video_bytes, filename="tiktok.mp4"),
                                caption=title[:1024],
                                parse_mode=None,
                                supports_streaming=True
                            )
                            await status.delete()
                            return
    except Exception as e:
        log.warning(f"TikWM failed, trying fallback: {e}")

    # المحاولة الثانية (الاحتياطية): عبر yt-dlp مباشرة من السيرفر
    temp_file = f"video_{message.from_user.id}_{message.message_id}.mp4"
    try:
        await status.edit_text("⚡ جارٍ التحميل عبر السيرفر البديل...")
        title = await asyncio.to_thread(download_with_ytdlp, url, temp_file)
        if os.path.exists(temp_file):
            with open(temp_file, "rb") as f:
                video_bytes = f.read()
            await message.answer_video(
                video=BufferedInputFile(video_bytes, filename="tiktok.mp4"),
                caption=title[:1024],
                parse_mode=None,
                supports_streaming=True
            )
            await status.delete()
            return
    except Exception as e2:
        log.error(f"Fallback yt-dlp error: {e2}")
        await status.edit_text(f"⚠️ تعذّر التحميل. سبب الخطأ التقني:\n<code>{e2}</code>")
    finally:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass

# --- جزء السيرفر الوهمي لإرضاء منصة Render ---
async def handle_ping(request):
    return web.Response(text="Bot is running 24/7!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    log.info(f"🌐 Web server started on port {port}")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print("🚀 البوت شغال الآن!")
    await asyncio.gather(
        start_web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())
