import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
from Libs import LCD_1in44
import time
import os
import subprocess
import psutil
import json

BROADCAST_IP = '<broadcast>'
PORT = 12345


KEY_UP_PIN = 6
KEY_DOWN_PIN = 19
KEY_LEFT_PIN = 5
KEY_RIGHT_PIN = 26
KEY_PRESS_PIN = 13
KEY1_PIN = 21
KEY2_PIN = 20
KEY3_PIN = 16


GPIO.setmode(GPIO.BCM)
GPIO.setup(KEY_UP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY_DOWN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY_LEFT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY_RIGHT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY_PRESS_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(KEY3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


disp = LCD_1in44.LCD()
Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT
disp.LCD_Init(Lcd_ScanDir)
disp.LCD_Clear()

def list_files_in_directory(directory):
    """List all files in the specified directory without extensions."""
    return [os.path.splitext(f)[0] for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

def draw_file_menu(files, selected_index):
    """Draw the file menu on the display in a grid format."""
    draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))


    num_cols = 3
    num_rows = 4
    item_width = width // num_cols
    item_height = 20

    for i, file in enumerate(files):
        col = i % num_cols
        row = i // num_cols
        x = col * item_width
        y = row * item_height

        if i == selected_index:
            text_size = draw.textbbox((0, 0), file, font=font)
            text_width = text_size[2] - text_size[0]
            text_height = text_size[3] - text_size[1]
            draw.rectangle((x, y, x + item_width, y + item_height), fill=(0, 255, 0))
            draw.text((x + 1, y + 1), file, font=font, fill=(0, 0, 0))
        else:
            draw.text((x + 1, y + 1), file, font=font, fill=(255, 255, 255))

    disp.LCD_ShowImage(image, 0, 0)

def execute_file(directory, file_base):
    """Execute the file based on its base name by searching its extension."""
    file_extensions = ['.py', '.sh', '.moj']
    for ext in file_extensions:
        file_path = os.path.join(directory, file_base + ext)
        if os.path.exists(file_path):
            if ext == '.py':
                subprocess.run(['sudo', 'python3', file_path])
            elif ext == '.sh':
                subprocess.run(['sudo', 'bash', file_path])
            elif ext == ".moj":
                subprocess.run(['sudo', './', file_path])
            return

    ui_print(f"Unsupported file: {file_base}")

def show_file_menu():
    directory = "app/"
    files = list_files_in_directory(directory)
    selected_index = 0
    num_cols = 3
    num_rows = 4

    def draw_file_menu(files, selected_index, num_cols, num_rows):
        num_items = len(files)


        cell_width = width // num_cols
        cell_height = height // num_rows

        draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))

        for i, file in enumerate(files):
            y = (i // num_cols) * cell_height
            x = (i % num_cols) * cell_width
            if i == selected_index:
                draw.rectangle((x, y, x + cell_width, y + cell_height), fill=(0, 255, 0))
                draw.text((x + 2, y + 2), file, font=font, fill=(0, 0, 0))
            else:
                draw.text((x + 2, y + 2), file, font=font, fill=(255, 255, 255))

        disp.LCD_ShowImage(image, 0, 0)

    draw_file_menu(files, selected_index, num_cols, num_rows)

    while True:
        if GPIO.input(KEY_UP_PIN) == 0:
            selected_index = (selected_index - num_cols) % len(files)
            draw_file_menu(files, selected_index, num_cols, num_rows)
            time.sleep(0.3)
        if GPIO.input(KEY_DOWN_PIN) == 0:
            selected_index = (selected_index + num_cols) % len(files)
            draw_file_menu(files, selected_index, num_cols, num_rows)
            time.sleep(0.3)
        if GPIO.input(KEY_LEFT_PIN) == 0:
            selected_index = (selected_index - 1) % len(files)
            draw_file_menu(files, selected_index, num_cols, num_rows)
            time.sleep(0.3)
        if GPIO.input(KEY_RIGHT_PIN) == 0:
            selected_index = (selected_index + 1) % len(files)
            draw_file_menu(files, selected_index, num_cols, num_rows)
            time.sleep(0.3)
        if GPIO.input(KEY_PRESS_PIN) == 0:
            selected_file = files[selected_index]
            ui_print(f"Selected: {selected_file}", 1)
            execute_file(directory, selected_file)
            break
        if GPIO.input(KEY1_PIN) == 0:
            break
        if GPIO.input(KEY2_PIN) == 0:
            break
        if GPIO.input(KEY3_PIN) == 0:
            break


width = 128
height = 128
image = Image.new('RGB', (width, height))


draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

def draw_keyboard(selected_key_index, input_text, mode="alpha", caps_lock=False):
    if mode == "alpha":
        keys = [
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
            'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p',
            'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';',
            'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/',
            ' ', 'DEL', '⏎', "!#1", "CAPS"
        ]
    else:
        keys = [
            '!', '"', '£', '$', '%', '&', '/', '(', ')', '=',
            '?', '^', '@', '#', '_', '-', '+', '{', '}', '\\',
            '[', ']', '*', ':', ';', "'", '<', '>', '|', '~',
            ' ', 'DEL', '⏎', "ABC", "CAPS"
        ]

    if caps_lock:
        keys = [key.upper() if key.isalpha() else key for key in keys]

    key_width = 12
    key_height = 12
    cols = 10


    draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))


    draw.text((0, 0), input_text, font=font, fill=(255, 255, 255))


    for i, key in enumerate(keys):
        col = i % cols
        row = i // cols
        x = col * key_width
        y = (row + 1) * key_height
        if i == selected_key_index:
            draw.rectangle((x, y, x + key_width, y + key_height), fill=(0, 255, 0))
            draw.text((x + 2, y + 2), key, font=font, fill=(0, 0, 0))
        else:
            draw.rectangle((x, y, x + key_width, y + key_height), outline=(255, 255, 255))
            draw.text((x + 2, y + 2), key, font=font, fill=(255, 255, 255))


    disp.LCD_ShowImage(image, 0, 0)
