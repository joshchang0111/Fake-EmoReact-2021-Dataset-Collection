import json
import shutil
import argparse
import configparser
from tqdm import tqdm

import tweepy

def str2bool(str):
	if str.lower() == "false":
		return False
	elif str.lower() == "true":
		return True

def parse_args():
	parser = argparse.ArgumentParser(description="Write data format as EmotionGIF.")

	# API keys (App: AgainstRumor)
	parser.add_argument("-app_name", type=str, default="AgainstRumor")
	parser.add_argument("-consumer_key", type=str, default="")
	parser.add_argument("-consumer_secret", type=str, default="")
	parser.add_argument("-access_token", type=str, default="")
	parser.add_argument("-access_token_secret", type=str, default="")

	# mode
	parser.add_argument("-txt2json", type=str2bool, default=False)
	parser.add_argument("-write10json", type=str2bool, default=False)
	parser.add_argument("-all2json", type=str2bool, default=False)
	parser.add_argument("-final_format", type=str2bool, default=False)

	# other arguments
	parser.add_argument("-txt_file", type=str, default="reply.txt")
	parser.add_argument("-json_file", type=str, default="reply.json")
	parser.add_argument("-json_file_index", type=str, default="0")
	parser.add_argument("-date_dir", type=str, default="20210301")
	parser.add_argument("-result_path", type=str, default="/mnt/hdd1/joshchang/datasets/FakeNewsGIF/")

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

def txt2json(args):
	'''
	From "reply.txt" to "reply.json", etc.
	'''
	input_path = "{}/reply/{}/{}".format(args.result_path, args.date_dir, args.txt_file)
	output_path = "{}/reply/{}/{}".format(args.result_path, args.date_dir, args.json_file)

	dict_list = []
	source_id = None
	source_list, reply_list = [], []
	for line in open(input_path, "r"):
		line = line.strip().rstrip()
		type, id = line.split("\t")[0], line.split("\t")[1]
		if type == "source":
			if not source_id == None:
				dict_list.append(conv_dict)
			reply_list = []
			source_id = id
			conv_dict = {}
		if type == "reply":
			reply_list.append(id)
			conv_dict[source_id] = reply_list
	dict_list.append(conv_dict)
	print(len(dict_list))

	with open(output_path, "w") as fw:
		json.dump(dict_list, fw, indent=4)

def write10json(args):
	'''
	Split data into 10 fold for multiprocessing.
	'''
	input_path = "{}/reply/{}/{}".format(args.result_path, args.date_dir, args.json_file)

	f_json = open(input_path)
	conv_dict_list = json.load(f_json)
	f_json.close()

	list0 = conv_dict_list[581*0:581*1]
	list1 = conv_dict_list[581*1:581*2]
	list2 = conv_dict_list[581*2:581*3]
	list3 = conv_dict_list[581*3:581*4]
	list4 = conv_dict_list[581*4:581*5]
	list5 = conv_dict_list[581*5:581*6]
	list6 = conv_dict_list[581*6:581*7]
	list7 = conv_dict_list[581*7:581*8]
	list8 = conv_dict_list[581*8:581*9]
	list9 = conv_dict_list[581*9:581*10]
	
	lists = [list0, list1, list2, list3, list4, list5, list6, list7, list8, list9]
	for idx, listi in enumerate(lists):
		output_path = "{}/reply/{}/10_split/{}.json".format(args.result_path, args.date_dir, idx)
		with open(output_path, "w") as fw:
			json.dump(listi, fw, indent=4)

def all2json(args):
	'''
	{"idx":32, "text":"Fell right under my trap", "reply":"Ouch!", "categories":['awww','yes','oops'], "mp4":"fe6ec1cd04cd009f3a5975e2d288ff82.mp4"}
	'''
	def get_src_txt_dict(src_txt_path):
		src_txt_dict = {}
		for line in open(src_txt_path, "r"):
			line = line.strip().rstrip()
			source_id, text = line.split("\t")[0], line.split("\t")[1]
			src_txt_dict[source_id] = text.replace("<newline>", " ").replace("\n", " ")
		return src_txt_dict

	def get_gif_reply_ids(gif_reply_path):
		gif_reply_ids = []

		f_json = open(gif_reply_path)
		dict_list = json.load(f_json)
		f_json.close()

		for dict in dict_list:
			for source_id, reply_list in dict.items():
				gif_reply_ids += reply_list

		return gif_reply_ids

	def get_reply_text(reply_id, api):
		reply_status = api.get_status(reply_id, tweet_mode="extended")
		return reply_status._json["full_text"]

	api = setup_tweepy_api(args)
	
	gif_reply_path = "{}/reply/{}/gif_reply.json".format(args.result_path, args.date_dir)
	src_txt_path   = "{}/reply/{}/gif_source.txt".format(args.result_path, args.date_dir)
	conv_dict_path = "{}/reply/{}/all_gif_reply.json".format(args.result_path, args.date_dir)
	#conv_dict_path = "{}/reply/{}/10_split/{}.json".format(args.result_path, args.date_dir, args.json_file_index)
	output_path    = "{}/reply/{}/labeled.json".format(args.result_path, args.date_dir)
	#output_path    = "{}/reply/{}/10_split/labeled_{}.json".format(args.result_path, args.date_dir, args.json_file_index)

	src_txt_dict = get_src_txt_dict(src_txt_path)
	gif_reply_ids = get_gif_reply_ids(gif_reply_path)

	f_json = open(conv_dict_path)
	conv_dict_list = json.load(f_json)
	f_json.close()
	
	result_list = []
	for conv_dict in tqdm(conv_dict_list):
		for source_id, reply_list in conv_dict.items():
			for reply_id in reply_list:
				json_data = {}
				json_data["idx"] = source_id
				json_data["text"] = src_txt_dict[source_id]
				json_data["categories"] = []

				try:
					json_data["reply"] = get_reply_text(reply_id, api)
					json_data["reply_id"] = reply_id
				except tweepy.error.TweepError as e:
					continue

				if reply_id in gif_reply_ids:
					json_data["mp4"] = "{}.mp4".format(reply_id)
				else:
					json_data["mp4"] = "None"

				result_list.append(json_data)
	
	with open(output_path, "w") as fw:
		json.dump(result_list, fw, indent=4)

def final_format(args):
	'''
	input_path = "{}/reply/{}/labeled.json".format(args.result_path, args.date_dir)
	output_path = "{}/reply/{}/labeled_new.json".format(args.result_path, args.date_dir)

	f = open(input_path, "r")
	dict_list = json.load(f)
	f.close()

	fw = open(output_path, "w")
	for dict in tqdm(dict_list):
		json.dump(dict, fw)
		fw.write("\n")
	fw.close()
	'''

	dict_list = []
	for idx in range(10):
		input_path = "{}/reply/{}/10_split/labeled_{}.json".format(args.result_path, args.date_dir, idx)

		f = open(input_path, "r")
		list = json.load(f)
		f.close()

		dict_list += list

	output_path = "{}/reply/{}/labeled.json".format(args.result_path, args.date_dir)
	fw = open(output_path, "w")
	for dict in tqdm(dict_list):
		json.dump(dict, fw)
		fw.write("\n")
	fw.close()
			
def main(args):
	if args.txt2json:
		txt2json(args)
	elif args.all2json:
		all2json(args)
	elif args.write10json:
		write10json(args)
	elif args.final_format:
		final_format(args)

if __name__ == "__main__":
	args = parse_args()
	setup_api_keys(args)
	main(args)