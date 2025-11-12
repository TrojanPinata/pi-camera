import RPi.GPIO as GPIO
import time, os, logging
import board
import digitalio
from PIL import Image, ImageDraw
import numpy as np
from picamera2 import Picamera2, Preview
from datetime import datetime

from encoder import *
from display import *

logger = logging.getLogger(__name__)

GPIO.setmode(GPIO.BCM)

OUTPUT_PATH = "/mnt/tft"
BACKUP_OUTPUT_PATH = "~"

WHITE_BALANCE =   "auto"
DENOISE =         "auto"
METERING =        "centre"
SHARPNESS =       "1.0"
BRIGHTNESS =      "1.0"
CONTRAST =        "1.0"
SATURATION =      "1.0"


SHUTTER_SPEEDS =  [8000000, 4000000, 2000000, 1000000, 500000, 250000, 125000, 66666, 33333, 16666, 8000, 4000, 2000, 1000, 500, 250, 125]
ISO =             [1.0, 2.0, 4.0, 8.0, 16.0]

class Camera:

   def __init__(self):
      logger.info('  Starting encoders')
      self.ss_encoder = Encoder(SS_SW, SS_DT, SS_CLK, 10)
      self.ev_encoder = Encoder(EV_SW, EV_DT, EV_CLK, 0)
      logger.info('  Starting display')
      self.display = Display()

      self.camera = Picamera2()
      self.preview_config = self.camera.create_preview_configuration(
         main={"format": "RGB888", "size": (400, 300)}
      )
      self.still_config = self.camera.create_still_configuration(
         main={"size": (4056, 3040), "format": "RGB888"},
         raw={"size": (4056, 3040)},
      )
      self.camera.configure(self.preview_config)  # initial config
      logger.info('  Starting camera')
      self.camera.start()
      time.sleep(3)  # delay for startup
      logger.info('  Setting default controls')
      self.camera.set_controls({
         "ExposureTime": SHUTTER_SPEEDS[10],
         "AnalogueGain": ISO[0],
         "ExposureValue": 0.0,
         "AwbEnable": True,
         "NoiseReductionMode": 2,
         "AeMeteringMode": 1
      })

      self.last_file = None
      self.last_capture_time = 0
      self.preview_started = False


   def check_encoders(self):

      print(self.ss_encoder.check_switch())
      capture = self.ss_encoder.check_switch()
      ev_index = self.ev_encoder.check_encoder()
      ss_index = self.ss_encoder.check_encoder()
      self.camera.set_controls({
         "ExposureTime": SHUTTER_SPEEDS[ss_index],
         "AnalogueGain": ISO[ev_index],
      })

      self.display.update_params(ss_index, ev_index)
      return capture
   

   def viewfinder(self, state):
      if state == VF:
         if int(datetime.now().strftime("%Y%m%d%H%M%S")) - self.last_capture_time < PREVIEW_CAPTURE_TIME:
            if self.preview_started == False:
               self.display.show_capture(self.last_file)
               self.preview_started = True
         else: 
            self.display.show_viewfinder(self.camera)

      if state == BLANK:
         self.display.black_screen()
      
      if state == PREVIEW:
         self.display.show_capture(self.last_file)

   
   def capture(self, path):
      self.camera.stop()
      self.camera.configure(self.still_config)
      self.camera.start()

      filename = path + f"/RPC_{datetime.now().strftime("%Y%m%d%H%M%S")}"
      filename_dng = filename + ".dng"
      filename_jpg = filename + ".jpg"
      logger.info("Saving capture in " + filename_dng)
      self.camera.capture_file(filename_dng)
      logger.info("Saving capture in " + filename_jpg)
      self.camera.capture_file(filename_jpg)
      self.last_file = filename_jpg

      self.camera.stop()
      self.camera.configure(self.preview_config)
      self.camera.start()

   def set_capture_time(self, capture_time):
      self.preview_started = False
      self.last_capture_time = capture_time


def main():
   try:
      logging.basicConfig(filename='camera.log', level=logging.INFO)

      # check if SD card is mounted
      logger.info("Checking that SPI TFT card is mounted...")
      if os.path.exists(OUTPUT_PATH):
         logger.info('  SD card found')
         path = OUTPUT_PATH
      else:
         logger.info('  No SD card found over SPI in TFT reader. Defaulting to ~/DCIM')
         path = BACKUP_OUTPUT_PATH

      # check DCIM folder exists
      logger.info('Checking for DCIM directory...')
      if os.path.exists(path + "/DCIM"):
         logger.info('  DCIM directory found')
      else:
         logger.info('  DCIM directory not found. Generating...')
         os.makedirs(path + "/DCIM")


      # start hardware and populate default parameters
      logger.info('Starting hardware...')
      cam = Camera()

      while (True):
         capture = cam.check_encoders()
         cam.viewfinder(VF)
         if capture:
            cam.viewfinder(BLANK)
            cam.capture(path)
            cam.set_capture_time(datetime.now().strftime("%Y%m%d%H%M%S"))

   finally:
      cam.camera.close()
      GPIO.cleanup()


if __name__=="__main__":
   main()
