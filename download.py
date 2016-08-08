#coding:utf8
'''图片爬虫
'''
import urllib, urllib2
import re
from Queue import Queue

TIMEOUT = 20
enable_proxy = False
proxy_handler = urllib2.ProxyHandler({'http' : 'http://some-proxy.com:8080'})
null_proxy_handler = urllib2.ProxyHandler({})

class ImageSpider(object):
	'''图片爬虫
	'''
	def __init__(self, url):
		self.url = url
		self.headers = { 
	        'Connection':'keep-alive',
	        'Cache-Control':'max-age=0',
	        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36',
	        # 'Accept-Encoding': 'gzip, deflate, sdch',
	        'Accept-Language': 'zh-CN,zh;q=0.8'
		}
		# 链接列表
		self.queue = Queue()
		self.queue.put(url)

		# 访问过的不要重复访问
		self.visited_list = []
		# if enable_proxy:
		# 	opener = urllib2.build_opener(proxy_handler)
		# else:
		# 	opener = urllib2.build_opener(null_proxy_handler)
		 
		# urllib2.install_opener(opener)
		

	def urlopen(self, url, data = '', headers = {}, timeout = TIMEOUT):
		headers = headers or self.headers
		if data:
			req = urllib2.Request(url, data = data, headers = headers)
		else:
			req = urllib2.Request(url, headers = headers)
		response = urllib2.urlopen(req, timeout = timeout)

		return response.read()

	def download_save_img(self, img_url):
		file_name = re.findall(r'/([^/]+)$', img_url)
		file_name = file_name and file_name[0] or 'test.jpg'

		data = self.urlopen(img_url)
		with open('img/%s' % file_name, 'wb') as f:
			f.write(data)

	def get_html(self, url):
		data = self.urlopen(url)

		img_list = re.findall(r'https?://[^\'"]*?\.(?:jpg|png|gif|JPG|PNG|GIF)', data)
		for img in img_list:
			print 'img', img
			try:
				self.download_save_img(img)
			except Exception, e:
				print e

		return data

	def start(self):
		'''开始爬虫
		'''
		while True:
			try:
				url = self.queue.get(block = False)
				if not url:
					break

				if url in self.visited_list:
					continue

				print 'visit', url

				self.visited_list.append(url)

				data = self.get_html(url)
				a_list = re.findall(r'<a .*href=[\'"]([^\'"]*?)[\'"]', data)
				host = re.findall(r'https?://[^/]+', url)
				if host:
					host = host[0]

				for a in a_list:
					if not re.match(r'^https?://', a):
						a = host + a
					self.queue.put(a)
			except Exception, e:
				pass


	def run(self):
		'''入口
		'''
		self.start()


if __name__ == '__main__':
	img = ImageSpider('http://www.netbian.com/desk/14904.htm')
	img.run()