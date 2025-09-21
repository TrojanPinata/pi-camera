import RPi.GPIO as GPIO
import time, storage, busio
import board
import digitalio
from PIL import Image, ImageDraw
import adafruit_rgb_display.ili9341 as ili9341

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
SD_CS          = digitalio.DigitalInOut(board.CE1)
DISPLAY_DC     = digitalio.DigitalInOut(board.D25)
DISPLAY_RST    = digitalio.DigitalInOut(board.D24)


class Display:

   def __init__(self):
      self.spi = board.SPI()
      self.disp = ili9341.ILI9341(self.spi, DISPLAY_CS, DISPLAY_DC, DISPLAY_RST)
      self.width = self.disp.width
      self.height = self.disp.height
      self.ss_string = SHUTTER_SPEED_STRINGS[10]

   def update_params(self, ss_index, ev_index):
      self.ss_string = SHUTTER_SPEED_STRINGS[ss_index]
      self.ev_string = ISO_STRINGS[ev_index]


   def black_screen(self):
      width = self.disp.width
      height = self.disp.height
      image = Image.new("RGB", (width, height))
      self.disp.image(image)


   def show_capture(self, filename):
      image = Image.open(filename)
      image = image.resize((self.disp.width, self.disp.height))
      self.disp.image(image)


   def show_viewfinder(self):
      return

