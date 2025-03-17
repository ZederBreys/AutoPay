import settings
from automatic import *
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import database
import asyncio
import aiocron
import settings
from random import randint

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(bot)

async def on_startup(dp):
    me = await bot.get_me()
    print(f'Бот запущен. Имя бота: {me.full_name}')

@dp.message_handler(commands=['start'], chat_type='private')
async def start(message: types.Message):
    users = settings.USERS
    if message.chat.id in users:
        await message.reply(f"""<b>Привет! 👋

Я — бот, созданный @XXXXXXX, чтобы напоминать тебе о продлении VPN!

📅 Каждый месяц 15 числа я буду прислать сообщение с кнопкой для оплаты.
🔔 Если ты вдруг забудешь оплатить VPN, я буду напоминать тебе каждые 2 дня.</b>
""", parse_mode="HTML", disable_web_page_preview=True)
        await send_logs(f"Авторизованный пользователь @{message.from_user.username} воспользовался командой /start")    
    else:
        await message.reply(f"Вы не авторизованы", parse_mode="HTML", disable_web_page_preview=True)
        await send_logs(f"Попытка авторизации в боте @{message.from_user.username} пользователя которого нет в списках бота")    


async def send_reminder(user_id, repeated : bool = True):
    """Функция отправки напоминания об оплате"""
    keyboard = types.InlineKeyboardMarkup()
    pay_button = types.InlineKeyboardButton("Оплатить", callback_data="pay")
    keyboard.add(pay_button)
    
    random_int = randint(1, 500)
    random_photo = f"./img/dog_images/dog_{random_int}.jpg"

    if repeated:
        message = (f"<b>🔔 Время продлить VPN!</b>\nНажми «<b>Оплатить</b>», чтобы получить ссылку для оплаты.\n<b>⏳ Важно</b>: Ссылка активна <b>только 10 минут</b> – не откладывай!\n\nСлучайное изображение собаки: {random_int}")
    else:
        message = (f"<b>🔔 VPN ещё не продлён!</b>\nНапоминаю, что для бесперебойной работы нужно оплатить подписку.\nНажми «<b>Оплатить</b>», и я сразу начну генерировать ссылку.\n⏳ <b>Важно:</b> ссылка активна только <b>10 минут.</b>\n\nСлучайное изображение собаки: {random_int}")
    try:
        with open(random_photo, "rb") as photo:
            photo_data = photo.read()
        await bot.send_photo(chat_id=user_id, caption=message, photo=photo_data, parse_mode="HTML", reply_markup=keyboard)
    except:
        pass

@dp.callback_query_handler(lambda c: c.data == "pay")
async def process_payment(callback_query: types.CallbackQuery):
    """Обработчик кнопки оплаты"""
    user_id = callback_query.from_user.id
    
    keyboard = types.InlineKeyboardMarkup()
    pay_button = types.InlineKeyboardButton("Оплатить", callback_data="pay")
    keyboard.add(pay_button)
    
    await callback_query.message.edit_caption(f"{callback_query.message.html_text}\n\n<b>Пожалуйста, подождите... Ссылка на оплату генерируется...</b>", reply_markup=keyboard, parse_mode="HTML")

    try:
        payment_url = get_payment_link(settings.EMAIL, settings.PASSWORD, amount=300)
        if not payment_url:
            raise Exception("Не удалось получить ссылку на оплату")
        await send_logs(f"<b>Не удалось получить ссылку на оплату для пользвателя @{callback_query.from_user.username}</b>")
        
        button = InlineKeyboardMarkup().add(InlineKeyboardButton("Оплатить!", url=payment_url))
        database.remove_unpaid_user(user_id)
        database.add_paid_user(
            user_id=user_id,
            username=callback_query.from_user.username,
            amount=300,
            date=str(datetime.now().strftime("%d.%m.%Y | %H:%M"))
        )
        await send_logs(f"<b>Пользватель @{callback_query.from_user.username} успешно сгенерировал ссылку на оплату!</b>")
        await bot.delete_message(chat_id=user_id, message_id=callback_query.message.message_id)
        with open("./img/description/oplata.png", "rb") as photo:
            await bot.send_photo(chat_id=user_id, caption=f"<b>💳 Ссылка для оплаты готова!\nНажми «Оплатить», выбери удобный способ (СПБ, карта, T-Pay, SberPay и др.) — и всё готово! 🚀</b>", photo=photo, parse_mode="HTML", reply_markup=button)
    except Exception as e:
        print(e)
        await bot.send_message(text="Ошибка при генерации ссылки. Попробуйте еще раз.", chat_id=user_id, parse_mode="HTML")

async def send_logs(text : str):
    now = str(datetime.now().strftime("%d.%m.%Y | %H:%M"))
    print(now, text)
    await bot.send_message(text=text, chat_id=settings.ADMINS_LOGS_CHANNEL, parse_mode="HTML", disable_web_page_preview=True, disable_notification=True) 


async def monthly_reminder():
    users = settings.USERS  # Список пользователей
    for user_id in users:
        database.add_unpaid_user(user_id=user_id) #Отмечаем не оплаченным
        await send_reminder(user_id)
        await send_logs(f"Отправлено сообщение с просьбой оплатить {user_id}")

async def overdue_reminder():
    unpaid_users = database.get_unpaid_users()  # Список пользователей, которые не оплатили
    for user_id in unpaid_users:
        await send_reminder(user_id, repeated=False)
        await send_logs(f"ПОВТОРНОЕ сообщение с просьбой оплатить {user_id}")

async def start_bot():
    await on_startup(dp)
    await dp.start_polling()

async def main():
    # Запускаем напоминание 15 числа каждого месяца в 10:00 утра
    aiocron.crontab('0 10 15 * *', func=monthly_reminder)
    # Запускаем напоминание каждые 2 дня, если не было оплаты
    aiocron.crontab('0 10 */2 * *', func=overdue_reminder)

    await asyncio.gather(start_bot())

if __name__ == "__main__":
    asyncio.run(main())