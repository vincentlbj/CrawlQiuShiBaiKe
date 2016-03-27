# coding:utf-8
from bs4 import BeautifulSoup
import urllib
import urllib2
import re
import string

class QSBK:
	def __init__(self):
		#记录当前页数
		self.index = 1
		#身份信息
		self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64)'
		#头部
		self.headers = {'User-Agent' : self.user_agent}
		#保存缓存下来的段子，一个元素为一页
		self.contents = []
		#是否继续的标志
		self.enable = False
	#获取网页源代码
	def getPage(self, index):
		try:
			url = 'http://www.qiushibaike.com/hot/page/' + str(index) 
			request = urllib2.Request(url, headers = self.headers)
			response = urllib2.urlopen(request)
			page = response.read().decode('utf-8')
			return page
		except urllib2.URLError, e:
			if hasattr(e, 'reason'):
				print u'连接网页失败，错误原因',e.reason
				return None
	#格式化抓取下来的段子
	def handle_output(self, name, content, vote):
		dict = {}
		#作者信息去除空格
		newname = "".join(name[0].split())
		#文章内容去除空格和<br/>
		newcontent = "".join(content[0].split()).replace('<br/>', '\n')
		dict['name'] = newname.decode('utf-8')
		dict['content'] = newcontent.decode('utf-8')
		dict['vote'] = vote[0].decode('utf-8')
		return dict
	def getPageContent(self, index):
		page = self.getPage(index)
		if not page:
			print u'页面加载失败'
			return None
		soup = BeautifulSoup(page, 'html.parser')
		#找到段子标签
		tags = soup.find_all('div', attrs = {'class':'article block untagged mb15'})
		#正则表达式
		name_pattern = re.compile('<h2>(.*?)</h2>', re.S)
		content_pattern = re.compile('<div class="content">(.*?)<!', re.S)
		vote_pattern = re.compile('class="stats-vote".*?"number">(.*?)</i>')
		#保存页面中的所有段子
		pagecontents = []
		for tag in tags:
			#筛选掉有图片的段子
			haveImg = re.search('thumb', str(tag))
			if not haveImg:
				#利用正则搜索作者名字，段子内容，被赞数量
				name = re.findall(name_pattern, str(tag))
				content = re.findall(content_pattern, str(tag))
				vote = re.findall(vote_pattern, str(tag))
				dict = self.handle_output(name, content, vote)
				pagecontents.append([dict['name'], dict['content'], dict['vote']])
		return pagecontents
	#加载段子
	def loadPage(self):
		if self.enable == True:
			#如果当前段子页数小于2，则重新抓取
			if(len(self.contents)<2):
				pagecontents = self.getPageContent(self.index)
				#添加到缓存的段子集合中
				if pagecontents:
					self.contents.append(pagecontents)
					self.index += 1
	#交互操作
	def getOneStory(self, contents, page):
		for eachstory in contents:
			input = raw_input()
			self.loadPage()
			if input == 'e':
				self.enable = False
				return
			print u'第%d页\t作者:%s\t被赞:%s\n%s' % (page, eachstory[0], eachstory[2], eachstory[1])
	#主函数
	def start(self):
		print u'正在读取中，按回车浏览新段子，按e退出'
		self.enable = True
		#首先加载一张页面
		self.loadPage()
		nowPage = 0
		while self.enable:
			if len(self.contents) > 0:
				pagecontent = self.contents[0]
				nowPage += 1
				#输出一张页面之后即将它删除
				del self.contents[0]
				#传递一整张页面过去
				self.getOneStory(pagecontent, nowPage)
spider = QSBK()
spider.start()