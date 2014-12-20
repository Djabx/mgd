#! /usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import BeautifulSoup
from urllib2  import urlopen
import mdl
import makepub
import json
import argparse
from module import zipfolder


class SerieParser(object):
	def __init__(self, url, out_dir):
		print "creating serie with:", url
		self.url = url
		self.out_dir = out_dir
		self.main_site = 'http://www.mangareader.net'
		self.main_html = urlopen(url)
		self.main_soup = BeautifulSoup(self.main_html.read())
		self.done_data = {}
		self.done_data['downloaded'] = []
		self.done_data['url_map'] = {}
		self.done_data['images'] = {}
		self.__load_done_data()

	def __save_done_data(self):
		done_file = os.path.join(self.out_dir, 'done.js')
		with open(done_file, 'w') as out:
			json.dump(self.done_data, out)

	def __load_done_data(self):
		done_file = os.path.join(self.out_dir, 'done.js')
		if os.path.exists(done_file):
			with open(done_file, 'r') as dh:
				self.done_data = json.load(dh)

	def _download_chapters(self):
		table_manga = self.main_soup.find('table', attrs={'id' : 'listing'})
		url_set = set()
		chapters = []
		for a in table_manga.find_all('a'):
			chapter_name = a.string
			chapter_url = self.main_site + a.get('href')
			chapter_dir = os.path.join(self.out_dir, chapter_name)

			url_set.add(chapter_url)
			chapters.append((chapter_url, chapter_name, chapter_dir))

		for chapter_url, chapter_name, chapter_dir in chapters:
#			if chapter_name in self.done_data['downloaded']:
#				# we do not have processed this dir...
#				yield chapter_dir, chapter_name
#				continue
			if not os.path.exists(chapter_dir):
				os.makedirs(chapter_dir)
			next_url = chapter_url
			while True:
				previous_url = next_url
				if previous_url in self.done_data['url_map'] and previous_url in self.done_data['images']:
					next_url = self.done_data['url_map'][previous_url]
				else:
					next_url, chapter_path = mdl.getit(chapter_dir, next_url)
					self.done_data['url_map'][previous_url] = next_url
					self.done_data['images'][previous_url] = chapter_path
				if not next_url or next_url in url_set:
					# the url does not exist or it's another chapter_dir
					self.done_data['downloaded'].append(chapter_name)
					self.__save_done_data()
					yield chapter_dir, chapter_name
					break

	def download_only(self):
		for x in self._download_chapters():
			pass

	def download_2_cbz(self):
		for chapter_dir, chapter_name in self._download_chapters():
			cbz_path = os.path.join(self.out_dir, chapter_name + '.cbz')
			if not os.path.exists(cbz_path):
				zipfolder.zipper(chapter_dir, cbz_path)


	def download_2_epub(self):
		for chapter_dir, chapter_name in self._download_chapters():
			epub_path = makepub.make_epub(chapter_dir, out_dir=self.out_dir)


def create_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument('url', help="the seri's url to open")
	parser.add_argument('out_dir', help="the output directory")
	group = parser.add_mutually_exclusive_group()
	group.add_argument('--cbz', action="store_true", help="if the output should be in cbz format")
	group.add_argument('--epub', action="store_true", help="if the output should be in epub format")
	group.add_argument('--dl', action="store_true", help="if only the download should be done")

	return parser


def main():
	parser = create_parser()
	


if __name__ == '__main__':
	options = parser.parse_args()
	s = SerieParser(options.url, options.out_dir)
	if options.cbz:
		s.download_2_cbz()
	elif options.epub:
		s.download_2_epub()
	elif options.dl:
		s.download_only()
