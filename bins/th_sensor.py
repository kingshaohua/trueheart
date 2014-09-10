import sys,os,random,time,json
from i2clibraries import i2c_adxl345
import logging
import threading

class SensorThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.cur_song=""

    def run(self):
        while True:
            print('cur_song='+self.cur_song)
            time.sleep(5)
    def set_song(self,songname):
        self.cur_song=songname

class ControlThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            print('ControlThread')
            time.sleep(4)

def main():
    sensor=SensorThread()
    control=ControlThread()
    sensor.start()
    control.start()
    time.sleep(5)
    sensor.set_song('myheart')
    time.sleep(5)
    sensor.set_song('myheart2')
    time.sleep(10000)

if __name__=='__main__':
    main()