def getinput():
    alpha_keys = [
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
        'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p',
        'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';',
        'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/',
        ' ', 'DEL', '⏎', "!#1", "CAPS"
    ]
    special_keys = [
        '!', '"', '£', '$', '%', '&', '/', '(', ')', '=',
        '?', '^', '@', '#', '_', '-', '+', '{', '}', '\\',
        '[', ']', '*', ':', ';', "'", '<', '>', '|', '~',
        ' ', 'DEL', '⏎', "ABC", "CAPS"
    ]

    input_text = ""
    selected_key_index = 0
    mode = "alpha"
    caps_lock = False

    draw_keyboard(selected_key_index, input_text, mode, caps_lock)

    while True:
        if GPIO.input(KEY_UP_PIN) == 0:
            selected_key_index = (selected_key_index - 10) % len(alpha_keys)
            draw_keyboard(selected_key_index, input_text, mode, caps_lock)
            time.sleep(0.3)
        if GPIO.input(KEY_DOWN_PIN) == 0:
            selected_key_index = (selected_key_index + 10) % len(alpha_keys)
            draw_keyboard(selected_key_index, input_text, mode, caps_lock)
            time.sleep(0.3)
        if GPIO.input(KEY_LEFT_PIN) == 0:
            selected_key_index = (selected_key_index - 1) % len(alpha_keys)
            draw_keyboard(selected_key_index, input_text, mode, caps_lock)
            time.sleep(0.3)
        if GPIO.input(KEY_RIGHT_PIN) == 0:
            selected_key_index = (selected_key_index + 1) % len(alpha_keys)
            draw_keyboard(selected_key_index, input_text, mode, caps_lock)
            time.sleep(0.3)


        if GPIO.input(KEY1_PIN) == 0:
            input_text = input_text[:-1]
            draw_keyboard(selected_key_index, input_text, mode, caps_lock)
            time.sleep(0.3)

        if GPIO.input(KEY2_PIN) == 0:
            input_text += ' '
            draw_keyboard(selected_key_index, input_text, mode, caps_lock)
            time.sleep(0.3)

        if GPIO.input(KEY3_PIN) == 0:
            return input_text


        if GPIO.input(KEY_PRESS_PIN) == 0:
            key = alpha_keys[selected_key_index] if mode == "alpha" else special_keys[selected_key_index]
            if key == "DEL":
                input_text = input_text[:-1]
            elif key == "⏎":
                return input_text
            elif key == "!#1":
                mode = "special" if mode == "alpha" else "alpha"
            elif key == "CAPS":
                caps_lock = not caps_lock
            elif key == "ABC":
                mode = "alpha" if mode == "special" else "special"
            else:
                input_text += key.upper() if caps_lock else key

            draw_keyboard(selected_key_index, input_text, mode, caps_lock)
            time.sleep(0.3)

def show_image(image_path, duration=1.25):
    image = Image.open(image_path)
    image = image.resize((128, 128))

    disp.LCD_Clear()
    disp.LCD_ShowImage(image, 0, 0)

    if duration != "unset":
        time.sleep(duration)
        disp.LCD_Clear()
    

def ui_print(message, duration=2, color=(255, 255, 255)):
    draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
    draw.text((10, 50), message, font=font, fill=color)
    disp.LCD_ShowImage(image, 0, 0)
    if duration != "unset":
        time.sleep(duration)
        disp.LCD_Clear()

def bk():
    if GPIO.input(KEY3_PIN) == 0:
        return True

