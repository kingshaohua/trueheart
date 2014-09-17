import sys,os,random,time,json
import logging

class SensorCLI():
    def __init__(self):
        filepath=os.path.join(os.getcwd(),'sensor_data')
        if (False == os.path.exists(filepath)):
            os.makedirs(filepath)
        self.sample_interval = 10  #millisecond
        logging.basicConfig(filename = os.path.join(os.getcwd(),'mylog.txt'), level = logging.DEBUG,
            format='LINE %(lineno)-4d : %(levelname)-8s %(message)s')
        
    def moni_data(self,songname,songtime):
        filepath=os.path.join(os.getcwd(),'sensor_data')
        if (False == os.path.exists(filepath)):
            os.makedirs(filepath)
        data={}
        data['interval'] = self.sample_interval
        data['sample'] = []
        for t in range(int(songtime)*1000/self.sample_interval ):
            data['sample'].append([round(random.uniform(-5, 5),3),
                    round(random.uniform(-5, 5),3),
                    round(random.uniform(-3, 3),3)])
            if(len(data['sample'])%10 == 0):
                self.write_data(songname,data)
            time.sleep(0.1)

    def write_data(self,songname,data):
        filename=self.get_data_file(songname) 
        fp = open(filename,'w')
        fp.write(json.dumps(data))
        fp.close()

    def get_data_file(self,songid):
        return os.path.join(os.path.join(os.getcwd(),'sensor_data'),songid+'.data')

    #get sensor data
    def get_data(self,songid,startmsec,endmsec):
        filename=self.get_data_file(songid) 
        if(os.path.exists(filename)):
            fp = open(filename,'r')
            data=json.loads(fp.read())
            startIndex=int(startmsec)/int(data['interval'])
            endIndex=int(endmsec)/int(data['interval'])
            data['sample']=data['sample'][int(startIndex):int(endIndex)]
            self.show_result(0,data)
        else:
            self.show_result(-1,"no data")

    def show_result(self,code,data):
        obj={}
        obj['code']=code
        obj['data']=data
        print(json.dumps(obj))

def main(argv):
    sensorcli = SensorCLI()
    cmd=argv[1]
    logging.debug('cmd='+' '.join(argv))
    if("get_data" == cmd):
        sensorcli.get_data(argv[2],argv[3],argv[4])
    elif("moni_data" == cmd):
        sensorcli.moni_data(argv[2],argv[3])
    elif("start_record" == cmd):
        sensorcli.start_record(argv[2],argv[3])
    else:
        print("no such cmd:"+cmd)

if __name__ == '__main__':
    main(sys.argv)