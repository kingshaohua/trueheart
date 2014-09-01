import sys,os,random,time,json



def main(argv):
    songname=argv[1]
    songtime=int(argv[2])
    filepath=os.path.join(os.getcwd(),'sensor_data')
    if (False == os.path.exists(filepath)):
        os.makedirs(filepath)

    #{{x,y,z},{x,y,z}}
    lists=[]
    for t in range(songtime*10):
            lists.append([round(random.uniform(-5, 5),3),
                    round(random.uniform(-5, 5),3),
                    round(random.uniform(-3, 3),3)])
            if(len(lists)%10 == 0):
                write_file(songname,lists)
            #time.sleep(0.1)

def write_file(songname,data):
    filename=os.path.join(os.path.join(os.getcwd(),'sensor_data'),songname+'.data')
    fp = open(filename,'w')
    fp.write(json.dumps(data))
    fp.close()

if __name__ == '__main__':
    main(sys.argv)