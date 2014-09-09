import sys,os,time,thread,ConfigParser,traceback,random
import urllib2,json,urllib,subprocess
import cookielib
import logging


class DoubanCLI(object):
    def __init__(self):
        self.init_log()
        self.cookiefile="mycookie.txt"
        self.config = ConfigParser.ConfigParser()
        self.opener = self.get_opener()
        self.load_config()
        self.channel = 0
        self.ck=""
        self.uid=""
        

    def init_log(self):
        try:
            logging.basicConfig(filename = os.path.join(os.getcwd(),'mylog.txt'), level = logging.DEBUG,
            format='LINE %(lineno)-4d : %(levelname)-8s %(message)s')
            #logging.Formatter()  
            # define a Handler which writes INFO messages or higher to the sys.stderr
            #console = logging.StreamHandler();
            #console.setLevel(logging.DEBUG);
            # set a format which is simpler for console use
            #formatter = logging.Formatter('LINE %(lineno)-4d : %(levelname)-8s %(message)s');
            # tell the handler to use this format
            #console.setFormatter(formatter);
            #logging.getLogger('').addHandler(console);
        except Exception,e:
                print traceback.format_exc()

    def __del__(self):
        self.cookie.save(self.cookiefile,ignore_discard=True, ignore_expires=True)
        self.save_config()
        


    def get_opener(self):
        if(os.path.isfile(self.cookiefile)):
            self.cookie=cookielib.LWPCookieJar()
            self.cookie.load(self.cookiefile,ignore_discard=True, ignore_expires=True)
            logging.debug("load cookie")

        else:
            self.cookie=cookielib.LWPCookieJar()
            #self.cookie.save(self.cookiefile)
            logging.debug("new cookie")
        return urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))

    def get_captcha(self):
        try:
            captcha_id = self.opener.open(urllib2.Request('http://douban.fm/j/new_captcha')).read().strip('"') 
            self.config.set('auth','captcha_id',captcha_id)
            captcha = self.opener.open(urllib2.Request('http://douban.fm/misc/captcha?size=m&id=' + captcha_id)).read()
            file = open('captcha.jpg', 'wb')
            file.write(captcha)
            file.close()
            logging.debug("save captcha.jpg ok")
            self.show_result(0,'save captcha.jpg ok')
        except Exception,e:
            print traceback.format_exc()

    def load_config(self):
        self.config.read(R"douban.config")
        self.user_info = self.config.get('data','user_info')
        if("" != self.user_info):
            self.user_info = json.loads(self.user_info)
            self.play_record = self.user_info['play_record']
            self.uid = self.user_info['uid']
            self.ck  = self.user_info['ck']
        else:
            self.user_info = None

        self.songlist = self.config.get('data','songlist')
        if("" != self.songlist):
            self.songlist = json.loads(self.songlist)
        else:
            self.songlist = None

        self.cur_song = self.config.get('data','cur_song')
        if("" != self.cur_song):
            self.cur_song = json.loads(self.cur_song)
        else:
            self.cur_song = None

    def save_config(self):
        if(None != self.user_info):
            self.config.set('data','user_info',json.dumps(self.user_info))
        else:
            self.config.set('data','user_info','')
        if(None != self.songlist):
            self.config.set('data','songlist',json.dumps(self.songlist))
        else:
            self.config.set('data','songlist','')
        if(None != self.cur_song):
            self.config.set('data','cur_song',json.dumps(self.cur_song))
        else:
            self.config.set('data','cur_song','')

        self.config.write(open(R'douban.config', "w"))

    def login(self):
        logging.debug('login...')
        try:
            response = json.loads(self.opener.open(
                  urllib2.Request('http://douban.fm/j/login'),
                  urllib.urlencode({
                      'source': 'radio',
                      'alias': self.config.get('auth','username'),
                      'form_password': self.config.get('auth','password'),
                      'captcha_solution': self.config.get('auth','captcha_solution'),
                      'captcha_id': self.config.get('auth','captcha_id'),
                      'task': 'sync_channel_list'})).read())

            logging.debug(response)

            self.config.set('auth','captcha_solution','')
            self.config.set('auth','captcha_id','')
            if 'err_msg' in response.keys():
                logging.error(response['err_msg'])
                self.show_result(-1,response['err_msg'])
            else:
                logging.debug('login success')
                self.user_info=response['user_info']
                self.play_record=self.user_info['play_record']
                self.show_result(0,self.user_info)

        except Exception,e:
            logging.error(traceback.format_exc())

    def logout(self):
        logging.debug('logout...')
        try:
            response = self.opener.open(
                urllib2.Request('http://douban.fm/partner/logout?source=radio&ck=aM21&no_login=y')
                      ).read()
            #logging.debug(response)
            self.user_info=""
            self.cookie.clear()
            os.remove(self.cookiefile)
            self.show_result(0,'ok')
        except Exception,e:
            logging.error(traceback.format_exc()) 

    def get_params(self,typename=None):
        params = {}
        params['r'] = ''.join(random.sample('0123456789abcdefghijklmnopqrstuvwxyz0123456789', 10))
        params['uid'] = self.uid
        params['channel'] = self.channel
        params['from'] = 'mainsite'
        if typename is not None:
            params['type'] = typename
        return params

    def communicate(self,params):
        try:
            data = urllib.urlencode(params)
            logging.debug('data='+data)
            return json.loads(self.opener.open(urllib2.Request('http://douban.fm/j/mine/playlist?'+data)).read())
        except Exception,e:
            logging.error(traceback.format_exc()) 

    def get_playlist(self):
        logging.debug('Fetching playlist ...')
        params = self.get_params('n')
        result = self.communicate(params)
        logging.debug(result)
        if(len(result['song']) == 0):
            logging.error('need logging')
        else:
            self.deal_new_songlist(result['song'])

    #fav unfav
    def fav_song(self):
        params = self.get_params('r')
        params['sid'] = self.cur_song['sid']
        params['aid'] = self.cur_song['aid']
        result = self.communicate(params)
        self.cur_song['like']=1
        self.deal_new_songlist(result['song'])

        

    def unfav_song(self):
        params = self.get_params('u')
        params['sid'] = self.cur_song['sid']
        params['aid'] = self.cur_song['sid']
        result = self.communicate(params)
        self.cur_song['like']=0
        self.deal_new_songlist(result['song'])

    #next song
    def skip_song(self):
        if None == self.songlist:
            self.get_playlist()
            return
        if None == self.cur_song :
            self.cur_song = self.songlist[0]
        else:
            for r in self.songlist:
                if None == self.cur_song :
                    self.cur_song = r
                    return
                if (self.cur_song['sid'] != r['sid']):
                    continue
                else:
                    self.cur_song = None
            #not find
            if(None == self.cur_song):
                self.get_playlist()
            else:
                self.cur_song = self.songlist[0]

    #delete song
    def del_song(self):
        params = self.get_params('b')
        params['sid'] = self.cur_song['sid']
        params['aid'] = self.cur_song['aid']
        result = self.communicate(params)
        self.deal_new_songlist(result['song'])
        self.cur_song = None
        self.skip_song()

    def deal_new_songlist(self,songlist):
        self.songlist = songlist
        if None == self.cur_song:
            self.cur_song=self.songlist[0]
        
    def show_cur_song(self):
        if(None == self.cur_song):
            self.skip_song()
        self.show_result(0,self.cur_song)

    def show_result(self,code,data):
        obj={}
        obj['code']=code
        obj['data']=data
        print json.dumps(obj)

    def set_auth(self,user,pwd,captcha):
        logging.debug('user='+user+',pwd='+pwd+',captcha='+captcha)
        self.config.set('auth','username',user)
        self.config.set('auth','password',pwd)
        self.config.set('auth','captcha_solution',captcha)

    def is_login(self):
        logging.debug('is_login?')
        self.channel=-3
        params = self.get_params('n')
        result = self.communicate(params)
        logging.debug(result)
        if(len(result['song']) == 0):
            self.show_result(-1,"not login.")
        else:
            self.show_result(0,'alreay login.')

    def play_song(self):
        logging.debug('play_song:'+json.dumps(self.cur_song))
        #kill other play song process,sensor record process
        
        #start play song

        #start sensor record.
        #mysensor = sensorcli.SensorCLI()
        #mysensor.moni_data(self.cur_song['sid'],self.cur_song['length'])

    def start_play_process(self):
        logging.debug('start_play_process.')
        subprocess.Popen('python doubancli.py play_song')


def main(argv):
    doubancli=DoubanCLI()
    cmd=argv[1]
    logging.debug(argv)
    if("get_captcha" == cmd):
        doubancli.get_captcha()
    elif ("login" == cmd):
        doubancli.login()
    elif ("get_playlist" == cmd):
        doubancli.get_playlist()
    elif ("logout" == cmd):
        doubancli.logout()
    elif ("skip_song" == cmd):
        doubancli.skip_song()
        doubancli.show_cur_song()
    elif ("fav_song" == cmd):
        doubancli.fav_song()
        doubancli.show_cur_song()
    elif ("unfav_song" == cmd):
        doubancli.unfav_song()
        doubancli.show_cur_song()
    elif ("del_song" == cmd):
        doubancli.del_song()
        doubancli.show_cur_song()
    elif ("cur_song" == cmd):
        doubancli.show_cur_song()
    elif ('set_auth' == cmd):
        doubancli.set_auth(argv[2],argv[3],argv[4])
    elif ('is_login' == cmd):
        doubancli.is_login()
    elif ('play_song' == cmd):
        doubancli.play_song()
    elif ('start_play_process' == cmd):
        doubancli.start_play_process()
    else:
        print "no such cmd:"+cmd

if __name__ == "__main__":
        main(sys.argv)