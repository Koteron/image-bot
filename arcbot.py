import telebot
import time
import ffmpeg
import os
import moviepy
from moviepy.editor import *
from wand.image import Image

bot = telebot.TeleBot("")
image_filename = ""
video_filename = ""
got_image = False
got_video = False
handler_to_blur = False
handler_to_edge = False
handler_to_bs = False
handler_to_yellow = False
handler_to_sepia = False
handler_to_sketch = False
handler_to_threshold_range = False
time_given = False
time_wait = False
startend = list()


@bot.message_handler(commands=['start'])
def start(message):
    global image_filename, got_image, handler_to_blur, handler_to_edge, handler_to_bs, \
        handler_to_sketch, handler_to_sepia, handler_to_yellow, handler_to_threshold_range, got_video, time_wait, time_given
    bot.send_message(message.from_user.id, "Бот для курсовой по Архитектуре компьютера. Обрабатывает видео и изображения\n"
                                                    "\nblue_shift - Сместить изображение по синей компоненте"
                                                    "\nedge - Оставить только границы на изображении"
                                                    "\nblur - Размыть изображение"
                                                    "\nsketch - Наложить эффект рисунка карандашом"
                                                    "\nsepia - Наложить эффект сепии"
                                                    "\nyellow - Применить жёлтый фильтр"
                                                    "\nthrange - Эффект порогового значения"
                                                    "\ncut число число - Обрезать видео"
                                                    "\nblackwhite - Сделать видео чёрно-белым"
                                                    "\nvdiscard - Удалить видео, находящееся у бота"
                                                    "\ndiscard - Удалить изображение, находящееся у бота")
    for f in os.listdir("files/"+str(message.chat.id)):
        os.remove(os.path.join("files/"+str(message.chat.id),f))
    image_filename = ""
    got_image = False
    got_video = False
    handler_to_blur = False
    handler_to_edge = False
    handler_to_bs = False
    handler_to_yellow = False
    handler_to_sepia = False
    handler_to_sketch = False
    handler_to_threshold_range = False
    time_given = False
    time_wait = False

"""
@bot.message_handler(commands=['add_watermark'])
def add_watermark(message):
    global got_video, video_filename
    if got_video:
        ffmpeg.input(video_filename, i=watermark.png)
        ff.options("-i input.mp4 -i watermark.png -filter_complex overlay=1500:10 output.mp4")
    else:
        bot.send_message(message.from_user.id, "У бота не было файла")
"""

@bot.message_handler(commands=['blackwhite'])
def bw_video(message):
    global video_filename
    if got_video:
        video_file = VideoFileClip(video_filename)
        video_file = moviepy.video.fx.all.blackwhite(video_file)
        video_file.write_videofile(video_filename.split(".")[0] + "_new.mp4")
        os.remove(video_filename)
        video_filename = video_filename.split(".")[0] + "_new.mp4"
        video = open(video_filename, 'rb')
        bot.send_video(message.from_user.id, video, caption="Видео обработано!")
    else:
        bot.send_message(message.from_user.id,
                         "У бота нет видео для обработки!")

@bot.message_handler(commands=['cut'])
def cut_video(message):
    global time_given, startend, got_video, time_wait, video_filename
    if got_video:
        split_message = message.text.split(" ")
        if len(split_message) == 3 and split_message[1].isnumeric() and split_message[2].isnumeric():
            startend = [int(split_message[1]), int(split_message[2])]
            time_given = True
        if time_given:
            video_file = VideoFileClip(video_filename)
            if (startend[1] > video_file.duration or startend[0] > video_file.duration):
                bot.send_message(message.from_user.id,
                                 "Начало или конец видео больше, чем его длина")
                time_given = False
            else:
                video_file.subclip(startend[0], startend[1])
                video_file.write_videofile(video_filename.split(".")[0] + "_new.mp4")
                os.remove(video_filename)
                video_filename = video_filename.split(".")[0] + "_new.mp4"
                video = open(video_filename, 'rb')
                bot.send_video(message.from_user.id, video, caption="Видео обрезано!")
                time_given = False
        else:
            time_wait = True
            bot.send_message(message.from_user.id, "Отправьте время начала видео и время конца видео в секундах:\nПример: 5 10")
    else:
        bot.send_message(message.from_user.id,
                         "У бота нет видео для обработки!")


