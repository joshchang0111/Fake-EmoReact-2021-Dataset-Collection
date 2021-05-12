import os
import json
import shutil
import random
import argparse
from tqdm import tqdm

def str2bool(str):
	if str.lower() == "false":
		return False
	elif str.lower() == "true":
		return True

def parse_args():
	parser = argparse.ArgumentParser(description="Statistics of FakeNewsGIF")

	# mode
	parser.add_argument("-total_count", type=str2bool, default=False)
	parser.add_argument("-gif_source_total_reply", type=str2bool, default=False)
	parser.add_argument("-count_by_txt", type=str2bool, default=False)
	parser.add_argument("-count_miss_gif", type=str2bool, default=False)
	parser.add_argument("-insert_missing", type=str2bool, default=False)
	parser.add_argument("-read_final_and_test", type=str2bool, default=False)
	parser.add_argument("-cnt_existing", type=str2bool, default=False)
	parser.add_argument("-detect_source", type=str2bool, default=False)
	parser.add_argument("-check", type=str2bool, default=False)
	parser.add_argument("-package2", type=str2bool, default=False)
	parser.add_argument("-count_package2", type=str2bool, default=False)
	parser.add_argument("-phase1_from_package2", type=str2bool, default=False)

	# other arguments
	parser.add_argument("-result_path", type=str, default="/mnt/hdd1/joshchang/datasets/FakeNewsGIF")
	parser.add_argument("-date_dir", type=str, default="20210301")

	args=parser.parse_args()
	
	return args

def count(input_path, source_list, reply_list):
	f = open(input_path, "r")
	lines = f.readlines()
	f.close()

	for line in lines:
		line = line.strip().rstrip()
		type, id = line.split("\t")[0], line.split("\t")[1]
		if type == "source":
			source_list.append(id)
		if type == "reply":
			reply_list.append(id)

	return source_list, reply_list

def total_count(args):
	'''
	Calculate total amount of source and replies.
	'''
	'''
	### by .txt
	source_list, reply_list = [], []
	input_path = "{}/reply/{}/gif_reply.txt".format(args.result_path, args.date_dir)
	source_list, reply_list = count(input_path, source_list, reply_list)

	print("# of source (gif): {}".format(len(source_list)))
	print("# of reply  (gif): {}".format(len(reply_list)))
	'''

	### by .json
	input_path = "{}/reply/{}/gif_reply.json".format(args.result_path, args.date_dir)
	
	f_json = open(input_path)
	conv_dict_list = json.load(f_json)
	f_json.close()

	reply_list = []
	for conv_dict in conv_dict_list:
		for source_id, replies in conv_dict.items():
			reply_list += replies

	print("# of source (gif): {}".format(len(conv_dict_list)))
	print("# of reply  (gif): {}".format(len(reply_list)))

def gif_source_total_reply(args):
	source_list, reply_list = [], []
	input_path = "{}/reply/{}/gif_reply.txt".format(args.result_path, args.date_dir)
	source_list, reply_list = count(input_path, source_list, reply_list)

	flag = 0
	reply_list = []
	input_path = "{}/reply/{}/reply.txt".format(args.result_path, args.date_dir)
	output_path = "{}/reply/{}/all_gif_reply.txt".format(args.result_path, args.date_dir)
	fw = open(output_path, "w")
	for line in open(input_path, "r"):
		line = line.strip().rstrip()
		type, id = line.split("\t")[0], line.split("\t")[1]
		if type == "source":
			if id in source_list:
				flag = 1
				fw.write("source\t{}\n".format(id))
			else:
				flag = 0
		if type == "reply" and flag == 1:
			reply_list.append(id)
			fw.write("reply\t{}\n".format(id))

	print("# of source (gif): {}".format(len(source_list)))
	print("# of reply  (all): {}".format(len(reply_list)))

