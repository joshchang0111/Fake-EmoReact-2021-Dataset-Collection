import os
import json
import shutil
import argparse
from tqdm import tqdm

import cv2

from PIL import Image
import imagehash
import numpy as np
from collections import Counter

def str2bool(str):
	if str.lower() == "false":
		return False
	elif str.lower() == "true":
		return True

def parse_args():
	parser = argparse.ArgumentParser(description="Attempting to label the mp4 files.")

	# mode
	parser.add_argument("-merge_mp4s", type=str2bool, default=False)
	parser.add_argument("-mp4_frames", type=str2bool, default=False)
	parser.add_argument("-find_similar_img", type=str2bool, default=False)
	parser.add_argument("-construct_categories_table", type=str2bool, default=False)
	parser.add_argument("-merge_EmotionGIF_mp4s", type=str2bool, default=False)
	parser.add_argument("-merge_10_json", type=str2bool, default=False)
	parser.add_argument("-analyze_FakeNewsGIF_labels", type=str2bool, default=False)
	parser.add_argument("-labeling_mp4s", type=str2bool, default=False)

	# other arguments
	parser.add_argument("-part", type=int, default=0)
	parser.add_argument("-date_dir", type=str, default="20210301")
	parser.add_argument("-result_path", type=str, default="/mnt/hdd1/joshchang/datasets/FakeNewsGIF")

	args=parser.parse_args()
	
	return args

def merge_mp4s(args):
	#print("Checking whether all mp4s exist.")
	##all_mp4s = os.listdir("{}/final/merge/mp4s/".format(args.result_path))
	#all_mp4s = os.listdir("/mnt/hdd1/joshchang/datasets/EmotionGIF/train_mp4s")
	##gif_json_path = "{}/final/from_FakeNewsGIF/GIF/all_gold.json".format(args.result_path)
	#files = ["train_gold.json", "dev_gold.json", "eval_gold.json"]
	#missing_mp4_list = []
	#for file in files:
	#	gif_json_path = "{}/final/from_EmotionGIF/{}".format(args.result_path, file)
	#	for line in tqdm(open(gif_json_path, encoding="utf-8").readlines()):
	#		line = line.strip().rstrip()
	#		json_obj = json.loads(line)
	#		if json_obj["mp4"] not in all_mp4s:
	#			missing_mp4_list.append(json_obj["mp4"])
	#print(len(missing_mp4_list))

	print("from FakeNewsGIF")
	
	date_dirs = ["20210217", "20210218", "20210301"]
	# iterate all date_dirs
	for date_dir in date_dirs:
		args.date_dir = date_dir
		path_date_dir = "{}/reply/{}/gif_reply".format(args.result_path, args.date_dir)
		source_ids = os.listdir(path_date_dir)
		# iterate all source_id dirs
		for source_id in tqdm(source_ids):
			if source_id[0] == ".":
				continue
			path_mp4s = "{}/{}/reply".format(path_date_dir, source_id)
			files = os.listdir(path_mp4s)
			# iterate all mp4 files
			for file in files:
				if file[0] == "." or ".json" in file:
					continue
				mp4_src = "{}/{}".format(path_mp4s, file)
				mp4_dst = "{}/final/merge/mp4s/{}".format(args.result_path, file)
				shutil.copyfile(mp4_src, mp4_dst)

	print()
	print("from EmotionGIF")

	path_train_mp4s = "/mnt/hdd1/joshchang/datasets/EmotionGIF/train_mp4s"
	train_mp4s = os.listdir(path_train_mp4s)
	for file in tqdm(train_mp4s):
		mp4_src = "{}/{}".format(path_train_mp4s, file)
		mp4_dst = "{}/final/merge/mp4s/EmotionGIF_train/{}".format(args.result_path, file)
		shutil.copyfile(mp4_src, mp4_dst)

