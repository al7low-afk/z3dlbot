import os
import asyncio
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery,
    LabeledPrice, PreCheckoutQuery
)
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
log = logging.getLogger("azkar-bot")

AZKAR_TOKEN = "8969387100:AAFPMrP7ZEQwKmROZO-56BT-QtG_tt-iAd8"
CHANNEL = "@azkar201"
TIMEZONE = ZoneInfo("Asia/Dubai")

bot = Bot(AZKAR_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# الأزرار التفاعلية للبوت (تظهر للمستخدم عند محادثة البوت شخصياً)
AZKAR_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌅 أذكار الصباح"), KeyboardButton(text="🌇 أذكار المساء")],
        [KeyboardButton(text="🕌 أذكار بعد الصلاة"), KeyboardButton(text="😴 أذكار النوم")],
        [KeyboardButton(text="📿 تسبيح"), KeyboardButton(text="🌟 إرسال هدية (نجوم) 🌟")],
    ],
    resize_keyboard=True,
    input_field_placeholder="اختر قسم الأذكار",
)

STARS_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⭐️ 10 نجوم", callback_data="gift_stars_10")],
        [InlineKeyboardButton(text="🌟 50 نجمة", callback_data="gift_stars_50")],
        [InlineKeyboardButton(text="🚀 100 نجمة", callback_data="gift_stars_100")],
        [InlineKeyboardButton(text="👑 500 نجمة", callback_data="gift_stars_500")],
    ]
)

AZKAR_TEXTS = {
    "🌅 أذكار الصباح": "🌅 <b>أذكار الصباح</b>\n\nأصبحنا وأصبح الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له، له الملك وله الحمد، وهو على كل شيء قدير.",
    "🌇 أذكار المساء": "🌇 <b>أذكار المساء</b>\n\nأمسينا وأمسى الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له، له الملك وله الحمد، وهو على كل شيء قدير.",
    "🕌 أذكار بعد الصلاة": "🕌 <b>أذكار بعد الصلاة</b>\n\nأستغفر الله (3 مرات)\nاللهم أنت السلام ومنك السلام تباركت يا ذا الجلال والإكرام.",
    "😴 أذكار النوم": "😴 <b>أذكار النوم</b>\n\nباسمك اللهم أموت وأحيا.",
}

# قائمة الأذكار والأدعية الصافية التي تُرسل للقناة مباشرة بدون عناوين
DAILY_AZKAR_AND_DUAS = [
    "سبحان الله وبحمده، سبحان الله العظيم.",
    "لا إله إلا الله وحده لا شريك له، له الملك وله الحمد، وهو على كل شيء قدير.",
    "أستغفر الله العظيم الذي لا إله إلا هو الحي القيوم وأتوب إليه.",
    "لا حول ولا قوة إلا بالله العلي العظيم.",
    "سُبْحَانَ اللَّهِ، وَالْحَمْدُ لِلَّهِ، وَلَا إِلَهَ إِلَّا اللَّهُ، وَاللَّهُ أَكْبَرُ.",
    "اللَّهُمَّ إنِّي أسألُكَ العافيةَ في الدنيا والآخرة.",
    "رَبِّ اغْفِر لي وَتُبْ عَلَيَّ إنَّكَ أنتَ التَّوَّابُ الرَّحيمُ.",
    "يا حي يا قيوم برحمتك أستغيث، أصلح لي شاني كله ولا تكلني إلى نفسي طرفة عين.",
    "لَا إِلَهَ إِلَّا أَنْتَ سُبْحَانَكَ إِنِّي كُنْتُ مِنَ الظَّالِمِينَ.",
    "رَبنا آتنا في الدنيا حسنة وفي الآخرة حسنة وقنا عذاب النار.",
    "حسبنا الله ونعم الوكيل، نعم المولى ونعم النصير.",
    "رضيت بالله رباً، وبالإسلام ديناً، وبمحمد صلى الله عليه وسلم نبياً ورسولاً.",
    "اللهم إني أسألك علماً نافعاً، ورزقاً طيباً، وعملاً متقبلاً.",
    "ربنا لا تزغ قلوبنا بعد إذ هديتنا وهب لنا من لدنك رحمة إنك أنت الوهاب.",
]

