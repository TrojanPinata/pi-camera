import RPi.GPIO as GPIO
import time
import board

# Shutter Speed Dial
SS_SW =  18
SS_DT =  17
SS_CLK = 4

# EV Compensation Dial
EV_SW =  3
EV_DT =  5
EV_CLK = 6


class Encoder:

   def __init__(self, sw, dt, clk, starting_index, max_index):
      self.sw = sw
      self.dt = dt
      self.clk = clk

      GPIO.setmode(GPIO.BCM)
      GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_UP)
      GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
      GPIO.setup(sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)

      self.last_state = GPIO.input(clk)
      self.index = starting_index
      self.max_index = max_index


   def check_switch(self):
      if GPIO.input(self.sw) == 0:
         return True
      return False
   
   def check_encoder(self):
      clk_state = GPIO.input(self.clk)
      dt_state = GPIO.input(self.dt)
      if clk_state != self.last_state:
         if dt_state != clk_state:
            self.index += 1
         else:
            self.index -= 1

         if (self.index < 0):
            self.index = 0
         if (self.index > self.max_index):
            self.index = self.max_index
      self.last_state = clk_state
      return self.index

   