def count_by_txt(args):
	'''
	2 categories: whether the source text contains keywords or not.
	Calculate amount of source of each category.
	'''
	def has_key(text, keywords):
		for keyword in keywords:
			if keyword in text.lower():
				return True

		return False

	keywords = ["covid", "coronavirus", "corona", "pandemic", "vaccine", "quarantine", "pneumonia"]
	num_key = len(keywords)

	for num_key in range(len(keywords)):
		num_key += 1
		src_with_key, src_wo_key = [], []
		input_path = "{}/source/{}/gif_source.txt".format(args.result_path, args.date_dir)
		for line in open(input_path, "r").readlines():
			line = line.strip().rstrip()
			source_id, text = line.split("\t")[0], line.split("\t")[1]
			
			if has_key(text, keywords[:num_key]):
				src_with_key.append(source_id)
			elif not has_key(text, keywords[:num_key]):
				src_wo_key.append(source_id)

		print("======================")
		print("-- with    keywords --")
		print("# of source (gif): {}".format(len(src_with_key)))
		print("-- without keywords --")
		print("# of source (gif): {}".format(len(src_wo_key)))

def count_miss_gif(args):
	## get gif reply from "gif_reply.json"
	input_path = "{}/reply/{}/gif_reply.json".format(args.result_path, args.date_dir)
	
	f_json = open(input_path, "r")
	conv_dict_list = json.load(f_json)
	f_json.close()

	reply_list = []
	for conv_dict in conv_dict_list:
		for source_id, replies in conv_dict.items():
			for reply in replies:
				reply_list.append([source_id, reply])

	## get replies from "labeled.json"
	labeled_reply = []
	input_path = "{}/reply/{}/labeled.json".format(args.result_path, args.date_dir)
	for line in tqdm(open(input_path, "r").readlines()):
		line = line.strip().rstrip()
		data = json.loads(line)

		labeled_reply.append(data["reply_id"])

	## count unlabeled gif reply
	unlabeled_gif_reply = []
	for source, reply in tqdm(reply_list):
		if reply not in labeled_reply:
			unlabeled_gif_reply.append([source, reply])

	print("Unlabeled GIF reply: {}".format(len(unlabeled_gif_reply)))

	## get source dict
	source_dict = {}
	for line in open("{}/reply/{}/gif_source.txt".format(args.result_path, args.date_dir)):
		line = line.strip().rstrip()
		id, text = line.split("\t")[0], line.split("\t")[1]
		source_dict[id] = text

	fw = open("{}/reply/{}/labeled_new.json".format(args.result_path, args.date_dir), "w")
	for source, gif_reply in unlabeled_gif_reply:
		f_json = open("{}/reply/{}/gif_reply/{}/reply/{}.json".format(args.result_path, args.date_dir, source, gif_reply))
		data = json.load(f_json)
		f_json.close()
		dict = {}
		dict["idx"] = source
		dict["text"] = source_dict[source]
		dict["categories"] = []
		dict["reply"] = data["full_text"]
		dict["reply_id"] = gif_reply
		dict["mp4"] = "{}.mp4".format(gif_reply)
		json.dump(dict, fw)
		fw.write("\n")
	fw.close()

def insert_missing(args):
	missing_datas = []
	input_path = "{}/reply/{}/labeled_new.json".format(args.result_path, args.date_dir)
	for line in tqdm(open(input_path, "r").readlines()):
		line = line.strip().rstrip()
		data = json.loads(line)
		missing_datas.append(data)

	datas = []
	input_path = "{}/reply/{}/labeled.json".format(args.result_path, args.date_dir)
	for line in tqdm(open(input_path, "r").readlines()):
		line = line.strip().rstrip()
		data = json.loads(line)
		datas.append(data)

	print("Before inserting: {}".format(len(datas)))

	for missing_data in tqdm(missing_datas):
		for index, data in enumerate(datas):
			if missing_data["idx"] == data["idx"]:
				datas.insert(index, missing_data)
				break

	print("After inserting: {}".format(len(datas)))

	fw = open("{}/reply/{}/all_labeled.json".format(args.result_path, args.date_dir), "w")
	for data in datas:
		json.dump(data, fw)
		fw.write("\n")
	fw.close()

