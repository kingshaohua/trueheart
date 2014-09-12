import sys,os,random,time,json
#from i2clibraries import i2c_adxl345
import logging
import threading

class SensorThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.cur_song=""
        self.rangeData=[]
        self.curtime=0
        self.rangeSecond=5
        self.axisX=0
        self.axisY=1
        self.axisZ=2

        self.sample_HZ=100

    def run(self):
        self.analyse()
        print("finish analyse")

    def set_song(self,songname):
        self.cur_song=songname

    def analyse(self):
        for i in range(1,15):
            self.get_data(self.rangeSecond)
            if(self.is_close(self.rangeData)):
                print 'in close'
            else:
                print 'out close'
            #print(self.rangeData)

    def is_close(self,data):
        for i in range(1,self.rangeSecond):
            cellData=data[i*self.sample_HZ:(i+1)*(self.sample_HZ)]
            if(max(self.get_axis_data(cellData,self.axisY)) > 200 and min(self.get_axis_data(cellData,self.axisY))>200):
                print('max='+str(max(self.get_axis_data(cellData,self.axisY))))
                print('min='+str(min(self.get_axis_data(cellData,self.axisY))))
                continue
            else:
                print('max='+str(max(self.get_axis_data(cellData,self.axisY))))
                print('min='+str(min(self.get_axis_data(cellData,self.axisY))))
                return False

        return True

        
    def get_data(self,rangeSecond=5):
        dataLen=len(self.rangeData)
        if dataLen != 0:
            #remove 1 second data,and get one second data
            self.rangeData=self.rangeData[int(dataLen/rangeSecond):]
            self.sample(1)
        else:
            #fill rangeSecond data
            self.sample(rangeSecond)

    def get_axis_data(self,data,axis):
        axisdata=[]
        for item in data:
            axisdata.append(int(item[axis]))
        return axisdata



    def sample(self,second=1):
        if(self.curtime >= 15):
            print("no data")
            return
        #moni data
        fp=open('../sensor_data/sensor_data/close.data','r')
        data=json.loads(fp.read())
        for i in range(self.curtime*100,(self.curtime+second)*100):
            self.rangeData.append(data['sample'][i])
        #self.rangeData.append(data[self.curtime*100:(self.curtime+1)*100])
        self.curtime+=1
        print("append "+str(second)+" second data,len="+str(len(self.rangeData)))
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
    sensor.start()
    time.sleep(10000)

if __name__=='__main__':
    main()