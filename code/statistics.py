import os
import json
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

	# other arguments
	parser.add_argument("-result_path", type=str, default="/mnt/hdd1/joshchang/datasets/FakeNewsGIF/")
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

if __name__ == "__main__":
	args = parse_args()
	main(args)
	