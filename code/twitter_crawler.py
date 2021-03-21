import os
import pdb
import time
import json
import random
import shutil
import argparse
import configparser
from tqdm import tqdm

# fetch source
import snscrape.modules.twitter as sntwitter

# fetch replies
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# find gif replies tweet id
import tweepy

# fetch gif file
import requests

def print_list(list):
	for element in list:
		print(element)

def str2bool(str):
	if str.lower() == "false":
		return False
	elif str.lower() == "true":
		return True

def parse_args():
	parser = argparse.ArgumentParser(description="Twitter Crawler.")
	# API keys (App: AgainstRumor)
	parser.add_argument("-app_name", type=str, default="AgainstRumor")
	parser.add_argument("-consumer_key", type=str, default="")
	parser.add_argument("-consumer_secret", type=str, default="")
	parser.add_argument("-access_token", type=str, default="")
	parser.add_argument("-access_token_secret", type=str, default="")
	
	# mode
	parser.add_argument("-fetch_source", type=str2bool, default=False)
	parser.add_argument("-install_chrome_driver", type=str2bool, default=False)
	parser.add_argument("-fetch_replies", type=str2bool, default=False)
	parser.add_argument("-find_gif_tweets", type=str2bool, default=False)
	parser.add_argument("-fetch_gif", type=str2bool, default=False)
	parser.add_argument("-get_gif_source", type=str2bool, default=False)
	parser.add_argument("-write_source_text", type=str2bool, default=False)
	
	# other arguments
	parser.add_argument("-min_replies", type=int, default=5)
	parser.add_argument("-query", type=str, default="(#FakeNews)")
	parser.add_argument("-source_file", type=str, default="source.txt")
	parser.add_argument("-gif_source_file", type=str, default="gif_source.txt")
	parser.add_argument("-reply_file", type=str, default="reply.txt")
	parser.add_argument("-gif_reply_file", type=str, default="gif_reply.txt") # for finding gif
	parser.add_argument("-gif_dir", type=str, default="gif_reply") # for finding gif
	parser.add_argument("-date_dir", type=str, default="20210318")
	parser.add_argument("-result_path", type=str, default="/mnt/hdd1/joshchang/datasets/FakeNewsGIF/")
	parser.add_argument("-user_agent", type=str, default="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36")
	
	args=parser.parse_args()
	
	return args

def setup_api_keys(args):
	config = configparser.ConfigParser()
	config.read("config.ini")

	args.consumer_key = config[args.app_name]["consumer_key"]
	args.consumer_secret = config[args.app_name]["consumer_secret"]
	args.access_token = config[args.app_name]["access_token"]
	args.access_token_secret = config[args.app_name]["access_token_secret"]

def setup_tweepy_api(args):
	auth = tweepy.OAuthHandler(args.consumer_key, args.consumer_secret)
	auth.set_access_token(args.access_token, args.access_token_secret)

	api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
	return api

def read_source_file(filename):
	f = open(filename, "r")
	lines = f.readlines()
	f.close()

	tweet_ids, usernames = [], []
	for line in tqdm(lines):
		line = line.strip().rstrip()
		tweet_id, username = line.split("\t")[0], line.split("\t")[1]
		tweet_ids.append(tweet_id)
		usernames.append(username)

	return tweet_ids, usernames

def read_reply_file(filename):
	f = open(filename, "r")
	lines = f.readlines()
	f.close()

	types, tweet_ids = [], []
	for line in lines:
		line = line.strip().rstrip()
		type, tweet_id = line.split("\t")[0], line.split("\t")[1]
		types.append(type)
		tweet_ids.append(tweet_id)

	return types, tweet_ids

def fetch_source(args):
	def read_existing():
		print("Reading existing ids")
		exist_ids = []
		date_dirs = ["20210217", "20210218", "20210301"]
		for date_dir in date_dirs:
			path_in = "{}/reply/{}/gif_source.txt".format(args.result_path, date_dir)
			for line in tqdm(open(path_in).readlines()):
				line = line.strip().rstrip()
				source_id = line.split("\t")[0]
				exist_ids.append(source_id)
		return exist_ids

	## Reading existing ids
	exist_ids = read_existing()

	## Fetching
	print("Fetching source tweets")
	print("query = {}".format(args.query))

	filename = "{}/reply/{}/source.txt".format(args.result_path, args.date_dir)
	tweet_list = []
	f = open(filename, "w")

	iter = 0
	while True:
		try:
			for i, tweet in enumerate(sntwitter.TwitterSearchScraper(args.query).get_items()):
				#pdb.set_trace()
				if tweet.id not in tweet_list and str(tweet.id) not in exist_ids:
					tweet_list.append(tweet.id)
					f.write("{}\t{}\t{}\n".format(tweet.id, tweet.username, tweet.content.replace("\n", "<newline>").replace("\n", "<newline>")))
					#if "#fakenews" not in tweet.content.lower():
					#	tweet_list.append(tweet.id)
					#	f.write("{}\t{}\t{}\n".format(tweet.id, tweet.username, tweet.content.replace("\n", "<newline>").replace("\n", "<newline>")))

			print("Iteration {}: {}".format(iter, len(tweet_list)))
			iter += 1

		except KeyboardInterrupt:
			print("KeyboardInterrupt, stop fetching source.")
			break
	
	f.close()