def read_final_and_test(args):
	def read_gold(input_path):
		gold_list = []
		for line in tqdm(open(input_path, encoding="utf-8").readlines()):
			line = line.strip().rstrip()
			json_obj = json.loads(line)
			gold_list.append(json_obj)
		return gold_list

	## three target file paths
	gif_gold_path = "{}/final/merge/gold/train_GIF_gold.json".format(args.result_path)
	context_gold_path = "{}/final/merge/gold/train_context_gold.json".format(args.result_path)
	train_mp4s_path = "{}/final/merge/mp4s/train_mp4s".format(args.result_path)

	gif_gold_list = read_gold(gif_gold_path)
	context_gold_list = read_gold(context_gold_path)

	mp4_files = []
	train_mp4s = os.listdir(train_mp4s_path)
	for train_mp4 in tqdm(train_mp4s):
		if train_mp4[0] == "." and ".mp4" not in train_mp4:
			continue
		mp4_files.append(train_mp4)
	#print(len(mp4_files))

	## statistics
	print("Statistics on gif_gold")
	total_real, total_fake = [], []
	for gif_gold in tqdm(gif_gold_list):
		if gif_gold["label"] == "real":
			total_real.append(gif_gold)
		elif gif_gold["label"] == "fake":
			total_fake.append(gif_gold)
	print("real: {}".format(len(total_real)))
	print("fake: {}".format(len(total_fake)))

def cnt_existing(args):
	## Read all existing source ids
	exist_ids = []
	date_dirs = ["20210217", "20210218", "20210301"]
	for date_dir in date_dirs:
		for line in tqdm(open("{}/with_FakeNews/{}/gif_source.txt".format(args.result_path, date_dir), encoding="utf-8").readlines()):
			line = line.strip().rstrip()
			source_id = line.split("\t")[0]
			exist_ids.append(source_id)
	print(len(set(exist_ids)))
	print(type(exist_ids[0]))

	## Read from 20210318
	duplicate = []
	path_mp4s = "{}/with_FakeNews/20210318/gif_reply.json".format(args.result_path)
	for line in tqdm(open(path_mp4s, encoding="utf-8").readlines()):
		line = line.strip().rstrip()
		json_obj = json.loads(line)
		if json_obj["idx"] in exist_ids:
			duplicate.append(json_obj["idx"])
	print(type(json_obj["idx"]))

	print("Duplicate in 20210318: {}".format(len(duplicate)))

def detect_source(args):
	input_path = "{}/with_FakeNews/20210415/source.txt".format(args.result_path)
	for idx, line in enumerate(tqdm(open(input_path, encoding="utf-8").readlines())):
		line = line.strip().rstrip()
		if len(line.split("\t")) < 3:
			print(idx)