@bot.message_handler(content_types=['video'])
def handler_video(message):
    global got_video, video_filename
    if not got_video:
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = f'files/{message.chat.id}/' + file_info.file_path.replace('videos/', '')
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        video_filename = new_file.name
        bot.send_message(message.from_user.id, "Видео cохранено!\n"
                                                    "\ncut число число - Обрезать видео"
                                                    "\nblackwhite - Сделать видео чёрно-белым"
                                                    "\nvdiscard - Удалить видео, находящееся у бота")
        got_video = True

@bot.message_handler(commands=['discard'])
def discard_image(message):
    global got_image, image_filename
    if got_image:
        os.remove(image_filename)
        bot.send_message(message.from_user.id, "Файл удалён")
        image_filename = ""
        got_image = False
    else:
        bot.send_message(message.from_user.id, "У бота не было файла")

@bot.message_handler(commands=['vdiscard'])
def discard_video(message):
    global got_video, video_filename
    if got_video:
        os.remove(video_filename)
        bot.send_message(message.from_user.id, "Файл удалён")
        video_filename = ""
        got_video = False
    else:
        bot.send_message(message.from_user.id, "У бота не было файла")

@bot.message_handler(commands=['blur'])
def blur_answer(message):
    global handler_to_blur
    handler_to_blur = True
    if got_image:
        handler_to_blur = False
        blur(message)
    elif message.content_type == 'photo':
        handler_image(message)
    else:
        bot.send_message(message.from_user.id, "Отправьте файл для размытия")

@bot.message_handler(commands=['edge'])
def edge_answer(message):
    global handler_to_edge
    handler_to_edge = True
    if got_image:
        handler_to_edge = False
        draw_edges(message)
    elif message.content_type == 'photo':
        handler_image(message)
    else:
        bot.send_message(message.from_user.id, "Отправьте файл для обработки")

@bot.message_handler(commands=['blue_shift'])
def blue_shift_answer(message):
    global handler_to_bs
    handler_to_bs = True
    if got_image:
        handler_to_bs = False
        blue_shift(message)
    elif message.content_type == 'photo':
        handler_image(message)
    else:
        bot.send_message(message.from_user.id, "Отправьте файл для обработки")

@bot.message_handler(commands=['sketch'])
def sketch_answer(message):
    global handler_to_sketch
    handler_to_sketch = True
    if got_image:
        handler_to_sketch = False
        sketch(message)
    elif message.content_type == 'photo':
        handler_image(message)
    else:
        bot.send_message(message.from_user.id, "Отправьте файл для обработки")

@bot.message_handler(commands=['colorize'])
def colorize_answer(message):
    global handler_to_yellow
    handler_to_yellow = True
    if got_image:
        handler_to_yellow = False
        yellow(message, message.split(" ")[1])
    elif message.content_type == 'photo':
        handler_image(message)
    else:
        bot.send_message(message.from_user.id, "Отправьте файл для обработки")

@bot.message_handler(commands=['sepia'])
def sepia_answer(message):
    global handler_to_sepia
    handler_to_sepia = True
    if got_image:
        handler_to_sepia = False
        sepia(message)
    elif message.content_type == 'photo':
        handler_image(message)
    else:
        bot.send_message(message.from_user.id, "Отправьте файл для обработки")

@bot.message_handler(commands=['thrange'])
def thrange_answer(message):
    global handler_to_threshold_range
    handler_to_threshold_range = True
    if got_image:
        handler_to_threshold_range = False
        thrange(message)
    elif message.content_type == 'photo':
        handler_image(message)
    else:
        bot.send_message(message.from_user.id, "Отправьте файл для обработки")

def blur(message):
    with Image(filename=image_filename) as img:
        img.blur(radius=0, sigma=3)
        img.save(filename=image_filename)
    photo = open(image_filename, 'rb')
    bot.send_photo(message.from_user.id, photo, "Фото размыто!")

def draw_edges(message):
    with Image(filename=image_filename) as img:
        img.transform_colorspace("gray")
        img.edge(radius=1)
        img.save(filename=image_filename)
    photo = open(image_filename, 'rb')
    bot.send_photo(message.from_user.id, photo, "Фото обработано!")