def mp4_frames(args):
	def extract_frames(path_mp4, path_frame):
		mp4s = os.listdir(path_mp4)
		corrupted_files = 0
		for file in tqdm(mp4s):
			try:
				if file[0] == "." or ".mp4" not in file:
					continue
				vidcap = cv2.VideoCapture("{}/{}".format(path_mp4, file))
				#if not vidcap.isOpened():
				#	print(file)
				#	print("Error opening video.")
				#	break
				#success = False
				#while not success:
				success, image = vidcap.read()
				cv2.imwrite("{}/{}.jpg".format(path_frame, file.split(".")[0]), image)
			except:
				corrupted_files += 1
				continue
				
		print(corrupted_files)

	print("Extracting frames of EmotionGIF")
	#path_mp4 = "/mnt/hdd1/joshchang/datasets/EmotionGIF/train_mp4s"
	path_mp4 = "{}/final/merge/mp4s/EmotionGIF_test".format(args.result_path)
	path_frame = "{}/final/merge/frames/EmotionGIF_test".format(args.result_path)
	extract_frames(path_mp4, path_frame)
	
	#print("Extracting frames of FakeNewsGIF")
	#path_mp4 = "{}/final/merge/mp4s/FakeNewsGIF".format(args.result_path)
	#path_frame = "{}/final/merge/frames/FakeNewsGIF".format(args.result_path)
	#extract_frames(path_mp4, path_frame)

def construct_categories_table(args):
	mp4_dict = {} # {"file name": list of categories}
	files = ["train_gold.json", "dev_gold.json", "eval_gold.json"]
	for file in files:
		input_path = "{}/final/from_EmotionGIF/{}".format(args.result_path, file)
		for line in tqdm(open(input_path, encoding="utf-8").readlines()):
			line = line.strip().rstrip()
			json_obj = json.loads(line)
			mp4_dict[json_obj["mp4"]] = json_obj["categories"]
	print(len(mp4_dict.items()))
	
	# Write
	output_path = "{}/final/merge/EmotionGIF_labels.json".format(args.result_path)
	fw = open(output_path, "w")
	json.dump(mp4_dict, fw, indent=4)
	fw.close()

def find_similar_img(args):
	## Read GIF categories
	path_categories = "{}/final/merge/GIF_labels.json".format(args.result_path)
	f = open(path_categories)
	mp4_dict = json.load(f)
	f.close()

	path_fakenews_frame = "{}/final/merge/frames/FakeNewsGIF".format(args.result_path)
	path_emotion_frame = "{}/final/merge/frames/EmotionGIF_train".format(args.result_path)
	
	## parameters for image hashing
	similarity, hash_size = 90, 8
	threshold = 1 - similarity / 100
	diff_limit = int(threshold * (hash_size ** 2))

	emotion_frames = os.listdir(path_emotion_frame)
	fakenews_frames = os.listdir(path_fakenews_frame)

	######################
	## Split 10 portion ##
	######################
	start_idx = int(args.part * (len(fakenews_frames) / 10))
	end_idx = int((args.part + 1) * (len(fakenews_frames) / 10))
	
	fakenews_mp4_dict = {}
	for target_file in tqdm(fakenews_frames[start_idx:end_idx]):
		target_path = "{}/{}".format(path_fakenews_frame, target_file)
		with Image.open(target_path) as img:
			hash1 = imagehash.average_hash(img, hash_size).hash
		
		labels = []
		for image in emotion_frames:
			if image[0] == "." or ".jpg" not in image:
				continue
			with Image.open("{}/{}".format(path_emotion_frame, image)) as img:
				hash2 = imagehash.average_hash(img, hash_size).hash
		
				if np.count_nonzero(hash1 != hash2) <= diff_limit:
					#print("{} image found {}% similar to {}".format(image, similarity, target_file))
					#shutil.copyfile("{}/{}".format(path_emotion_frame, image), "{}/final/merge/frames/{}".format(args.result_path, image))
					label_str = ""
					for label in mp4_dict["{}.mp4".format(image.split(".")[0])]:
						label_str += "/{}".format(label)
					labels.append(label_str)
		
		categories = []
		if labels != []:
			labels = Counter(labels)
			label_str = labels.most_common(1)[0][0]
			for label in label_str.split("/"):
				if label == "":
					continue
				categories.append(label)
			#print(categories)
		fakenews_mp4_dict["{}.mp4".format(target_file.split(".")[0])] = categories

	## Write FakeNewsGIF categories table
	path_out = "{}/final/merge/FakeNewsGIF_labels_{}.json".format(args.result_path, args.part)
	fw = open(path_out, "w")
	json.dump(fakenews_mp4_dict, fw, indent=4)
	fw.close()

