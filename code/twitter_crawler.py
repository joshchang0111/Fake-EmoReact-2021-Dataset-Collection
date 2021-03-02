import os
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
	parser.add_argument("-sample", type=str2bool, default=False) # for fetching replies
	parser.add_argument("-find_gif_tweets", type=str2bool, default=False)
	parser.add_argument("-rewrite_gif_tweets", type=str2bool, default=False)
	parser.add_argument("-fetch_gif", type=str2bool, default=False)
	parser.add_argument("-rewrite_data_format", type=str2bool, default=False)
	
	# other arguments
	parser.add_argument("-min_replies", type=int, default=5)
	parser.add_argument("-query", type=str, default="(#FakeNews)")
	parser.add_argument("-source_file", type=str, default="covid_5_replies.txt") # no_covid_5_replies.txt
	parser.add_argument("-reply_file", type=str, default="covid_reply.txt") # no_covid_reply.txt
	parser.add_argument("-sample_num", type=int, default=1000)
	parser.add_argument("-gif_reply_file", type=str, default="covid_gif_tweets.txt") # for finding gif
	parser.add_argument("-gif_dir", type=str, default="covid_gif_tweets") # for finding gif
	parser.add_argument("-result_path", type=str, default="/mnt/hdd1/joshchang/datasets/FakeNewsGIF/results")
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
	covid_exist_file    = "{}/source/covid_{}_replies.txt".format(args.result_path, args.min_replies)
	no_covid_exist_file = "{}/source/no_covid_{}_replies.txt".format(args.result_path, args.min_replies)
	covid_filename    = "{}/source/20210218/covid_{}_replies.txt".format(args.result_path, args.min_replies)
	no_covid_filename = "{}/source/20210218/no_covid_{}_replies.txt".format(args.result_path, args.min_replies)

	## Read and count existing tweet ids
	def read_existing(covid_exist_path, no_covid_exist_path, covid_exist_ids, no_covid_exist_ids):
		tweet_ids, _ = read_source_file(covid_exist_path)
		covid_exist_ids += tweet_ids
		tweet_ids, _ = read_source_file(no_covid_exist_path)
		no_covid_exist_ids += tweet_ids

		return covid_exist_ids,  no_covid_exist_ids

	print("Reading existing files (source id).")
	covid_exist_ids, no_covid_exist_ids = [], []
	covid_exist_ids, no_covid_exist_ids = read_existing(covid_exist_file, no_covid_exist_file, covid_exist_ids, no_covid_exist_ids)
	covid_exist_ids, no_covid_exist_ids = read_existing(covid_filename, no_covid_filename, covid_exist_ids, no_covid_exist_ids)

	print("Existing source (   covid): {}".format(len(covid_exist_ids)))
	print("Existing source (no_covid): {}".format(len(no_covid_exist_ids)))
	print("")

	## Fetching
	print("Fetching source tweets with min_replies: {}".format(args.min_replies))
	covid_filename    = "{}/source/20210301/covid_{}_replies.txt".format(args.result_path, args.min_replies)
	no_covid_filename = "{}/source/20210301/no_covid_{}_replies.txt".format(args.result_path, args.min_replies)
	covid_tweet_list, no_covid_tweet_list = [], []
	f_covid    = open(covid_filename, "w")
	f_no_covid = open(no_covid_filename, "w")
	
	iter = 0
	while True:
		try:
			for i, tweet in enumerate(sntwitter.TwitterSearchScraper(args.query).get_items()):
				if "covid" in tweet.content.lower():
					if tweet.id not in covid_tweet_list and str(tweet.id) not in covid_exist_ids: ###
						covid_tweet_list.append(tweet.id)
						f_covid.write("{}\t{}\t{}\n".format(tweet.id, tweet.username, tweet.content.replace("\n", "<newline>")))
				else:
					if tweet.id not in no_covid_tweet_list and str(tweet.id) not in no_covid_exist_ids: ###
						no_covid_tweet_list.append(tweet.id)
						f_no_covid.write("{}\t{}\t{}\n".format(tweet.id, tweet.username, tweet.content.replace("\n", "<newline>")))

			print("Iteration {}, covid: {}, no_covid: {}".format(iter, len(covid_tweet_list), len(no_covid_tweet_list)))
			iter += 1

		except KeyboardInterrupt:
			print("KeyboardInterrupt, stop fetching source.")
			break
	
	f_covid.close()
	f_no_covid.close()

