import sys,os,random,time,json,traceback
from i2clibraries import i2c_adxl345
import psutil
import logging
import threading

class SensorThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.init_log()
        self.cur_song=""
        self.rangeData=[]
        self.curtime=0
        self.rangeSecond=5
        self.axisX=0
        self.axisY=1
        self.axisZ=2

        self.sample_HZ=100
        self.adxl345 = i2c_adxl345.i2c_adxl345(1)
        self.adxl345.setScale(2)

    def init_log(self):
        try:
            logging.basicConfig(filename = os.path.join(os.getcwd(),'mylog_sensor.txt'), level = logging.DEBUG,
            format='LINE %(lineno)-4d : %(levelname)-8s %(message)s')
        except Exception(e):
                print(traceback.format_exc())


    def run(self):
        self.analyse()
        logging.debug("finish analyse")

    def set_song(self,songname):
        self.cur_song=songname

    def analyse(self):
        while True:
            self.get_data(self.rangeSecond)
            self.check_start_stop()
            if self.is_playing():
                if self.check_fav():
                    continue
                if self.check_skip():
                    continue
                
            #print(self.rangeData)
    def is_fav(self):
        timeline=self.get_timeline_YZ()
        if(len(timeline)  < 16):
            return False
        timeline=list(set(timeline))
        if(len(timeline) > 4 ):
            return False
        #logging.debug('is_fav:'+(',').join(timeline))
        if('Y_UP' not in timeline or 'Y_DOWN' not in timeline):
            return False
        else:
            return True

    def is_skip(self):
        timeline=self.get_timeline_YZ()
        if(len(timeline) < 40):
            return False
        timeline_str=(',').join(timeline)
        match_str="Y_UP,Y_DOWN,Y=Z,Z_DOWN,Z_UP,Z_DOWN,Y=Z,Y_DOWN"*1
        if(timeline_str.find(match_str) >=0):
            return True
        else:
            return False

    def get_timeline_YZ(self):
        axisdata=[]
        before_flag=''
        for item in self.rangeData:
            YZ_diff = int(item[self.axisY]) - int(item[self.axisZ])
            flag = ''
            if( YZ_diff < 10 and YZ_diff > -10):
                flag='Y=Z'
            elif (YZ_diff > 50):
                flag='Y_UP'
            elif (YZ_diff < 50 and YZ_diff > 10):
                flag='Y_DOWN'
            elif (YZ_diff < -50):
                flag='Z_UP'
            elif (YZ_diff > -50 and YZ_diff < -10):
                flag='Z_DOWN'

            if ''==flag:
                continue
            if before_flag != flag:
                axisdata.append(flag)
                before_flag=flag

        return axisdata

    def check_fav(self):
        if self.is_fav():
            logging.debug('fav song')
            os.system('python doubancli.py fav_song')
            return True
        else:
            return False

    def check_skip(self):
        if self.is_skip():
            logging.debug('skip song')
            os.system('python doubancli.py skip_song')
            os.system('python doubancli.py start_play_process')
            self.rangeData=[]
            return True
        else:
            return False

    def check_start_stop(self):
        if(self.is_close(self.rangeData)):
            logging.debug('in close')
            if True == self.is_playing():
                os.system('python doubancli.py stop_play_process')
        else:
            logging.debug('out close')
            if False == self.is_playing():
                os.system('python doubancli.py start_play_process')

    def is_playing(self):
        if os.path.exists('./play_song.pid'):
            fp = open('./play_song.pid','r')
            old_pid = fp.read()
            fp.close()
            if psutil.pid_exists(int(old_pid)):
                return True
        return False


    def is_close(self,data):
        for i in range(1,self.rangeSecond):
            cellData=data[i*self.sample_HZ:(i+1)*(self.sample_HZ)]
            if(max(self.get_axis_data(cellData,self.axisY)) > 200 and min(self.get_axis_data(cellData,self.axisY))>200):
                #print('max='+str(max(self.get_axis_data(cellData,self.axisY))))
                #print('min='+str(min(self.get_axis_data(cellData,self.axisY))))
                continue
            else:
                #print('max='+str(max(self.get_axis_data(cellData,self.axisY))))
                #print('min='+str(min(self.get_axis_data(cellData,self.axisY))))
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
        for i in range(1,second*self.sample_HZ):
            (x,y,z) = self.adxl345.getRawAxes()
            self.rangeData.append([x,y,z])
            time.sleep(0.01)
        return

    # def sample(self,second=1):
    #     if(self.curtime >= 15):
    #         print("no data")
    #         return
    #     #moni data
    #     fp=open('../sensor_data/sensor_data/notlike.data','r')
    #     data=json.loads(fp.read())
    #     for i in range(self.curtime*100,(self.curtime+second)*100):
    #         self.rangeData.append(data['sample'][i])
    #     #self.rangeData.append(data[self.curtime*100:(self.curtime+1)*100])
    #     self.curtime+=1
    #     print("append "+str(second)+" second data,len="+str(len(self.rangeData)))
    #     time.sleep(1)
    #     return



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