def merge_EmotionGIF_mp4s(args):
	## Read train mp4 names
	train_mp4s, eval_mp4s, dev_mp4s = [], [], []
	input_path = "{}/final/from_EmotionGIF/train_gold.json".format(args.result_path)
	for line in tqdm(open(input_path).readlines()):
		line = line.strip().rstrip()
		json_obj = json.loads(line)
		train_mp4s.append(json_obj["mp4"])

	train_mp4s = set(train_mp4s)
	print(len(train_mp4s))

	dirs = ["EmotionGIF_dev", "EmotionGIF_eval"]
	for dir in dirs:
		mp4_path = "{}/final/merge/mp4s/{}".format(args.result_path, dir)
		mp4_files = os.listdir(mp4_path)
		for mp4_file in tqdm(mp4_files):
			if mp4_file[0] == "." or ".mp4" not in mp4_file:
				continue
			if dir == "EmotionGIF_dev" and mp4_file not in train_mp4s:
				dev_mp4s.append(mp4_file)
			if dir == "EmotionGIF_eval" and mp4_file not in train_mp4s:
				eval_mp4s.append(mp4_file)

	test_mp4s = dev_mp4s + eval_mp4s
	test_mp4s = set(test_mp4s)
	print(len(test_mp4s))

	path_out = "{}/final/merge/mp4s/EmotionGIF_test".format(args.result_path)
	for dev_mp4 in tqdm(dev_mp4s):
		shutil.copyfile("{}/final/merge/mp4s/EmotionGIF_dev/{}".format(args.result_path, dev_mp4), "{}/{}".format(path_out, dev_mp4))
	for eval_mp4 in tqdm(eval_mp4s):
		shutil.copyfile("{}/final/merge/mp4s/EmotionGIF_eval/{}".format(args.result_path, eval_mp4), "{}/{}".format(path_out, eval_mp4))

def merge_10_json(args):
	json_file_name = "unlabeled_mp4s_labels"
	labels_dict = {}
	for idx in range(10):
		path_in = "{}/final/merge/{}_{}.json".format(args.result_path, json_file_name, idx)
		json_obj = json.load(open(path_in))
		labels_dict.update(json_obj)
	print(len(list(labels_dict.items())))

	path_out = "{}/final/merge/{}.json".format(args.result_path, json_file_name)
	fw = open(path_out, "w")
	json.dump(labels_dict, fw, indent=4)
	fw.close()

def analyze_FakeNewsGIF_labels(args):
	'''
	path_in = "{}/final/merge/unlabeled_mp4s_labels.json".format(args.result_path)
	
	json_obj = json.load(open(path_in))
	labeled_files, unlabeled_files = [], []
	for mp4_file, categories in tqdm(list(json_obj.items())):
		if not categories: ## empty list
			unlabeled_files.append(mp4_file)
		else:
			labeled_files.append(mp4_file)

	print("Unlabeled files: {}".format(len(unlabeled_files)))
	print("Labeled files: {}".format(len(labeled_files)))

	## Rewrite FakeNewsGIF_labels.json
	path_in = "{}/final/merge/FakeNewsGIF_labels.json".format(args.result_path)
	mp4_dict = json.load(open(path_in))

	for labeled_mp4 in tqdm(labeled_files):
		mp4_dict[labeled_mp4] = json_obj[labeled_mp4]

	path_out = "{}/final/merge/FakeNewsGIF_labels_new.json".format(args.result_path)
	json.dump(mp4_dict, open(path_out, "w"), indent=4)
	'''
	path_in = "{}/final/merge/FakeNewsGIF_labels.json".format(args.result_path)
	
	json_obj = json.load(open(path_in))
	labeled_files, unlabeled_files = [], []
	for mp4_file, categories in tqdm(list(json_obj.items())):
		if not categories: ## empty list
			unlabeled_files.append(mp4_file)
		else:
			labeled_files.append(mp4_file)

	print("Unlabeled files: {}".format(len(unlabeled_files)))
	print("Labeled files: {}".format(len(labeled_files)))

	fw = open("{}/final/merge/unlabeled_files.txt".format(args.result_path), "w")
	for unlabeled_file in tqdm(unlabeled_files):
		fw.write("{}\n".format(unlabeled_file))
	fw.close()