SALAWAT_MESSAGES = [
    "إِنَّ اللَّهَ وَمَلَائِكَتَهُ يُصَلُّونَ على النَّبِيِّ يَا أَيُّهَا الَّذِينَ آمَنُوا صَلَُّوا عَلَيْهِ وَسَلِّمُوا تَسْلِيماً 🤍\n\nاللهم صلِ وسلّم وبارك على نبينا محمد وعلى آله وصحبه أجمعين.",
    "صلى الله عليه وسلم تسليماً كثيراً عدد ما ذكره الذاكرون وغفل عن ذكره الغافلون ✨",
    "اللهم صلِ على محمد وعلى آل محمد كما صليت على إبراهيم وعلى آل إبراهيم إنك حميد مجيد 🕊️",
]

@dp.message(Command("start"))
async def azkar_start(message: Message):
    await message.answer("أهلاً بك في بوت الأذكار والأدعية 🕌\nاختر القسم المناسب من الأزرار أدناه:", reply_markup=AZKAR_MENU)

@dp.message(F.text == "📿 تسبيح")
async def azkar_tasbeeh(message: Message):
    await message.answer("📿 سبحان الله، والحمد لله، ولا إله إلا الله، والله أكبر.", reply_markup=AZKAR_MENU)

@dp.message(F.text == "🌟 إرسال هدية (نجوم) 🌟")
async def show_stars_options(message: Message):
    await message.answer("اختر عدد النجوم التي ترغب بإهدائها لدعم بوت الأذكار والقناة 🎁:", reply_markup=STARS_KEYBOARD)

@dp.callback_query(F.data.startswith("gift_stars_"))
async def process_gift_stars(callback: CallbackQuery):
    stars_amount = int(callback.data.split("_")[-1])
    prices = [LabeledPrice(label=f"هدية {stars_amount} نجمة", amount=stars_amount)]
    
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=f"إرسال {stars_amount} نجمة 🌟",
        description=f"دعم بوت الأذكار بـ {stars_amount} من نجوم تيليجرام!",
        payload=f"azkar_gift_{stars_amount}_stars",
        currency="XTR",
        prices=prices,
    )
    await callback.answer()

@dp.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    await message.answer("❤️ جزاك الله خيراً وجعل هذا الدعم والهدايا في ميزان حسناتك.")

@dp.message(F.text.in_(list(AZKAR_TEXTS.keys())))
async def azkar_section(message: Message):
    await message.answer(AZKAR_TEXTS[message.text], reply_markup=AZKAR_MENU)

# حلقة النشر التلقائي للقناة (ترسل النص صافي وبدون أي عناوين فوقه)
async def automated_poster():
    last_salawat_time = datetime.now(TIMEZONE) - timedelta(days=3)

    while True:
        await asyncio.sleep(7200)  # انتظار ساعتين

        try:
            now = datetime.now(TIMEZONE)
            
            # 1. الصلاة على النبي (كل 3 أيام أو يوم الجمعة)
            is_friday = (now.weekday() == 4)
            time_passed = (now - last_salawat_time).total_seconds() >= 259200

            if is_friday or time_passed:
                await bot.send_message(chat_id=CHANNEL, text=random.choice(SALAWAT_MESSAGES))
                log.info("تم نشر الصلاة على النبي ﷺ في القناة.")
                last_salawat_time = now

            # 2. إرسال الذكر أو الدعاء مباشرة بدون أي عناوين أو تصنيفات
            await bot.send_message(chat_id=CHANNEL, text=random.choice(DAILY_AZKAR_AND_DUAS))
            log.info("تم نشر ذكر/دعاء في القناة.")

        except Exception as e:
            log.error(f"خطأ في النشر التلقائي: {e}")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print("🚀 بوت الأذكار والأدعية يعمل بكفاءة تامة!")
    
    await asyncio.gather(
        dp.start_polling(bot),
        automated_poster()
    )

if __name__ == "__main__":
    asyncio.run(main())