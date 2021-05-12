import os
import json
import shutil
import random
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
	parser.add_argument("-split_train_test", type=str2bool, default=False)
	parser.add_argument("-from_EmotionGIF", type=str2bool, default=False)
	parser.add_argument("-merge", type=str2bool, default=False)
	parser.add_argument("-for_lab1", type=str2bool, default=False)
	parser.add_argument("-split_context_GIF", type=str2bool, default=False)
	parser.add_argument("-remove_corrupted_mp4", type=str2bool, default=False)
	parser.add_argument("-merge10txt", type=str2bool, default=False)

	# other arguments
	parser.add_argument("-txt_file", type=str, default="reply.txt")
	parser.add_argument("-json_file", type=str, default="reply.json")
	parser.add_argument("-json_file_index", type=str, default="0")
	parser.add_argument("-date_dir", type=str, default="20210415")
	parser.add_argument("-result_path", type=str, default="/mnt/hdd1/joshchang/datasets/FakeNewsGIF")

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
	input_path = "{}/with_FakeNews/{}/{}".format(args.result_path, args.date_dir, args.txt_file)
	output_path = "{}/with_FakeNews/{}/{}".format(args.result_path, args.date_dir, args.json_file)

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
	def write_gold(output_path, new_dict, from_idx, to_idx):
		file_dir = output_path.split("/")[-2]
		print("Writing {} gold".format(file_dir))
	
		fw = open(output_path, "w", encoding="utf-8")
		for source_id, json_datas in tqdm(list(new_dict.items())[from_idx:to_idx]):
			for json_data in json_datas:
				if "GIF" == file_dir:
					if json_data["mp4"] != "":
						fw.write(json.dumps(json_data, ensure_ascii=False)) # for writing emojis
						fw.write("\n")
				elif "context" == file_dir:
					if json_data["mp4"] == "":
						fw.write(json.dumps(json_data, ensure_ascii=False)) # for writing emojis
						fw.write("\n")
				else:
					fw.write(json.dumps(json_data, ensure_ascii=False)) # for writing emojis
					fw.write("\n")

		fw.close()

	## 1. Read from all date_dir
	json_list = []

	date_dirs = ["20210217", "20210218", "20210301"]
	for date_dir in date_dirs:
		print("Reading all_labeled.json from {}".format(date_dir))

		input_path = "{}/reply/{}/all_labeled.json".format(args.result_path, date_dir)
		for line in tqdm(open(input_path, encoding="utf-8").readlines()):
			line = line.strip().rstrip()
			json_list.append(json.loads(line))
	#print(len(json_list))

	## 2. Build a dict with all idx as keys
	print()
	print("Processing")
	dict_list = {}
	for json_data in tqdm(json_list):
		if json_data["idx"] not in dict_list:
			dict_list[json_data["idx"]] = []
		dict_list[json_data["idx"]].append(json_data)

	new_dict = {}
	for index, (source_id, json_datas) in enumerate(tqdm(dict_list.items())):
		new_dict[source_id] = []
		# Sort by reply_id
		json_datas = sorted(json_datas, key=lambda s:s["reply_id"])
		for context_idx, json_data in enumerate(json_datas):
			new_data = {}
			sub_idx = json_data["text"].lower().find("#fakenews")
			sub_len = len("#fakenews")
			new_data["idx"] = index
			new_data["text"] = json_data["text"].replace(json_data["text"][sub_idx:sub_idx + sub_len], "")
			new_data["categories"] = json_data["categories"]
			new_data["context_idx"] = context_idx
			new_data["reply"] = json_data["reply"]
			new_data["mp4"] = json_data["mp4"].replace("None", "")
			new_data["label"] = "fake"
			
			new_dict[source_id].append(new_data)

	## 3. Write gif reply and text reply respectively
	print()
	#write_gold("{}/final/from_FakeNewsGIF/context/all_gold.json".format(args.result_path), new_dict, 0, len(list(new_dict.items())))
	#write_gold("{}/final/from_FakeNewsGIF/GIF/all_gold.json".format(args.result_path), new_dict, 0, len(list(new_dict.items())))
	write_gold("{}/final/from_FakeNewsGIF/all_gold.json".format(args.result_path), new_dict, 0, len(list(new_dict.items())))

def from_EmotionGIF(args):
	"""
	Arrange EmotionGIF dataset to FakeNewsGIF format.
	"""
	files = ["train_gold.json", "dev_gold.json", "eval_gold.json"]
	for file in files:
		input_path = "/mnt/hdd1/joshchang/datasets/EmotionGIF/{}".format(file)
		json_list = []
		for line in tqdm(open(input_path, encoding="utf-8").readlines()):
			line = line.strip().rstrip()
			json_list.append(json.loads(line))
		
		new_datas = []
		for json_data in tqdm(json_list):
			new_data = {}
			new_data["idx"] = json_data["idx"]
			new_data["text"] = json_data["text"]
			new_data["categories"] = json_data["categories"]
			new_data["context_idx"] = 0
			new_data["reply"] = json_data["reply"]
			new_data["mp4"] = json_data["mp4"]
			if "#fakenews" in json_data["text"].lower():
				sub_idx = json_data["text"].lower().find("#fakenews")
				sub_len = len("#fakenews")
				new_data["text"] = json_data["text"].replace(json_data["text"][sub_idx:sub_idx + sub_len], "")
				new_data["label"] = "fake"
			else:
				new_data["label"] = "real"
			new_datas.append(new_data)
		
		output_path = "/mnt/hdd1/joshchang/datasets/FakeNewsGIF/final/{}".format(file)
		fw = open(output_path, "w", encoding="utf-8")
		for new_data in tqdm(new_datas):
			#json.dump(new_data, fw)
			fw.write(json.dumps(new_data, ensure_ascii=False))
			fw.write("\n")
		fw.close()