def install_chrome_driver(args):
	## 0. Install ChromeDriver automatically
	driver = webdriver.Chrome(ChromeDriverManager().install())
	
def crawl_replies(args, driver, source_id, username):
	'''
	Web crawling on twitter page by selenium.
	Get replies of a specific source tweet.
	Source (examples):
		https://ithelp.ithome.com.tw/articles/10191165?fbclid=IwAR2biL_rIY78_u783eWI8zdaPHGqT9EQieQEwRD4X_Qurh1WaMeEy7tdBYc
		https://towardsdatascience.com/build-a-scalable-web-crawler-with-selenium-and-pyhton-9c0c23e3ebe5
	'''
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
	
	return reply_ids

def fetch_replies(args):
	def create_driver():
		## 1. Define browser options
		chrome_options = Options()
		chrome_options.add_argument("--headless") # Hide the browser window
		
		## 2. Reference the local Chromedriver instance
		chrome_path = r"/Users/joshua/.wdm/drivers/chromedriver/mac64/87.0.4280.88/chromedriver"
		driver = webdriver.Chrome(executable_path=chrome_path, options=chrome_options)

		return driver
	
	source_ids_file = "{}/source/{}".format(args.result_path, args.source_file)
	output_path = "{}/reply/{}".format(args.result_path, args.reply_file)

	print("Fetching replies from {}".format(source_ids_file))
	print("Writing to {}".format(output_path))

	f = open(source_ids_file, "r")
	lines = f.readlines()
	f.close()

	if args.sample:
		random.shuffle(lines)
		lines = lines[:args.sample_num]

	## create driver
	driver = create_driver()
	
	fw = open(output_path, "w")
	for line in tqdm(lines):
		line = line.strip().rstrip()
		source_id, username = line.split("\t")[0], line.split("\t")[1]
		reply_ids = crawl_replies(args, driver, source_id, username)

		fw.write("source\t{}\n".format(source_id))
		# write reply ids to file
		for reply_id in reply_ids:
			fw.write("reply\t{}\n".format(reply_id))
	fw.close()

	driver.quit()

def find_gif_tweets(args):
	'''
	Find gif tweets among all replies.
	'''
	api = setup_tweepy_api(args)

	input_path  = "{}/reply/20210218/{}".format(args.result_path, args.reply_file)
	output_path = "{}/reply/20210218/{}".format(args.result_path, args.gif_reply_file)

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
			#fw.write("source\t{}\n".format(id))
			continue

		try:
			reply_status = api.get_status(id, tweet_mode="extended")
			reply_type = reply_status.extended_entities["media"][0]["type"]
			if reply_type == "animated_gif":
				source_path = "{}/reply/20210218/{}/{}/reply".format(args.result_path, args.gif_dir, source_id)
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
	
	fw.close()

def rewrite_gif_tweets(args):
	for idx in range(5):
		input_path = "{}/reply/no_covid_{}_gif_reply.txt".format(args.result_path, idx)
		output_path = "{}/reply/no_covid_{}_gif_replyy.txt".format(args.result_path, idx)
	
		#input_path = "{}/FakeNews/reply/covid_gif_tweets.txt".format(args.result_path)
		#output_path = "{}/FakeNews/reply/covid_gif_reply.txt".format(args.result_path)
	
		f = open(input_path, "r")
		lines = f.readlines()
		f.close()
	
		tweet_dict = {}
		for line in tqdm(lines):
			line = line.strip().rstrip()
			type, id = line.split("\t")[0], line.split("\t")[1]
	
			if type == "source":
				source_id = id
				tweet_dict[source_id] = []
			else:
				reply_id = id
				tweet_dict[source_id].append(reply_id)
	
		fw = open(output_path, "w")
		for source, replies in tweet_dict.items():
			if len(replies) != 0:
				fw.write("source\t{}\n".format(source))
				for reply in replies:
					fw.write("reply\t{}\n".format(reply))
		fw.close()

def fetch_gif(args):
	'''
	Retrieve gif files (.mp4) from urls.
	'''
	gif_path = "{}/reply/{}".format(args.result_path, args.gif_dir)

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

