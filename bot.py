import os
import aiohttp
from aiohttp import web
import asyncio
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

# أزرار الاشتراك بأسماء القنوات
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
        "🤖 **مميزات البوت:**\n"
        "• تحميل المقاطع والصور بدون علامة مائية.\n"
        "• جلب الوصف (الكابشن) الأصلي للفيديو.\n"
        "• سرعة فائقة في التحميل.\n\n"
        "🔗 **أرسل أي رابط تيك توك الآن للبدء!**"
    )

@dp.message(Command("start"))
async def start_cmd(message: Message):
    if not message.from_user:
        return
    if not await is_subscribed(message.from_user.id):
        sub_text = "❌ **عذراً عزيزي!**\nلا يمكنك استخدام البوت إلا بعد الاشتراك في قنواتنا. يرجى الاشتراك من الأزرار بالأسفل ثم الضغط على 'تحقق من الاشتراك'."
        await message.answer(sub_text, reply_markup=get_subscription_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return
    
    await message.answer(get_welcome_text(), reply_markup=MAIN_MENU, parse_mode=ParseMode.MARKDOWN)

@dp.callback_query(F.data == "check_sub")
async def check_subscription_callback(callback: CallbackQuery):
    if await is_subscribed(callback.from_user.id):
        await callback.message.delete()
        await callback.message.answer("✅ **تم التحقق بنجاح! شكراً لاشتراكك.**", parse_mode=ParseMode.MARKDOWN)
        await callback.message.answer(get_welcome_text(), reply_markup=MAIN_MENU, parse_mode=ParseMode.MARKDOWN)
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
    await message.answer(about_text, parse_mode=ParseMode.MARKDOWN)

@dp.message(F.text == "📞 تواصل مع المطور")
async def contact_developer(message: Message):
    dev_text = (
        "👨‍💻 **للتواصل مع مطور البوت:**\n\n"
        "لأي استفسارات، اقتراحات، أو الإبلاغ عن مشكلة، يمكنك مراسلتي عبر المعرف التالي:\n"
        "👉 @no3zzz" 
    )
    await message.answer(dev_text, parse_mode=ParseMode.MARKDOWN)

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

@dp.message(F.text)
async def download_tiktok(message: Message):
    if not await is_subscribed(message.from_user.id):
        sub_text = "❌ **عذراً!** لا يمكنك التحميل قبل الاشتراك في القنوات:"
        await message.answer(sub_text, reply_markup=get_subscription_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return

    url = (message.text or "").strip()
    if url.startswith("/"):
        return
    if "tiktok.com" not in url.lower():
        await message.answer("⚠️ يرجى إرسال رابط تيك توك صحيح.", reply_markup=MAIN_MENU)
        return

    status = await message.answer("⏳ جارٍ التحميل...")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Referer": "https://www.tikwm.com/"
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post("https://www.tikwm.com/api/", data={"url": url}, timeout=25) as resp:
                data = await resp.json(content_type=None)
                if data and data.get("code") == 0 and data.get("data"):
                    item = data["data"]
                    title = item.get("title", "تحميل ناجح 🚀")
                    images = item.get("images", [])
                    video_url = item.get("play") or item.get("wmplay") or ""
                    music_url = item.get("music") or ""

                    if video_url.startswith("/"):
                        video_url = f"https://www.tikwm.com{video_url}"
                    if music_url.startswith("/"):
                        music_url = f"https://www.tikwm.com{music_url}"

                    if images:
                        await status.edit_text("📸 جارٍ إرسال الصور...")
                        media_group = [InputMediaPhoto(media=img, caption=title[:1024] if i == 0 else None, parse_mode=None) for i, img in enumerate(images[:10])]
                        await message.answer_media_group(media_group)
                        if music_url:
                            try:
                                await message.answer_audio(audio=music_url, caption="🎵 الصوت المصاحب للصور")
                            except Exception:
                                async with session.get(music_url, timeout=25) as m_resp:
                                    if m_resp.status == 200:
                                        audio_bytes = await m_resp.read()
                                        await message.answer_audio(audio=BufferedInputFile(audio_bytes, filename="audio.mp3"), caption="🎵 الصوت المصاحب للصور")
                    elif video_url:
                        await status.edit_text("🎥 جارٍ إرسال الفيديو...")
                        try:
                            await message.answer_video(video=video_url, caption=title[:1024], parse_mode=None, supports_streaming=True)
                        except Exception:
                            async with session.get(video_url, timeout=45) as v_resp:
                                if v_resp.status == 200:
                                    video_bytes = await v_resp.read()
                                    await message.answer_video(video=BufferedInputFile(video_bytes, filename="tiktok.mp4"), caption=title[:1024], parse_mode=None, supports_streaming=True)
                                else:
                                    raise Exception("Failed to fetch video stream")
                    else:
                        await status.edit_text("❌ لم يتم العثور على وسائط.")
                        return
                    await status.delete()
                else:
                    await status.edit_text("❌ تعذّر جلب البيانات. تأكد من أن الرابط صحيح وأن المقطع عام.")
    except Exception as e:
        log.error(f"Download error: {e}")
        await status.edit_text("❌ حدث خطأ أثناء التحميل.")

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