def check(args):
	"""
	20210429
	Check if gif files of testing set from package1 is in the training data.
	Rearrange train_m4ps and test_mp4s (Update train_mp4s).
	"""
	test_gifs = []
	path_in = "{}/package1/merge/test_gold(context+GIF).json".format(args.result_path)
	for line in tqdm(open(path_in).readlines()):
		line = line.strip().rstrip()
		json_obj = json.loads(line)
		if json_obj["mp4"] != "":
			test_gifs.append(json_obj["mp4"])

	train_gifs = []
	path_in = "{}/package1/merge/gold/train_GIF_gold.json".format(args.result_path)
	for line in tqdm(open(path_in).readlines()):
		line = line.strip().rstrip()
		json_obj = json.loads(line)
		if json_obj["mp4"] != "":
			train_gifs.append(json_obj["mp4"])

	print(len(set(test_gifs)))
	print(len(set(train_gifs)))

	path_FakeNewsGIF_mp4s = "{}/package1/merge/mp4s/FakeNewsGIF".format(args.result_path)
	path_EmotionGIF_mp4s = "{}/package1/merge/mp4s/EmotionGIF".format(args.result_path)
	FakeNewsGIF_mp4s = os.listdir(path_FakeNewsGIF_mp4s)
	EmotionGIF_mp4s = os.listdir(path_EmotionGIF_mp4s)

	## move EmotionGIF mp4s to train_mp4s
	for EmotionGIF_mp4 in tqdm(EmotionGIF_mp4s):
		if EmotionGIF_mp4[0] == "." or ".mp4" not in EmotionGIF_mp4:
			continue
		file_to_move = "{}/{}".format(path_EmotionGIF_mp4s, EmotionGIF_mp4)
		dest_to_move = "{}/package1/merge/mp4s/train_mp4s/{}".format(args.result_path, EmotionGIF_mp4)
		shutil.move(file_to_move, dest_to_move)

	## move FakeNewsGIF mp4s to train_mp4s
	for FakeNewsGIF_mp4 in tqdm(FakeNewsGIF_mp4s):
		if FakeNewsGIF_mp4[0] == "." or ".mp4" not in FakeNewsGIF_mp4:
			continue
		if FakeNewsGIF_mp4 in train_gifs:
			file_to_move = "{}/{}".format(path_FakeNewsGIF_mp4s, FakeNewsGIF_mp4)
			dest_to_move = "{}/package1/merge/mp4s/train_mp4s/{}".format(args.result_path, FakeNewsGIF_mp4)
			shutil.move(file_to_move, dest_to_move)