def read_gold_to_dict(file_path, data_dict):
	for line in tqdm(open(file_path, encoding="utf-8").readlines()):
		line = line.strip().rstrip()
		json_data = json.loads(line)
		if json_data["idx"] not in data_dict:
			data_dict[json_data["idx"]] = []
		data_dict[json_data["idx"]].append(json_data)
	return data_dict

def merge(args):
	"""
	Merge dataset from EmotionGIF and FakeNewsGIF.
	EmotionGIF: All for training.
	FakeNewsGIF: 4000 source tweets for training.
	"""
	def write_list(path_out, tgt_list):
		fw = open(path_out, "w", encoding="utf-8")
		cnt = 0
		brk = False
		for merge_data_list in tqdm(tgt_list):
			for merge_data in merge_data_list:
				## for data that doesn't have categories (in FakeNews)
				if merge_data["mp4"] != "" and not merge_data["categories"]:
					merge_data["categories"] = ["others"]
					cnt += 1
				fw.write(json.dumps(merge_data, ensure_ascii=False))
				fw.write("\n")

		fw.close()
		print(cnt)

	path_emotion = "{}/final/from_EmotionGIF".format(args.result_path)
	path_fakenews = "{}/final/from_FakeNewsGIF".format(args.result_path)
	
	print("Reading from_EmotionGIF")
	emotion_dict = {}
	files = ["train_gold.json", "dev_gold.json", "eval_gold.json"]
	for file in files:
		file_path = "{}/{}".format(path_emotion, file)
		emotion_dict = read_gold_to_dict(file_path, emotion_dict)

	print(len(list(emotion_dict.items())))

	print()
	print("Reading from_FakeNewsGIF")
	fakenews_dict = {}
	file_path = "{}/new_all_gold(categories).json".format(path_fakenews)
	fakenews_dict = read_gold_to_dict(file_path, fakenews_dict)

	print(len(list(fakenews_dict.items())))

	print()
	print("Merging GIF training data of two datasets")
	## EmotionGIF: all for training
	## FakeNewsGIF: 4000 source tweets for training, the rest are for testing
	train_fake_emotion, test_fake = [], []
	for source_id, reply_list in tqdm(list(emotion_dict.items())):
		train_fake_emotion.append(reply_list)
	for source_id, reply_list in tqdm(list(fakenews_dict.items())[:4000]):
		train_fake_emotion.append(reply_list)
	for source_id, reply_list in tqdm(list(fakenews_dict.items())[4000:]):
		test_fake.append(reply_list)

	## shuffle data of two labels
	random.shuffle(train_fake_emotion)

	## give new index
	for new_idx, reply_list in enumerate(tqdm(train_fake_emotion)):
		for reply in reply_list:
			reply["idx"] = new_idx

	for new_idx, reply_list in enumerate(tqdm(test_fake)):
		for reply in reply_list:
			reply["idx"] = new_idx + len(train_fake_emotion)

	print(len(train_fake_emotion))
	print(len(test_fake))

	print()
	print("writing merge train / test file")
	path_merge = "{}/final/merge".format(args.result_path)
	train_path = "{}/train_gold(context+GIF).json".format(path_merge)
	test_path = "{}/test_gold(context+GIF).json".format(path_merge)

	write_list(train_path, train_fake_emotion)
	write_list(test_path, test_fake)

def split_context_GIF(args):
	"""
	Splitting context and GIF files from all.
	"""
	print("Reading all")
	path_merge = "{}/final/merge".format(args.result_path)
	all_path = "{}/train_gold(context+GIF).json".format(path_merge)

	all_dict = {}
	all_dict = read_gold_to_dict(all_path, all_dict)

	print()
	print("Writing merge training file")
	gif_path = "{}/gold/train_GIF_gold.json".format(path_merge)
	context_path = "{}/gold/train_context_gold.json".format(path_merge)

	fw_gif = open(gif_path, "w", encoding="utf-8")
	fw_context = open(context_path, "w", encoding="utf-8")
	for source_idx, merge_data_list in tqdm(list(all_dict.items())):
		for merge_data in merge_data_list:
			if merge_data["mp4"] == "":
				fw_context.write(json.dumps(merge_data, ensure_ascii=False))
				fw_context.write("\n")
			else:
				fw_gif.write(json.dumps(merge_data, ensure_ascii=False))
				fw_gif.write("\n")
	fw_gif.close()
	fw_context.close()

