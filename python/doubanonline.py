import sys,os,time,thread,ConfigParser,traceback
import json, urllib, httplib, contextlib, random, binascii, calendar
from select import select
from contextlib import closing
from dateutil import parser
from Cookie import SimpleCookie
import pickle

class Cache:
    """docstring for cache"""
    def has(self, name):
        file_name = self.get_cache_file_name(name)
        return os.path.exists(file_name)

    def get(self, name, default = None):
        file_name = self.get_cache_file_name(name)
        if not os.path.exists(file_name):
            return default
        cache_file = open(file_name, 'rb')
        content = pickle.load(cache_file)
        cache_file.close()
        return content

    def set(self, name, content):
        file_name = self.get_cache_file_name(name)
        cache_file = open(file_name, 'wb')
        pickle.dump(content, cache_file)
        cache_file.close()

    def get_cache_file_name(self, name):
        # file should put into a `cache` dir
        return name + '.cache'


class DoubanOnline:
    def __init__(self):
        self.cache = Cache()
        self.config = ConfigParser.ConfigParser()
        self.dispatch_dic = {'get_captcha':lambda:self.do_get_captcha()}
        self.init_cookie()
        self.data={}
        try:
            thread.start_new_thread(self.dispatch,())
        except:
            print "Error: unable to start thread"

    def init_cookie(self):
        self.cookie = {}
        cookie = self.cache.get('cookie', {})
        self.merge_cookie(cookie)

    def save_cookie(self,cookie):
         self.merge_cookie(cookie)
         self.cache.set('cookie', self.cookie)

    # maybe we should extract a class XcCookie(SimpleCookie)
    # merge(SimpleCookie)
    def merge_cookie(self, cookie):
        for key in cookie:
            expires = cookie[key]['expires']
            if expires:
                expires = parser.parse(expires)
                expires = calendar.timegm(expires.utctimetuple())
                now = time.time()
                if expires > now:
                    self.cookie[key] = cookie[key]
                else:
                    if key in self.cookie:
                        del self.cookie[key]
            else:
                self.cookie[key] = cookie[key]


    def do_get_captcha(self,path = "http://douban.fm/j/new_captcha"):
        print "do_get_captcha:path="+path
        try:
            with closing(self.get_fm_conn()) as conn:
                headers = self.get_headers_for_request()
                conn.request("GET", path, None, headers)
                response = conn.getresponse()
                set_cookie = response.getheader('Set-Cookie')
                if not set_cookie is None:
                    cookie = SimpleCookie(set_cookie)
                    self.save_cookie(cookie)

                if response.status == 302:
                    print '...'
                    redirect_url = response.getheader('location')
                    return self.do_get_captcha(redirect_url)
                if response.status == 200:
                    body = response.read()
                    captcha_id = body.strip('"')
                    self.data['captcha_id'] = captcha_id
                    self.data['captcha_file'] = self.get_captcha_image(captcha_id)
        except Exception,e:
            print e
            print traceback.format_exc()

    def get_captcha_image(self,captcha_id):
        print 'get_captcha_image:'+captcha_id
        with closing(self.get_fm_conn()) as conn:
            path = "http://douban.fm/misc/captcha?size=m&id=" + captcha_id

            import cStringIO

            headers = self.get_headers_for_request()

            conn.request("GET", path, None, headers)
            response = conn.getresponse()

            set_cookie = response.getheader('Set-Cookie')
            if not set_cookie is None:
                cookie = SimpleCookie(set_cookie)
                self.save_cookie(cookie)

            if response.status == 200:
                body = response.read()
                from PIL import Image
                f = cStringIO.StringIO(body)
                img = Image.open(f)
                img.save('E:\github\kingshaohau\trueheart\python\1.jpg');
                print 'save ok'

    # todo XcCookie.get_request_string()
    def get_cookie_for_request(self):
        cookie_segments = []
        for key in self.cookie:
            cookie_segment = key + '="' + self.cookie[key].value + '"'
            cookie_segments.append(cookie_segment)
        return '; '.join(cookie_segments)

    def fill_dispach_result():
        pass

    def get_fm_conn(self):
        return httplib.HTTPConnection("10.64.8.8", "8080")


    def get_headers_for_request(self, extra = {}):
        headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/28.0.1500.71 Chrome/28.0.1500.71 Safari/537.36',
            'Referer': 'http://douban.fm/',
            'Accept-Language': 'zh-CN,zh;q=0.8'
        }
        if self.cookie:
            cookie_str = self.get_cookie_for_request()
            headers['Cookie'] = cookie_str
        for key in extra:
            headers[key] = extra[key]
        return headers


    def login(self,username,password):
        print u'login...'
        data = {
                'source': 'radio',
                'alias': username, 
                'form_password': password,
                'remember': 'on',
                'task': 'sync_channel_list'
                }

    def reload_cfg(self):
        while 1:
            self.config.read('douban.config')
            print 'section:',self.config.sections()
            print self.config.get('auth','user')
            print self.config.get('auth','password')
            time.sleep(5)

    def dispatch(self):
        while 1:
            time.sleep(1)
            self.config.read('douban.config')
            try:
                self.dispatch_dic[self.config.get('dispatch','oper')]()
            except:
                print("no such command.")
            break



def main():
    print u"Douban Online"
    douban=DoubanOnline()
    while 1:
        time.sleep(1)


if __name__ == "__main__":
        main()