def package2(args):
	def stat_file(input_path, GIF_path):
		GIFs = os.listdir(GIF_path)
		## cnt source, cnt gifs
		source_ids, gif_files = [], []
		for line in tqdm(open(input_path, encoding="utf-8").readlines()):
			line = line.strip().rstrip()
			json_obj = json.loads(line)
			source_ids.append(json_obj["idx"])
			if "gif_url" not in json_obj:
				if json_obj["mp4"] != "":
					gif_files.append(json_obj["mp4"])
			else:
				if json_obj["gif_url"] != "":
					gif_files.append(json_obj["gif_url"])
					#if json_obj["gif_url"].split("/")[-1] not in GIFs and "{}.mp4".format(json_obj["reply_id"]) not in GIFs:
					#	print(json_obj["gif_url"])

		print("Statistics of {}".format(input_path.split("/")[-2]))
		print("# of source_ids: {}".format(len(set(source_ids))))
		print("# of GIFs: {}".format(len(set(gif_files))))

	def update_20210318_mp4s_name():
		GIF_path = "{}/with_FakeNews/20210318/mp4s".format(args.result_path)
		GIFs = os.listdir(GIF_path)

		input_path = "{}/with_FakeNews/20210318/gif_reply.json".format(args.result_path)
		for line in tqdm(open(input_path, encoding="utf-8").readlines()):
			line = line.strip().rstrip()
			json_obj = json.loads(line)

			if json_obj["gif_url"] != "":
				mp4_name = "{}.mp4".format(json_obj["reply_id"])
				new_mp4_name = json_obj["gif_url"].split("/")[-1]
				if mp4_name not in GIFs:
					continue
				os.rename("{}/{}".format(GIF_path, mp4_name), "{}/{}".format(GIF_path, new_mp4_name))
				#if mp4_name not in GIFs:
				#	print(mp4_name)

	def fill_categories():
		input_paths = [
			"{}/with_FakeNews/20210318/gif_reply.json".format(args.result_path)
			#"{}/with_FakeNews/20210413/gif_reply.json".format(args.result_path), 
			#"{}/with_FakeNews/20210415/gif_reply.json".format(args.result_path),
			#"{}/wo_FakeNews/20210330/gif_reply.json".format(args.result_path)
		]
		categories_label_paths = [
			"{}/with_FakeNews/20210318/mp4s_labels.json".format(args.result_path), 
			#"{}/with_FakeNews/20210413/mp4s_labels.json".format(args.result_path), 
			#"{}/with_FakeNews/20210415/mp4s_labels.json".format(args.result_path), 
			#"{}/wo_FakeNews/20210330/mp4s_labels.json".format(args.result_path) 
		]
		label2_paths = [
			"",
			#"{}/with_FakeNews/20210413/unlabeled_mp4s_labels.json".format(args.result_path), 
			#"{}/with_FakeNews/20210415/unlabeled_mp4s_labels.json".format(args.result_path), 
			#"{}/wo_FakeNews/20210330/unlabeled_mp4s_labels.json".format(args.result_path) 
		]

		for input_path, categories_label_path, label2_path in zip(input_paths, categories_label_paths, label2_paths):
			print(input_path)
			label1 = json.load(open(categories_label_path))
			label2 = None
			if label2_path != "":
				label2 = json.load(open(label2_path))

			outputs = []
			for line in tqdm(open(input_path, encoding="utf-8").readlines()):
				line = line.strip().rstrip()
				json_obj = json.loads(line)
				if json_obj["gif_url"] != "":
					#if json_obj["gif_url"].split("/")[-1].replace("mp4", "jpg") not in label1:
					#	continue
					#json_obj["categories"] = label1[json_obj["gif_url"].split("/")[-1].replace("mp4", "jpg")]
					json_obj["categories"] = label1["{}.jpg".format(json_obj["reply_id"])]
					if label2 != None:
						if json_obj["gif_url"].split("/")[-1] in label2:
							json_obj["categories"] = label2[json_obj["gif_url"].split("/")[-1].replace("mp4", "jpg")]
					if json_obj["categories"] == []:
						json_obj["categories"] = ["others"]
				outputs.append(json_obj)

			output_path = input_path.replace("gif_reply", "gif_reply_new")
			fw = open(output_path, "w", encoding="utf-8")
			for output in tqdm(outputs):
				fw.write(json.dumps(output, ensure_ascii=False))
				fw.write("\n")
			fw.close()

	def to_gold(input_path, label, output_path):
		## Gold format: idx, text, categories, context_idx, reply, mp4, label
		## Read to tree dict
		tree_dict = {}
		for line in tqdm(open(input_path, encoding="utf-8").readlines()):
			line = line.strip().rstrip()
			json_obj = json.loads(line)
			if json_obj["idx"] not in tree_dict:
				reply_list = []
				tree_dict[json_obj["idx"]] = reply_list
			#else:
			tree_dict[json_obj["idx"]].append(json_obj)

		final_gold = []
		for source_id, reply_list in tqdm(list(tree_dict.items())):
			if "reply_id" in reply_list[0]:
				reply_list = sorted(reply_list, key=lambda s:s["reply_id"])
			for i, json_obj in enumerate(reply_list):
				new_json_obj = {}
				
				new_json_obj["idx"] = source_id
				sub_idx = json_obj["text"].lower().find("#fakenews")
				sub_len = len("#fakenews")
				new_json_obj["text"] = json_obj["text"].replace(json_obj["text"][sub_idx:sub_idx + sub_len], "")
				new_json_obj["categories"] = json_obj["categories"]
				new_json_obj["context_idx"] = i
				new_json_obj["reply"] = json_obj["reply"]
				if "gif_url" not in json_obj:
					new_json_obj["mp4"] = json_obj["mp4"]
				else:
					if json_obj["gif_url"] != "":
						new_json_obj["mp4"] = json_obj["gif_url"].split("/")[-1]
					else:
						new_json_obj["mp4"] = ""
				new_json_obj["label"] = label

				final_gold.append(new_json_obj)

		fw = open(output_path, "w", encoding="utf-8")
		for gold in tqdm(final_gold):
			fw.write(json.dumps(gold, ensure_ascii=False))
			fw.write("\n")
		fw.close()
	
	#update_20210318_mp4s_name()

	#fill_categories()

	## Statistics
	path_with_FakeNews = "{}/with_FakeNews".format(args.result_path)
	with_FakeNews_date_dirs = ["20210318", "20210413", "20210415"]
	for date_dir in with_FakeNews_date_dirs:
		input_path = "{}/{}/gif_reply.json".format(path_with_FakeNews, date_dir)
		stat_file(input_path, "{}/with_FakeNews/{}/mp4s".format(args.result_path, date_dir))

	path_wo_FakeNews = "{}/wo_FakeNews".format(args.result_path)
	input_path = "{}/20210330/gif_reply.json".format(path_wo_FakeNews)
	stat_file(input_path, "{}/wo_FakeNews/20210330/mp4s".format(args.result_path))
	
	input_path = "{}/package1/merge/test_gold(context+GIF).json".format(args.result_path)
	stat_file(input_path, "{}/package1/merge/mp4s/test_mp4s".format(args.result_path))

	## Fake Gold
	for date_dir in with_FakeNews_date_dirs:
		input_path = "{}/{}/gif_reply.json".format(path_with_FakeNews, date_dir)
		output_path = "{}/package2/{}_gold.json".format(args.result_path, date_dir)
		to_gold(input_path, "fake", output_path)

	input_path = "{}/package1/merge/test_gold(context+GIF).json".format(args.result_path)
	output_path = "{}/package2/package1_gold.json".format(args.result_path)
	to_gold(input_path, "fake", output_path)

	## Real Gold
	input_path = "{}/20210330/gif_reply.json".format(path_wo_FakeNews)
	output_path = "{}/package2/20210330_gold.json".format(args.result_path)
	to_gold(input_path, "real", output_path)

