import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
from Libs import LCD_1in44
import time
import os

try:
    font = ImageFont.truetype("/root/font.ttf", 10)
except:
    font = ImageFont.load_default()


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
width = 128
height = 128
image = Image.new('RGB', (width, height))
draw = ImageDraw.Draw(image)


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

