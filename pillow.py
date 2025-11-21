import telebot
from telebot.types import InputMediaPhoto,ReplyKeyboardMarkup as Rkm
from PIL import Image,ImageFilter,ImageEnhance
import os

bot = telebot.TeleBot("8442187773:AAFvwgU5QqpOID_fw1LjxvApwqzjDo3Ib_c")
item = {
    'Резкость':'sharpen',
    'Гравировка':'EMBOSS',
    'Конутр':'CONTOUR',
    'Негатив':'negative',
}
@bot.message_handler(["start"])
def start_cmd(message):
    bot.send_message(message.chat.id, 'Я бот по работе с изображением.\n Выберите фильтр')
    kb = Rkm(False,True)
    for i in item.keys():
        kb.row(i)
    bot.send_message(message.chat.id,"Выберите фильтр",reply_markup=kb)

@bot.message_handler(func=lambda message: message.text in item.keys())    
def handle_text(message):
    filters = item[message.text]
    bot.send_message(message.chat.id, f'Вы выбрали {filters},пришлите изображения')
    bot.register_next_step_handler(message,photo_next_page,filters)

def photo_next_page(message:telebot.types.Message,filters):
    #Получение и подготовка файла
    os.makedirs('temp',exist_ok=True)
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    input_path = os.path.join('temp',f"{message.chat.id}_input.jpg")
    output_path = os.path.join('temp',f"{message.chat.id}_output.jpg")
    
    with open(input_path,'wb') as f:
        f.write(downloaded_file)# Обработка изображений
    
    imgeg = Image.open(input_path)
    imgeg.convert('RGB')

    match filters:
        case 'sharpen':
            new_image = imgeg.filter(ImageFilter.SHARPEN)
        case 'EMBOSS':
            new_image = imgeg.filter(ImageFilter.EMBOSS)
        case 'CONTOUR':
            new_image = imgeg.filter(ImageFilter.CONTOUR)
        case 'negative':
            new_image = ImageEnhance.Contrast(imgeg).enhance(-1)

    new_image.save(output_path)
    #Отправка результата

    with open(output_path,'rb') as f:
        bot.send_photo(message.chat.id,f,caption = f"Вот твое фото фильтр:{filters}")
    
    os.remove(input_path)
    os.remove(output_path)

    start_cmd(message)

bot.infinity_polling()