def count_package2(args):
	golds = ["20210318", "20210413", "20210415", "package1"] #"20210330"
	
	idx = []
	for gold in golds:
		source_idx = []
		input_path = "{}/package2/{}_gold.json".format(args.result_path, gold)
		for line in tqdm(open(input_path, encoding="utf-8").readlines()):
			line = line.strip().rstrip()
			json_obj = json.loads(line)
			source_idx.append(json_obj["idx"])
			idx.append(json_obj["idx"])
		print(len(set(source_idx)))
	
	print(len(set(idx)))
	#print(len(set(source_idx)))

	def read_existing():
		print("Reading existing ids")
		exist_ids = []
		date_dirs = ["20210217", "20210218", "20210301"]
		for date_dir in date_dirs:
			path_in = "{}/with_FakeNews/{}/gif_source.txt".format(args.result_path, date_dir)
			for line in tqdm(open(path_in).readlines()):
				line = line.strip().rstrip()
				source_id = line.split("\t")[0]
				exist_ids.append(source_id)
		exist_ids = set(exist_ids)

		return exist_ids

	exist_ids = read_existing()
	
	duplicate = []
	for id in idx:
		if id in exist_ids:
			duplicate.append(id)
	print(len(duplicate))

def phase1_from_package2(args):
	##all_data = {}
	##idxes = []
	#fake_data, real_data = {}, {}
	#fake_idxs, real_idxs = [], []
	##gifs = []
	##GIF_files = []
#
	### fake_data
	#golds = ["20210318", "20210413", "20210415", "package1"]#, "20210330"]
	#for gold in golds:
	#	input_path = "{}/package2/{}_gold.json".format(args.result_path, gold)
	#	for line in tqdm(open(input_path, encoding="utf-8").readlines()):
	#		line = line.strip().rstrip()
	#		json_obj = json.loads(line)
	#		if json_obj["idx"] not in fake_data:
	#			fake_data[json_obj["idx"]] = []
	#			fake_idxs.append(json_obj["idx"])
	#		fake_data[json_obj["idx"]].append(json_obj)
	#		#if json_obj["mp4"] != "":
	#		#	gifs.append(json_obj["mp4"])
	##random.shuffle(fake_idxs)
	#print(len(list(fake_data.items())))
	#print(len(fake_idxs))
