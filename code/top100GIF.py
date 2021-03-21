import time
import json
import argparse
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def str2bool(str):
	if str.lower() == "false":
		return False
	elif str.lower() == "true":
		return True

def parse_args():
	parser = argparse.ArgumentParser(description="Crawl twitter top 100 GIF.")

	# mode
	parser.add_argument("-install_chrome_driver", type=str2bool, default="False")
	parser.add_argument("-top100GIF", type=str2bool, default="False")
	
	# other arguments
	parser.add_argument("-chrome_path", type=str, default="/Users/joshua/.wdm/drivers/chromedriver/mac64/89.0.4389.23/chromedriver")
	parser.add_argument("-user_agent", type=str, default="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36")
	
	args=parser.parse_args()
	
	return args

def install_chrome_driver(args):
	driver = webdriver.Chrome(ChromeDriverManager().install())

def top100GIF(args):
	def create_driver(args):
		## 1. Define browser options
		chrome_options = Options()
		#chrome_options.add_argument("--headless") # Hide the browser window
		## 2. Reference the local Chromedriver instance
		chrome_path = args.chrome_path
		driver = webdriver.Chrome(executable_path=chrome_path, options=chrome_options)
		driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": args.user_agent})
	
		return driver

	def find_top100url(htmltext, url_list):
		soup = BeautifulSoup(driver.page_source, "html.parser")
		imgs = soup.find_all("img", src=True)
		
		for img in imgs:
			if ".gif" in img["src"] and img["src"] not in url_list:
				url_list.append(img["src"])

		return url_list

	tweet_url = "https://twitter.com/login"
	#email = "joshchang0111.eed06@nctu.edu.tw"
	username = "BMETk6SEW52suIU"
	password = "taylor0111"

	## create driver
	driver = create_driver(args)
	driver.get(tweet_url)
	time.sleep(1)

	## login to twitter
	driver.find_element_by_xpath("//*[@name='session[username_or_email]']").send_keys(username)
	driver.find_element_by_xpath("//*[@name='session[password]']").send_keys(password)
	driver.find_element_by_xpath("//*[@data-testid='LoginForm_Login_Button']").click()
	time.sleep(1)

	## click on "Add a GIF"
	driver.find_element_by_xpath("//*[@aria-label='Add a GIF']").click()
	time.sleep(1)

	categories = ["Agree", "Applause", "Awww", "Dance", "Deal with it", "Do not want", "Eww", "Eye roll", "Facepalm", "Fist bump", "Good luck", "Happy dance", "Hearts", "High five", "Hug", "IDK", "Kiss", "Mic drop", "No", "Oh snap", "Ok", "OMG", "Oops", "Please", "Popcorn", "Scared", "Seriously", "Shocked", "Shrug", "Sigh", "Slow clap", "SMH", "Sorry", "Thank you", "Thumbs down", "Thumbs up", "Want", "Win", "Wink", "Yawn", "Yes", "YOLO", "You got this"]
	categories_dict = {}
	for category in tqdm(categories):
		## click category
		driver.find_element_by_xpath("//*[text()='{}']".format(category)).click()
		time.sleep(1)

		top100url = []
		top100url = find_top100url(driver.page_source, top100url)

		idx = 1
		while True:
			while True:
				try:
					element = driver.find_element_by_xpath("//*[@id='layers']/div[2]/div/div/div/div/div/div[2]/div[2]/div/div[2]/div/div[2]/div/div[{}]".format(idx))
					break
				except selenium.common.exceptions.NoSuchElementException:
					time.sleep(1)
			driver.execute_script('arguments[0].scrollIntoView(true);', element)

			top100url = find_top100url(driver.page_source, top100url)
			idx += 1

			if len(top100url) >= 100:
				break

		categories_dict[category] = top100url

		## click "Back" button
		driver.find_element_by_xpath("//*[@aria-label='Back']".format(category)).click()
		time.sleep(1)

	driver.quit()

	## write to file
	json.dump(categories_dict, open("top100GIF.json", "w"), indent=4)

def main(args):
	if args.install_chrome_driver:
		install_chrome_driver(args)
	elif args.top100GIF:
		top100GIF(args)

if __name__ == "__main__":
	args = parse_args()
	main(args)