def labeling_mp4s(args):
	def labeling(mp4_dict, target_path, path_frames_pool, frames_pool):
		## parameters for image hashing
		similarity, hash_size = 90, 8
		threshold = 1 - similarity / 100
		diff_limit = int(threshold * (hash_size ** 2))

		with Image.open(target_path) as img:
			hash1 = imagehash.average_hash(img, hash_size).hash
		
		labels = []
		for image in frames_pool:
			if image[0] == "." or ".jpg" not in image:
				continue
			with Image.open("{}/{}".format(path_frames_pool, image)) as img:
				hash2 = imagehash.average_hash(img, hash_size).hash
		
				if np.count_nonzero(hash1 != hash2) <= diff_limit:
					label_str = ""
					for label in mp4_dict["{}.mp4".format(image.split(".")[0])]:
						label_str += "/{}".format(label)
					labels.append(label_str)
		
		categories = []
		if labels != []:
			labels = Counter(labels)
			label_str = labels.most_common(1)[0][0]
			for label in label_str.split("/"):
				if label == "":
					continue
				categories.append(label)
		return categories

	path_fakenews_frame = "{}/final/merge/frames/FakeNewsGIF".format(args.result_path)
	path_emotion_frame = "{}/final/merge/frames/EmotionGIF_test".format(args.result_path)

	## Read from EmotionGIF categories
	path_categories = "{}/final/merge/EmotionGIF_labels.json".format(args.result_path)
	f = open(path_categories)
	mp4_dict = json.load(f)
	f.close()

	## Read unlabeled mp4s
	unlabeled_mp4s = []
	for line in tqdm(open("{}/final/merge/unlabeled_files.txt".format(args.result_path)).readlines()):
		line = line.strip().rstrip()
		unlabeled_mp4s.append(line)

	## Split 10 portion
	start_idx = int(args.part * (len(unlabeled_mp4s) / 10))
	end_idx = int((args.part + 1) * (len(unlabeled_mp4s) / 10))
	## Labeling
	new_dict = {}
	emotion_frames = os.listdir(path_emotion_frame)
	for unlabeled_mp4 in tqdm(unlabeled_mp4s[start_idx:end_idx]):
		target_path = "{}/{}.jpg".format(path_fakenews_frame, unlabeled_mp4.split(".")[0])
		categories = labeling(mp4_dict, target_path, path_emotion_frame, emotion_frames)
		new_dict[unlabeled_mp4] = categories

	fw = open("{}/final/merge/unlabeled_mp4s_labels_{}.json".format(args.result_path, args.part), "w")
	json.dump(new_dict, fw, indent=4)
	fw.close()

def main(args):
	if args.merge_mp4s:
		merge_mp4s(args)
	elif args.mp4_frames:
		mp4_frames(args)
	elif args.find_similar_img:
		find_similar_img(args)
	elif args.construct_categories_table:
		construct_categories_table(args)
	elif args.merge_EmotionGIF_mp4s:
		merge_EmotionGIF_mp4s(args)
	elif args.merge_10_json:
		merge_10_json(args)
	elif args.analyze_FakeNewsGIF_labels:
		analyze_FakeNewsGIF_labels(args)
	elif args.labeling_mp4s:
		labeling_mp4s(args)

if __name__ == "__main__":
	args = parse_args()
	main(args)