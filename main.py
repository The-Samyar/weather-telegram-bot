from constants import *
from telegram import Update
from telegram.ext import ContextTypes, Application, CommandHandler
import requests
from pprint import pprint
from datetime import datetime

async def start(update:Update, context:ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Yo")


async def weather(update:Update, context:ContextTypes.DEFAULT_TYPE):
    try:
        user = f"({update.effective_user.username}){update.effective_user.full_name}:"
        args = context.args
        city = ' '.join(args)
        print(f"{user} {city}")
        response = requests.request(
            'get',
            f'http://api.openweathermap.org/geo/1.0/direct?q={city.capitalize()}&limit=1&appid={API_KEY}',
        )
        response = response.json()
        if len(response) != 0:
            lat = response[0]['lat']
            lon = response[0]['lon']

            current_temp = requests.request(
                'get',
                f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={API_KEY}'
            )

            current_temp = current_temp.json()

            message = f"Current temperature of {current_temp['name']}, {current_temp['sys']['country']} is {int(current_temp['main']['temp'])}°"
            if int(current_temp['main']['temp']) != int(current_temp['main']['feels_like']):
                message += f" while it feels like {int(current_temp['main']['feels_like'])}°"

            weather = requests.request(
                'get',
                f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={API_KEY}'
            )

            weather = weather.json()

            message += f".\n\nTemperature forecast for upcoming days:\n"

            weather = weather['list']

            temper_sum = 0
            count = 0
            date = datetime.strptime(weather[0]['dt_txt'], '%Y-%m-%d %H:%M:%S')
            for item in weather:
                cdate = datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S')
                if cdate.date() == date.date():
                    temper_sum += float(item['main']['temp'])
                    count += 1
                else:
                    avg = int(temper_sum / count)
                    message += f"({date.date()}) {date.strftime('%A')} => {avg}°\n"
                    temper_sum = 0
                    count = 0
                    date = cdate
        else:
            message = "Couldn't find the city you are looking for. Try again"

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            reply_to_message_id=update.effective_message.id,
            text=f"{message}"
            )
    except:
        print("Error")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            reply_to_message_id=update.effective_message.id,
            text=f"Error"
            )




def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handlers([
        CommandHandler('start', start),
        CommandHandler('weather', weather)
    ])

    app.run_polling()

if __name__ == '__main__':
    main()