def install_chrome_driver(args):
	## 0. Install ChromeDriver automatically
	driver = webdriver.Chrome(ChromeDriverManager().install())
	
def crawl_replies(args, source_id, username):
	'''
	Web crawling on twitter page by selenium.
	Get replies of a specific source tweet.
	Source (examples):
		https://ithelp.ithome.com.tw/articles/10191165?fbclid=IwAR2biL_rIY78_u783eWI8zdaPHGqT9EQieQEwRD4X_Qurh1WaMeEy7tdBYc
		https://towardsdatascience.com/build-a-scalable-web-crawler-with-selenium-and-pyhton-9c0c23e3ebe5
	'''
	def create_driver():
		## 1. Define browser options
		chrome_options = Options()
		chrome_options.add_argument("--headless") # Hide the browser window
		## 2. Reference the local Chromedriver instance
		chrome_path = r"/Users/joshua/.wdm/drivers/chromedriver/mac64/88.0.4324.96/chromedriver"
		driver = webdriver.Chrome(executable_path=chrome_path, options=chrome_options)
		driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": args.user_agent})

		return driver

	def scroll_to_bottom(driver, reply_ids):
		SCROLL_PAUSE_TIME = 0.5
		# Get scroll height
		last_height = driver.execute_script("return document.body.scrollHeight")
		while True:
			# Scroll down to bottom
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			# Wait to load page
			time.sleep(SCROLL_PAUSE_TIME)
			find_reply_id_from_html(driver.page_source, reply_ids)
			# Calculate new scroll height and compare with last scroll height
			new_height = driver.execute_script("return document.body.scrollHeight")
			if new_height == last_height:
				break
			last_height = new_height
		return driver

	def tryclick(driver, xpath, count=0):
		try:
			#elem = driver.find_element_by_css_selector(selector)
			elem = driver.find_element_by_xpath(xpath)
			elem.click()
		except:
			time.sleep(2)
			count += 1
			if count < 2:
				tryclick(driver, xpath, count)
			#else:
			#	print("cannot locate element {}".format(xpath))

	def find_reply_id_from_html(htmltext, reply_ids):
		soup = BeautifulSoup(htmltext, "html.parser")
		a_tags = soup.find_all("a", href=True)
		for a in a_tags:
			if a.text and "status" in a["href"] and source_id not in a["href"]:
				tweet_id = a["href"].split("/")[-1]
				if tweet_id not in reply_ids and len(tweet_id) == len(source_id):
					reply_ids.append(tweet_id)
		return reply_ids

	## create driver
	driver = create_driver()
	tweet_url = "https://twitter.com/{}/status/{}".format(username, source_id)

	## Run the Webdriver, save page and quit browser
	reply_ids = []

	## 1 get source html and wait for javascript element
	driver.get(tweet_url)
	time.sleep(3) # wait for javascript element
	reply_ids = find_reply_id_from_html(driver.page_source, reply_ids)
	driver = scroll_to_bottom(driver, reply_ids)

	## 2 Click "Show more replies" button
	tryclick(driver, "//*[contains(text(), 'Show more replies')]")
	time.sleep(3)
	reply_ids = find_reply_id_from_html(driver.page_source, reply_ids)
	driver = scroll_to_bottom(driver, reply_ids)

	## 3 Click "Show" button
	tryclick(driver, "//*[text()='Show']")
	time.sleep(3)
	reply_ids = find_reply_id_from_html(driver.page_source, reply_ids)
	driver = scroll_to_bottom(driver, reply_ids)

	driver.quit()
	
	return reply_ids

def fetch_replies(args):
	source_ids_file = "{}/FakeNews/source/20210301/{}".format(args.result_path, args.source_file)
	output_path = "{}/FakeNews/reply/20210301/{}".format(args.result_path, args.reply_file)

	print("Fetching replies from {}".format(source_ids_file))
	print("Writing to {}".format(output_path))

	f = open(source_ids_file, "r")
	lines = f.readlines()
	f.close()

	## iterate through all source ids and crawl its replies
	fw = open(output_path, "w")
	for line in tqdm(lines):
		line = line.strip().rstrip()
		source_id, username = line.split("\t")[0], line.split("\t")[1]

		#reply_ids = crawl_replies(args, driver, source_id, username)
		reply_ids = crawl_replies(args, source_id, username)

		fw.write("source\t{}\n".format(source_id))
		# write reply ids to file
		for reply_id in reply_ids:
			fw.write("reply\t{}\n".format(reply_id))
	fw.close()

