import sys,urllib2,os,httplib,glob,shutil
from urllib import urlretrieve
from module import BeautifulSoup

def cleanup(dirname):
	for jpgFile in glob.glob(os.path.join(dirname, '*.jpg')):
		chapter_arr = jpgFile.split("-")
		chapter = chapter_arr[0]

		if not os.path.exists(chapter):
			os.makedirs(chapter)

		shutil.copy(jpgFile,chapter)
		os.remove(jpgFile)

	print ">>> Done"

def getit(dirname,target_url):

	print ">>> " + target_url
	try:
		req = urllib2.Request(target_url)
		response = urllib2.urlopen(req)
		the_page = response.read()

		soup = BeautifulSoup.BeautifulSoup(the_page)
		imgholder = soup.find("div", attrs={"id": "imgholder"})
		imgholder_a = imgholder.find('a')
		next_url = "http://www.mangareader.net"
		next_url += imgholder_a['href'];

		url = imgholder.find('img')['src']

		lnk = url.split("/")
		name = lnk[-1]
		chapter = lnk[-2]
		
		if not os.path.exists(dirname):
			os.makedirs(dirname)

		chapter_path = os.path.join(dirname, chapter+"-"+name)
		if not os.path.exists(chapter_path):
			urlretrieve(url, chapter_path)

		return next_url, chapter_path

	except urllib2.URLError, e:
		print ">>> Fail at "+target_url
		print ">>> Start cleaning"
		cleanup(dirname)

	except httplib.InvalidURL , e:
		print ">>> Fail at "+target_url
		print ">>> Start cleaning"
		cleanup(dirname)

if __name__ == '__main__':
	nexturl = sys.argv[1]
	while nexturl:
		nexturl = getit(sys.argv[2],nexturl)