def rewrite_data_format(args):
	## Fetch source json files and create reply directory.
	'''
	source_path = "{}/reply".format(args.result_path)
	input_path = "{}/{}".format(source_path, args.reply_file)
	
	f = open(input_path, "r")
	lines = f.readlines()
	f.close()

	source_list = []
	for line in lines:
		line = line.strip().rstrip()
		type, id = line.split("\t")[0], line.split("\t")[1]
		if type == "source":
			source_list.append(id)

	source_accessed, source_not_accessed = [], []
	#f1 = open("{}/source/{}".format(args.result_path, args.reply_file.replace("reply", "source")), "w")
	#f2 = open("{}/source/{}".format(args.result_path, args.reply_file.replace("reply", "source_not_accessed")), "w")
	api = setup_tweepy_api(args)
	for source_id in tqdm(source_list):
		reply_files = os.listdir("{}/{}/{}".format(source_path, args.gif_dir, source_id))
		if "reply" not in reply_files:
			os.makedirs("{}/{}/{}/reply".format(source_path, args.gif_dir, source_id), exist_ok=True)
			# move all reply json files to new reply directory
			for reply_file in reply_files:
				os.rename("{}/{}/{}/{}".format(source_path, args.gif_dir, source_id, reply_file), "{}/{}/{}/reply/{}".format(source_path, args.gif_dir, source_id, reply_file))
		
		## Remove source_id.json files
		#if "{}.json".format(source_id) in reply_files:
		#	os.remove("{}/{}/{}/{}.json".format(source_path, args.gif_dir, source_id, source_id))
		#	cnt += 1

		# write source text files
		try:
			source_status = api.get_status(source_id, tweet_mode="extended")._json
			source_accessed.append(source_id)
			#f1.write("{}\t{}\n".format(source_id, source_status["full_text"].replace("\n", "<newline>")))
			#f_json = open("{}/{}/{}/{}.json".format(source_path, args.gif_dir, source_id, source_id), "w")
			#f_json.write(json.dumps(source_status._json, indent=4))
			#f_json.close()
		except tweepy.error.TweepError as e:
			# these are the tweets that tweepy cannot access
			source_not_accessed.append(source_id)
			#f2.write("{}\n".format(source_id))

	print("accessed {}/{}".format(len(source_accessed), len(source_list)))
	print("Not accessed {}/{}".format(len(source_not_accessed), len(source_list)))

	#f1.close()
	#f2.close()
	'''

	'''
	## Move not accessed files
	input_path = "{}/source/no_covid_gif_source_not_accessed.txt".format(args.result_path)
	source_path = "{}/reply/{}".format(args.result_path, args.gif_dir)

	f = open(input_path, "r")
	lines = f.readlines()
	f.close()

	for line in lines:
		source_id = line.strip().rstrip()
		old_path = "{}/{}".format(source_path, source_id)
		new_path = "{}/reply/no_covid_not_accessed/{}".format(args.result_path, source_id)

		shutil.move(old_path, new_path)
	'''

	'''
	## Write source.txt to each source directory
	input_path = "{}/source/no_covid_gif_source.txt".format(args.result_path)

	f = open(input_path, "r")
	lines = f.readlines()
	f.close()

	for line in tqdm(lines):
		line = line.strip().rstrip()
		source_id, text = line.split("\t")[0], line.split("\t")[1]

		output_path = "{}/reply/no_covid_gif_tweets/{}/source.txt".format(args.result_path, source_id)
		fw = open(output_path, "w")
		fw.write(text.replace("<newline>", "\n"))
		fw.close()
	'''
	'''
	## Remove .mp4 files of covid_gif_reply
	input_path = "{}/source/covid_gif_source.txt".format(args.result_path)

	f = open(input_path, "r")
	lines = f.readlines()
	f.close()

	for line in tqdm(lines):
		line = line.strip().rstrip()
		source_id, text = line.split("\t")[0], line.split("\t")[1]

		source_path = "{}/reply/covid_gif_reply/{}/reply".format(args.result_path, source_id)
		files = os.listdir(source_path)

		for file in files:
			if ".mp4" in file:
				os.remove("{}/{}".format(source_path, file))
	'''

def main(args):
	if args.fetch_source:
		fetch_source(args)
	elif args.install_chrome_driver:
		install_chrome_driver(args)
	elif args.fetch_replies:
		fetch_replies(args)
	elif args.find_gif_tweets:
		find_gif_tweets(args)
	elif args.rewrite_gif_tweets:
		rewrite_gif_tweets(args)
	elif args.fetch_gif:
		fetch_gif(args)
	elif args.rewrite_data_format:
		rewrite_data_format(args)

if __name__ == "__main__":
	args = parse_args()
	setup_api_keys(args)
	main(args)