def for_lab1(args):
	"""
	Data for NLP Lab1. Only index and text needed.
	"""
	dirs = ["context", "GIF"]
	for dir in dirs:
		print()
		print("Reading {} from merge".format(dir))
		
		path_in = "{}/final/merge/{}/all_gold.json".format(args.result_path, dir)
		json_list = []
		for line in tqdm(open(path_in, encoding="utf-8").readlines()):
			line = line.strip().rstrip()
			json_data = json.loads(line)
			json_list.append(json_data)

		print()
		print("Processing for lab1 format, writing to lab1 directory")

		path_out = "{}/final/lab1/{}.json".format(args.result_path, dir)
		fw = open(path_out, "w", encoding="utf-8")
		for json_data in tqdm(json_list):
			del json_data["label"]
			del json_data["categories"]
			del json_data["context_idx"]
			del json_data["mp4"]
			fw.write(json.dumps(json_data, ensure_ascii=False))
			fw.write("\n")
		fw.close()

def remove_corrupted_mp4(args):
	"""
	Remove FakeNewsGIF tweets that contains mp4 file that can not be read by opencv.
	"""
	path_frames = "{}/final/merge/frames/FakeNewsGIF".format(args.result_path)
	path_mp4s = "{}/final/merge/mp4s/FakeNewsGIF".format(args.result_path)

	ok_mp4s, not_ok_mp4s = [], []
	all_frames = os.listdir(path_frames)
	for frame_file in tqdm(all_frames):
		if ".jpg" not in frame_file and frame_file[0] == ".":
			continue
		ok_mp4s.append("{}.mp4".format(frame_file.split(".")[0]))

	all_mp4s = os.listdir(path_mp4s)
	for mp4_file in tqdm(all_mp4s):
		if ".mp4" not in mp4_file and mp4_file[0] == ".":
			continue
		if mp4_file not in ok_mp4s:
			not_ok_mp4s.append(mp4_file)
	'''
	## read gif content, build dict
	not_ok_idx = []
	dict_list = {}
	path_all_tweets = "{}/final/from_FakeNewsGIF/all_gold.json".format(args.result_path)
	for line in tqdm(open(path_all_tweets, encoding="utf-8").readlines()):
		line = line.strip().rstrip()
		json_data = json.loads(line)
		if json_data["mp4"] in not_ok_mp4s:
			not_ok_idx.append(json_data["idx"])
		if json_data["idx"] not in dict_list:
			dict_list[json_data["idx"]] = []
		dict_list[json_data["idx"]].append(json_data)
	not_ok_idx = set(not_ok_idx)
	print(len(not_ok_idx))
	print(len(list(dict_list.items())))

	## give new idx and write
	new_list = []
	for idx, reply_list in tqdm(list(dict_list.items())):
		if idx in not_ok_idx:
			continue
		new_list.append(reply_list)
	print(len(new_list))

	new_all_tweets = "{}/final/from_FakeNewsGIF/new_all_gold.json".format(args.result_path)
	fw = open(new_all_tweets, "w", encoding="utf-8")
	for new_idx, reply_list in enumerate(tqdm(new_list)):
		for reply in reply_list:
			reply["idx"] = new_idx
			fw.write(json.dumps(reply, ensure_ascii=False))
			fw.write("\n")
	fw.close()
	'''
	for not_ok_mp4 in tqdm(not_ok_mp4s):
		os.remove("{}/final/merge/mp4s/FakeNewsGIF/{}".format(args.result_path, not_ok_mp4))

def merge10txt(args):
	"""
	This function merge txt files or (json files with one line one json object)
	"""

	all_json_objs, source_ids, gif_urls = [], [], []
	for idx in tqdm(range(10)):
		input_path = "{}/with_FakeNews/{}/gif_reply_{}.json".format(args.result_path, args.date_dir, idx)
		for line in open(input_path, encoding="utf-8"):
			line = line.strip().rstrip()
			json_obj = json.loads(line)
			all_json_objs.append(json_obj)
			source_ids.append(json_obj["idx"])
			if json_obj["gif_url"] != "":
				gif_urls.append(json_obj["gif_url"])
	#print(len(all_json_objs))
	print(len(set(source_ids)))
	print(len(gif_urls))

	output_path = "{}/with_FakeNews/{}/gif_reply.json".format(args.result_path, args.date_dir)

	fw = open(output_path, "w", encoding="utf-8")
	for json_obj in tqdm(all_json_objs):
		fw.write(json.dumps(json_obj, ensure_ascii=False))
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
	elif args.split_train_test:
		split_train_test(args)
	elif args.from_EmotionGIF:
		from_EmotionGIF(args)
	elif args.merge:
		merge(args)
	elif args.for_lab1:
		for_lab1(args)
	elif args.split_context_GIF:
		split_context_GIF(args)
	elif args.remove_corrupted_mp4:
		remove_corrupted_mp4(args)
	elif args.merge10txt:
		merge10txt(args)

if __name__ == "__main__":
	args = parse_args()
	setup_api_keys(args)
	main(args)