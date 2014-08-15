import sys,os,time,thread,ConfigParser

class DoubanOnline:
	def __init__(self):
		self.config = ConfigParser.ConfigParser()
        self.dispatch_dic = {'get_captcha':lambda:self.do_get_captcha()}
        try:
            thread.start_new_thread(self.reload_cfg,())
        except:
            print "Error: unable to start thread"

    # def save_cookie(self,cookie):
    #     self.merge_cookie(cookie)
    #     self.cache.set('cookie', self.cookie)

    def do_get_captcha(self,path = "/j/new_captcha"):
        with closing(self.get_fm_conn()) as conn:
            headers = self.get_headers_for_request()

            conn.request("GET", path, None, headers)
            response = conn.getresponse()
            set_cookie = response.getheader('Set-Cookie')
            if not set_cookie is None:
                cookie = SimpleCookie(set_cookie)
                #self.save_cookie(cookie)

            if response.status == 302:
                print '...'
                redirect_url = response.getheader('location')
                self.get_captcha_id(redirect_url)
            if response.status == 200:
                body = response.read()
                self.data['captcha_id'] = body.strip('"')

    def get_captcha_image(self,captcha_id):
        with closing(self.get_fm_conn()) as conn:
            path = "/misc/captcha?size=m&id=" + captcha_id

            import cStringIO

            headers = self.get_headers_for_request()

            conn.request("GET", path, None, headers)
            response = conn.getresponse()

            set_cookie = response.getheader('Set-Cookie')
            if not set_cookie is None:
                cookie = SimpleCookie(set_cookie)
                #self.save_cookie(cookie)

            if response.status == 200:
                body = response.read()
                from PIL import Image
                f = cStringIO.StringIO(body)
                img = Image.open(f)
                img.show();


    def fill_dispach_result():
        pass

	def get_fm_conn(self):
        return httplib.HTTPConnection("douban.fm")


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