#
	### real_data
	#input_path = "{}/package2/20210330_gold.json".format(args.result_path)
	#for line in tqdm(open(input_path, encoding="utf-8").readlines()):
	#	line = line.strip().rstrip()
	#	json_obj = json.loads(line)
	#	if json_obj["idx"] not in real_data:
	#		real_data[json_obj["idx"]] = []
	#		real_idxs.append(json_obj["idx"])
	#	real_data[json_obj["idx"]].append(json_obj)
#
	#phase1_idx = real_idxs[:1200] + fake_idxs[:1200]
	#all_data = fake_data.copy()
	#all_data.update(real_data)
	#random.shuffle(phase1_idx)
#
	#### Check GIF files
	##GIF_files += os.listdir("{}/package1/merge/mp4s/test_mp4s".format(args.result_path))
	##GIF_files += os.listdir("{}/with_FakeNews/20210318/mp4s".format(args.result_path))
	##GIF_files += os.listdir("{}/with_FakeNews/20210413/mp4s".format(args.result_path))
	##GIF_files += os.listdir("{}/with_FakeNews/20210415/mp4s".format(args.result_path))
	##GIF_files += os.listdir("{}/wo_FakeNews/20210330/mp4s".format(args.result_path))
	#
	##missing_gifs = []
	##for gif in gifs:
	##	if gif not in GIF_files:
	##		missing_gifs.append(gif)
	##print(len(missing_gifs))
#
	#fw = open("{}/package2/phase1_test/test_gold.json".format(args.result_path), "w", encoding="utf-8")
	#for index, idx in enumerate(tqdm(phase1_idx)):
	#	for json_obj in all_data[idx]:
	#		json_obj["idx"] = index + 44000
	#		fw.write(json.dumps(json_obj, ensure_ascii=False))
	#		fw.write("\n")
	#fw.close()

	GIF_files = os.listdir("{}/package2/mp4s/phase1_mp4s".format(args.result_path))
	missing_gifs = []
	## Move phase1 GIF files
	phase1_GIFs = []
	for line in tqdm(open("{}/package2/phase1_test/test_gold.json".format(args.result_path), encoding="utf-8").readlines()):
		line = line.strip().rstrip()
		json_obj = json.loads(line)
		if json_obj["mp4"] != "":
			phase1_GIFs.append(json_obj["mp4"])
			if json_obj["mp4"] not in GIF_files:
				missing_gifs.append(json_obj["mp4"])
	
	print(len(set(phase1_GIFs)))
	print(len(missing_gifs))

	#mp4_dirs = ["20210318", "20210330", "20210413", "20210415", "test_mp4s"]
	#for mp4_dir in tqdm(mp4_dirs):
	#	for mp4_file in os.listdir("{}/package2/mp4s/{}".format(args.result_path, mp4_dir)):
	#		if mp4_file in phase1_GIFs:
	#			shutil.move("{}/package2/mp4s/{}/{}".format(args.result_path, mp4_dir, mp4_file), "{}/package2/mp4s/phase1_mp4s/{}".format(args.result_path, mp4_file))

def main(args):
	if args.total_count:
		total_count(args)
	elif args.gif_source_total_reply:
		gif_source_total_reply(args)
	elif args.count_by_txt:
		count_by_txt(args)
	elif args.count_miss_gif:
		count_miss_gif(args)
	elif args.insert_missing:
		insert_missing(args)
	elif args.read_final_and_test:
		read_final_and_test(args)
	elif args.cnt_existing:
		cnt_existing(args)
	elif args.detect_source:
		detect_source(args)
	elif args.check:
		check(args)
	elif args.package2:
		package2(args)
	elif args.count_package2:
		count_package2(args)
	elif args.phase1_from_package2:
		phase1_from_package2(args)

if __name__ == "__main__":
	args = parse_args()
	main(args)
	