def find_gif_tweets(args):
	'''
	Find gif tweets among all replies.
	'''
	api = setup_tweepy_api(args)

	input_path  = "{}/reply/20210301/{}".format(args.result_path, args.reply_file)
	output_path = "{}/reply/20210301/{}".format(args.result_path, args.gif_reply_file)

	print("Finding GIF tweets from {}".format(input_path))

	# read source and reply ids
	f = open(input_path, "r")
	lines = f.readlines()
	f.close()

	fw = open(output_path, "w")
	for line in tqdm(lines):
		line = line.strip().rstrip()
		type, id = line.split("\t")[0], line.split("\t")[1]

		if type == "source":
			source_id = id
			continue

		try:
			reply_status = api.get_status(id, tweet_mode="extended")
			reply_type = reply_status.extended_entities["media"][0]["type"]
			if reply_type == "animated_gif":
				source_path = "{}/reply/20210301/{}/{}/reply".format(args.result_path, args.gif_dir, source_id)
				# write to file
				if not os.path.exists(source_path):
					fw.write("source\t{}\n".format(source_id))
				os.makedirs(source_path, exist_ok=True)
				fw.write("reply\t{}\n".format(id))
				# write json file
				f_json = open("{}/{}.json".format(source_path, id), "w")
				f_json.write(json.dumps(reply_status._json, indent=4))
				f_json.close()
		except (AttributeError, tweepy.error.TweepError) as e:
			continue
		except KeyboardInterrupt as e:
			break
	fw.close()

def fetch_gif(args):
	'''
	Retrieve gif files (.mp4) from urls.
	'''
	gif_path = "{}/reply/{}/{}".format(args.result_path, args.date_dir, args.gif_dir)

	source_ids = os.listdir(gif_path)
	for source_id in source_ids:
		if not os.path.isdir("{}/{}".format(gif_path, source_id)):
			source_ids.remove(source_id)

	for source_id in tqdm(source_ids):
		reply_path = "{}/{}/reply".format(gif_path, source_id)
		files = os.listdir(reply_path)

		json_files, mp4_files = [], []
		for file in files:
			# remove files not named "source_id.json" or "source_id.mp4"
			if len(file.split(".")) != 2 or file[0] == "." or file[0] == "_":
				continue
			# check number of .mp4 and .json
			if ".mp4" in file:
				mp4_files.append(file)
			elif ".json" in file:
				json_files.append(file)

		if len(mp4_files) == len(json_files):
			continue

		for json_file in json_files:
			# read json
			json_path = "{}/{}".format(reply_path, json_file)
			f_json = open(json_path, "r")
			tweet_json = json.load(f_json)
			# fetch gif
			gif_url = tweet_json["extended_entities"]["media"][0]["video_info"]["variants"][0]["url"]
			r = requests.get(gif_url, allow_redirects=True)
			open("{}/{}.mp4".format(reply_path, json_file.split(".")[0]), "wb").write(r.content)

def get_gif_source(args):
	source_path = "{}/reply/{}/gif_reply".format(args.result_path, args.date_dir)
	dirs = os.listdir(source_path)

	gif_source_ids = []
	for dir in dirs:
		if os.path.isdir("{}/{}".format(source_path, dir)) and dir[0] != ".":
			gif_source_ids.append(dir)

	gif_reply_ids = []
	for gif_source_id in gif_source_ids:
		reply_path = "{}/{}/reply".format(source_path, gif_source_id)
		reply_files = os.listdir(reply_path)

		for reply_file in reply_files:
			if ".json" in reply_file and reply_file[0] != ".":
				gif_reply_ids.append(reply_file)
				reply_id = reply_file.split(".")[0]

	print(len(gif_source_ids))
	print(len(gif_reply_ids))

	input_path = "{}/source/{}/{}".format(args.result_path, args.date_dir, args.source_file)
	fw = open("{}/source/{}/{}".format(args.result_path, args.date_dir, args.gif_source_file), "w")
	for line in open(input_path, "r"):
		line = line.strip().rstrip()
		source_id, username, text = line.split("\t")[0], line.split("\t")[1], line.split("\t")[2]
		if source_id in gif_source_ids:
			fw.write("{}\t{}\n".format(source_id, text))
	fw.close()

def write_source_text(args):
	## Write source.txt to each source directory
	input_path = "{}/source/20210218/gif_source.txt".format(args.result_path)

	f = open(input_path, "r")
	lines = f.readlines()
	f.close()

	for line in tqdm(lines):
		line = line.strip().rstrip()
		source_id, text = line.split("\t")[0], line.split("\t")[1]

		output_path = "{}/reply/20210218/gif_reply/{}/source.txt".format(args.result_path, source_id)
		fw = open(output_path, "w")
		fw.write(text.replace("<newline>", "\n"))
		fw.close()

def main(args):
	if args.fetch_source:
		fetch_source(args)
	elif args.install_chrome_driver:
		install_chrome_driver(args)
	elif args.fetch_replies:
		fetch_replies(args)
	elif args.find_gif_tweets:
		find_gif_tweets(args)
	elif args.fetch_gif:
		fetch_gif(args)
	elif args.get_gif_source:
		get_gif_source(args)
	elif args.write_source_text:
		write_source_text(args)

if __name__ == "__main__":
	args = parse_args()
	setup_api_keys(args)
	main(args)