def blue_shift(message):
    with Image(filename=image_filename) as img:
        img.blue_shift(factor=1.25)
        img.save(filename=image_filename)
    photo = open(image_filename, 'rb')
    bot.send_photo(message.from_user.id, photo, "Фото смещено!")

def sketch(message):
    with Image(filename=image_filename) as img:
        img.transform_colorspace("gray")
        img.sketch(0.5, 0.0, 98.0)
        img.save(filename=image_filename)
    photo = open(image_filename, 'rb')
    bot.send_photo(message.from_user.id, photo, "Фото обработано!")

def yellow(message):
    with Image(filename=image_filename) as img:
        img.colorize(color="yellow", alpha="rgb(10%, 0%, 20%)")
        img.save(filename=image_filename)
    photo = open(image_filename, 'rb')
    bot.send_photo(message.from_user.id, photo, "Фото обработано!")

def sepia(message):
    with Image(filename=image_filename) as img:
        img.sepia_tone(threshold=0.8)
        img.save(filename=image_filename)
    photo = open(image_filename, 'rb')
    bot.send_photo(message.from_user.id, photo, "Фото смещено!")

def thrange(message):
    with Image(filename=image_filename) as img:
        img.transform_colorspace('gray')
        white_point = 0.9 * img.quantum_range
        black_point = 0.5 * img.quantum_range
        delta = 0.05 * img.quantum_range
        img.range_threshold(low_black=black_point - delta,
                            low_white=white_point - delta,
                            high_white=white_point + delta,
                            high_black=black_point + delta)
        img.save(filename=image_filename)
    photo = open(image_filename, 'rb')
    bot.send_photo(message.from_user.id, photo, "Фото обработано!")


@bot.message_handler(content_types=['photo', 'document'])
def handler_image(message):
    global image_filename, got_image, handler_to_blur, handler_to_edge, handler_to_bs, handler_to_yellow,\
        handler_to_threshold_range, handler_to_sepia, handler_to_sketch
    if not got_image:
        from pathlib import Path
        Path(f'files/{message.chat.id}/').mkdir(parents=True, exist_ok=True)
        if message.content_type == 'photo':
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            src = f'files/{message.chat.id}/' + file_info.file_path.replace('photos/', '')
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)


        elif message.content_type == 'document':
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            src = f'files/{message.chat.id}/' + message.document.file_name
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)

        image_filename = new_file.name
        got_image = True
        if handler_to_blur or message.caption == "/blur":
            handler_to_blur = False
            blur(message)
        elif handler_to_edge or message.caption == "/edge":
            handler_to_edge = False
            draw_edges(message)
        elif handler_to_bs or message.caption == "/blue_shift":
            handler_to_bs = False
            blue_shift(message)
        elif handler_to_sketch or message.caption == "/sketch":
            handler_to_sketch = False
            sketch(message)
        elif handler_to_yellow or message.caption == "/yellow":
            handler_to_yellow = False
            yellow(message)
        elif handler_to_threshold_range or message.caption == "/thrange":
            handler_to_threshold_range = False
            thrange(message)
        elif handler_to_sepia or message.caption == "/sepia":
            handler_to_sepia = False
            sepia(message)
        else:
            bot.send_message(message.from_user.id, "Бот сохранил изображение.\nblue_shift - Сместить изображение по синей компоненте"
                                                    "\nedge - Оставить только границы на изображении"
                                                    "\nblur - Размыть изображение"
                                                    "\nsketch - Наложить эффект рисунка карандашом"
                                                    "\nsepia - Наложить эффект сепии"
                                                    "\nyellow - Применить жёлтый фильтр"
                                                    "\nthrange - Эффект порогового значения"
                                                    "\ndiscard - Удалить изображение, находящееся у бота")

    else:
        bot.send_message(message.from_user.id, "У бота уже есть файл. (Удалить файл: /discard)")


@bot.message_handler(content_types=['text'])
def handler_text(message):
    global startend, time_given, time_wait
    split_message = message.text.split(" ")
    if time_wait and len(split_message) == 3 and split_message[1].isnumeric() and split_message[2].isnumeric():
        startend = [int(split_message[1]), int(split_message[2])]
        time_given = True
        time_wait = False
    else:
        bot.send_message(message.from_user.id, "Неопознанная команда!")

while True:
    try:
        bot.polling(non_stop=True, interval=0)
    except Exception as e:
        print(e)
        time.sleep(5)
        continue
