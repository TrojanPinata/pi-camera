import RPi.GPIO as GPIO
import time, busio
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7735

# UART Reserved = 14, 15

PREVIEW_CAPTURE_TIME = 3

# states
VF       = 0
BLANK    = 1
PREVIEW  = 2

SHUTTER_SPEED_STRINGS   = ["8", "4", "2", "1", "1/2", "1/4", "1/8", "1/15", "1/30", "1/60", "1/125", "1/250", "1/500", "1/1000", "1/2000", "1/4000", "1/8000"]
ISO_STRINGS             = ["100", "200", "400", "800", "1600"]

# TFT SPI Display
DISPLAY_CLK    = board.SCLK
DISPLAY_MOSI   = board.MOSI
DISPLAY_MISO   = board.MISO
DISPLAY_CS     = digitalio.DigitalInOut(board.CE0)
DISPLAY_DC     = digitalio.DigitalInOut(board.D25)
DISPLAY_RST    = digitalio.DigitalInOut(board.D24)


class Display:

   def __init__(self):
      self.spi = board.SPI()
      self.disp = st7735.ST7735R(self.spi, rotation=0, cs=DISPLAY_CS, dc=DISPLAY_DC, rst=DISPLAY_RST, baudrate=24000000)
      self.width = self.disp.width
      self.height = self.disp.height
      self.ss_string = SHUTTER_SPEED_STRINGS[10]
      self.ev_string = ISO_STRINGS[0]

   def update_params(self, ss_index, ev_index):
      self.ss_string = SHUTTER_SPEED_STRINGS[ss_index]
      self.ev_string = ISO_STRINGS[ev_index]


   def black_screen(self):
      width = self.disp.width
      height = self.disp.height
      image = Image.new("RGB", (width, height), (0, 0, 0))

      self.disp.image(image)


   def show_capture(self, filename):
      try:
         image = Image.open(filename)
         image = image.resize((self.disp.width, self.disp.height), Image.LANCZOS)
         image = image.convert("RGB")
         ss_text = f"{self.ss_string}s"
         ev_text = f"ISO {self.ev_string}"
         print(ss_text + " " + ev_text)
         self.disp.image(image)

      except Exception as e:
         print(f"Error displaying capture {filename}: {e}")
         self.black_screen()


   def show_viewfinder(self, camera):
      try:
         frame = camera.capture_array("main")
         image = Image.fromarray(frame)
         image = image.resize((self.disp.width, self.disp.height), Image.LANCZOS)
         image = image.convert("RGB")
         draw = ImageDraw.Draw(image)

         font = ImageFont.load_default()
         draw.rectangle((0, self.disp.height - 20, self.disp.width, self.disp.height), fill=(0, 0, 0))

         ss_text = f"{self.ss_string}s"
         ev_text = f"ISO {self.ev_string}"
         print(ss_text + " " + ev_text)

         draw.text((4, self.disp.height - 16), ss_text, font=font, fill=(255, 255, 255))
         draw.text((self.disp.width - 60, self.disp.height - 16), ev_text, font=font, fill=(255, 255, 255))
   
         image = image.crop((0, 0, self.disp.width, self.disp.height))
         self.disp.image(image)

      except Exception as e:
         print(f"Failure when running viewfinder")
         self.black_screen()

