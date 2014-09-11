import sys,os,random,time,json
from i2clibraries import i2c_adxl345
import logging
import threading

class SensorThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.cur_song=""
        self.rangeData=[]
        self.curtime=0
        self.rangeSecond=5

    def run(self):
        while True:
            print('cur_song='+self.cur_song)
            time.sleep(5)

    def set_song(self,songname):
        self.cur_song=songname

    def analyse(self):
        while True:
            self.get_data(self.rangeSecond)

    def is_close(self,data):
        
    def get_data(self,rangeSecond=5):
        dataLen=len(self.rangeData)
        if dataLen != 0:
            #remove 1 second data,and get one second data
            self.rangeData=self.rangeData[int(4*dataLen/5):]
            self.sample(1)
        else:
            #fill rangeSecond data
            self.sample(5)

    def sample(self,second=1):
        if(self.curtime >= 15):
            print("no data")
            return
        #moni data
        fp=open('../sensor_data/sensor_data/close.data','r')
        data=json.loads(fp.read())
        self.rangeData.append(data[self.curtime*100:(self.curtime+1)*100])
        self.curtime+=1
        print("append one second data")
        time.sleep(1)
        return



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