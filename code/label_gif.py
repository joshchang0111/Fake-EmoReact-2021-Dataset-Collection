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
	parser.add_argument("-gif_frames", type=str2bool, default=False)
	parser.add_argument("-find_similar_img", type=str2bool, default=False)
	parser.add_argument("-construct_categories_table", type=str2bool, default=False)
	parser.add_argument("-merge_EmotionGIF_mp4s", type=str2bool, default=False)
	parser.add_argument("-merge_10_json", type=str2bool, default=False)
	parser.add_argument("-analyze_FakeNewsGIF_labels", type=str2bool, default=False)
	parser.add_argument("-label_from_EmotionGIF", type=str2bool, default=False)
	parser.add_argument("-label_from_top100", type=str2bool, default=False)
	parser.add_argument("-write2gold", type=str2bool, default=False)
	parser.add_argument("-arrange_mp4_files", type=str2bool, default=False)

	# other arguments
	parser.add_argument("-part", type=int, default=0)
	parser.add_argument("-date_dir", type=str, default="20210413")
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
	'''
	Extract first frame of mp4s.
	'''
	def extract_frames(path_mp4, path_frame):
		mp4s = os.listdir(path_mp4)
		corrupted_files = []
		for file in tqdm(mp4s):
			try:
				if file[0] == "." or ".mp4" not in file:
					continue
				vidcap = cv2.VideoCapture("{}/{}".format(path_mp4, file))
				success, image = vidcap.read()
				cv2.imwrite("{}/{}.jpg".format(path_frame, file.split(".")[0]), image)
			except:
				corrupted_files.append(file)
				continue
				
		print(corrupted_files)

	print("Extracting frames")
	path_mp4 = "{}/with_FakeNews/{}/mp4s".format(args.result_path, args.date_dir)
	path_frame = "{}/with_FakeNews/{}/frames".format(args.result_path, args.date_dir)
	extract_frames(path_mp4, path_frame)

def gif_frames(args):
	def write_frame(video_file, out_frame_path):
		vidcap = cv2.VideoCapture(video_file)
		success, image = vidcap.read()
		cv2.imwrite("{}/{}.jpg".format(out_frame_path, video_file.split("/")[-1].split(".")[0]), image)

	categories = ["Agree", "Applause", "Awww", "Dance", "Deal with it", "Do not want", "Eww", "Eye roll", "Facepalm", "Fist bump", "Good luck", "Happy dance", "Hearts", "High five", "Hug", "IDK", "Kiss", "Mic drop", "No", "Oh snap", "Ok", "OMG", "Oops", "Please", "Popcorn", "Scared", "Seriously", "Shocked", "Shrug", "Sigh", "Slow clap", "SMH", "Sorry", "Thank you", "Thumbs down", "Thumbs up", "Want", "Win", "Wink", "Yawn", "Yes", "YOLO", "You got this"]
	for category in tqdm(categories):
		path_gif_category = "{}/final/merge/top100GIF/{}".format(args.result_path, category)
		path_frame_category = "{}/final/merge/top100frame/{}".format(args.result_path, category)
		os.makedirs(path_frame_category, exist_ok=True)

		for idx in tqdm(range(100)):
			path_gif = "{}/{}.gif".format(path_gif_category, idx)
			write_frame(path_gif, path_frame_category)

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
	json_file_name = "gif_reply"#"unlabeled_mp4s_labels"
	labels_dict = {}
	for idx in range(10):
		path_in = "{}/with_FakeNews/{}/{}_{}.json".format(args.result_path, args.date_dir, json_file_name, idx)
		json_obj = json.load(open(path_in))
		labels_dict.update(json_obj)
	print(len(list(labels_dict.items())))

	path_out = "{}/with_FakeNews/{}/{}.json".format(args.result_path, args.date_dir, json_file_name)
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
		new_list = []
		for label in json_obj[labeled_mp4]:
			label = label.lower().replace(" ", "_")
			new_list.append(label)
		mp4_dict[labeled_mp4] = new_list

	path_out = "{}/final/merge/FakeNewsGIF_labels_new.json".format(args.result_path)
	json.dump(mp4_dict, open(path_out, "w"), indent=4)
	'''
	
	#path_in = "{}/final/merge/FakeNewsGIF_labels_new.json".format(args.result_path)
	path_in = "{}/with_FakeNews/{}/mp4s_labels.json".format(args.result_path, args.date_dir)
	
	json_obj = json.load(open(path_in))
	labeled_files, unlabeled_files = [], []
	for mp4_file, categories in tqdm(list(json_obj.items())):
		if not categories: ## empty list
			unlabeled_files.append(mp4_file)
		else:
			labeled_files.append(mp4_file)

	print("Unlabeled files: {}".format(len(unlabeled_files)))
	print("Labeled files: {}".format(len(labeled_files)))

	fw = open("{}/with_FakeNews/{}/unlabeled_mp4s.txt".format(args.result_path, args.date_dir), "w")
	for unlabeled_file in tqdm(unlabeled_files):
		fw.write("{}\n".format(unlabeled_file))
	fw.close()

def label_from_EmotionGIF(args):
	def labeling(mp4_dict, target_path, path_frames_pool, frames_pool):
		## parameters for image hashing
		similarity, hash_size = 90, 8
		threshold = 1 - similarity / 100
		diff_limit = int(threshold * (hash_size ** 2))

		with Image.open(target_path) as img:
			hash1 = imagehash.average_hash(img, hash_size).hash
		
		labels = []
		for image in frames_pool:
			## filter hidden files and not jpg files
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

	path_fakenews_frame = "{}/with_FakeNews/{}/frames/".format(args.result_path, args.date_dir)
	path_emotion_frame = "{}/package1/merge/frames/EmotionGIF".format(args.result_path)

	## Read from EmotionGIF categories
	path_categories = "{}/package1/merge/EmotionGIF_labels.json".format(args.result_path)
	f = open(path_categories)
	mp4_dict = json.load(f)
	f.close()

	## Read unlabeled mp4s
	unlabeled_mp4s = []
	for line in tqdm(open("{}/with_FakeNews/{}/unlabeled_mp4s.txt".format(args.result_path, args.date_dir)).readlines()):
		line = line.strip().rstrip()
		unlabeled_mp4s.append(line)

	######################
	## Split 10 portion ##
	######################
	start_idx = int(args.part * (len(unlabeled_mp4s) / 10))
	end_idx = int((args.part + 1) * (len(unlabeled_mp4s) / 10))

	## Labeling
	new_dict = {}
	emotion_frames = os.listdir(path_emotion_frame)
	#for unlabeled_mp4 in tqdm(unlabeled_mp4s[start_idx:end_idx]):
	for unlabeled_mp4 in tqdm(unlabeled_mp4s):
		target_path = "{}/{}.jpg".format(path_fakenews_frame, unlabeled_mp4.split(".")[0])
		categories = labeling(mp4_dict, target_path, path_emotion_frame, emotion_frames)
		new_dict[unlabeled_mp4] = categories

	fw = open("{}/with_FakeNews/{}/unlabeled_mp4s_labels_{}.json".format(args.result_path, args.date_dir, args.part), "w")
	json.dump(new_dict, fw, indent=4)
	fw.close()

def label_from_top100(args):
	def labeling(target_path):
		categories = ["Agree", "Applause", "Awww", "Dance", "Deal with it", "Do not want", "Eww", "Eye roll", "Facepalm", "Fist bump", "Good luck", "Happy dance", "Hearts", "High five", "Hug", "IDK", "Kiss", "Mic drop", "No", "Oh snap", "Ok", "OMG", "Oops", "Please", "Popcorn", "Scared", "Seriously", "Shocked", "Shrug", "Sigh", "Slow clap", "SMH", "Sorry", "Thank you", "Thumbs down", "Thumbs up", "Want", "Win", "Wink", "Yawn", "Yes", "YOLO", "You got this"]

		## parameters for image hashing
		similarity, hash_size = 90, 8
		threshold = 1 - similarity / 100
		diff_limit = int(threshold * (hash_size ** 2))

		## target image hashing
		with Image.open(target_path) as img:
			hash1 = imagehash.average_hash(img, hash_size).hash
		
		labels = []
		## iterate through all categories
		for category in categories:
			## comparing target with all images of on category
			path_frames_pool = "{}/package1/merge/top100frame/{}".format(args.result_path, category)
			for idx in range(100):
				path_frame = "{}/{}.jpg".format(path_frames_pool, idx)
				with Image.open(path_frame) as img:
					hash2 = imagehash.average_hash(img, hash_size).hash
					## if one image are similar with target
					if np.count_nonzero(hash1 != hash2) <= diff_limit:
						labels.append(category)
						break

		return labels

	### Read unlabeled files
	#input_path = "{}/final/merge/unlabeled_files.txt".format(args.result_path)
	#unlabeled_files = []
	#for line in tqdm(open(input_path).readlines()):
	#	line = line.strip().rstrip()
	#	unlabeled_files.append(line)

	path_frame = "{}/with_FakeNews/{}/frames".format(args.result_path, args.date_dir)
	new_frame_files = []
	frame_files = os.listdir(path_frame)
	for frame in frame_files:
		if frame[0] == "." or ".jpg" not in frame:
			continue
		new_frame_files.append(frame)
	frame_files = new_frame_files

	### Split 10 portion
	#start_idx = int(args.part * (len(frame_files) / 10))
	#end_idx = int((args.part + 1) * (len(frame_files) / 10))

	## Labeling
	new_dict = {}
	#for frame in tqdm(frame_files[start_idx:end_idx]):
	for frame in tqdm(frame_files):
		target_path = "{}/{}.jpg".format(path_frame, frame.split(".")[0])
		categories = labeling(target_path)
		new_dict[frame] = categories

	fw = open("{}/with_FakeNews/{}/mp4s_labels_{}.json".format(args.result_path, args.date_dir, args.part), "w")
	json.dump(new_dict, fw, indent=4)
	fw.close()

def write2gold(args):
	def read_gold(input_path):
		gold_json_list = []
		for line in tqdm(open(input_path, encoding="utf-8").readlines()):
			line = line.strip().rstrip()
			json_obj = json.loads(line)
			gold_json_list.append(json_obj)
		return gold_json_list

	def read_GIF_labels(input_path):
		mp4_dict = json.load(open(input_path))
		return mp4_dict

	#input_path = "{}/final/merge/all_gold(context+GIF).json".format(args.result_path)
	input_path = "{}/final/from_FakeNewsGIF/new_all_gold.json".format(args.result_path)
	gold_json_list = read_gold(input_path)

	input_path = "{}/final/merge/FakeNewsGIF_labels.json".format(args.result_path)
	mp4_dict = read_GIF_labels(input_path)
	print(len(list(mp4_dict.items())))

	new_gold_list = []
	for gold_json in tqdm(gold_json_list):
		if gold_json["mp4"] in mp4_dict:
			gold_json["categories"] = mp4_dict[gold_json["mp4"]]
		new_gold_list.append(gold_json)
	print(len(new_gold_list))

	output_path = "{}/final/from_FakeNewsGIF/new_all_gold(categories).json".format(args.result_path)
	fw = open(output_path, "w", encoding="utf-8")
	for new_gold in tqdm(new_gold_list):
		fw.write(json.dumps(new_gold, ensure_ascii=False)) # for writing emojis
		fw.write("\n")
	fw.close()

def arrange_mp4_files(args):
	## read mp4 file name
	input_path = "{}/final/from_FakeNewsGIF/new_all_gold.json".format(args.result_path)
	fakenews_mp4s = []
	for line in tqdm(open(input_path, "r", encoding="utf-8").readlines()):
		line = line.strip().rstrip()
		json_obj = json.loads(line)
		if json_obj["mp4"] != "":
			fakenews_mp4s.append(json_obj["mp4"])
	fakenews_mp4s = set(fakenews_mp4s)
	print(len(fakenews_mp4s))

	'''
	## remove files that are at the same tree of corrupted file
	path_mp4s = "{}/final/merge/mp4s".format(args.result_path)
	mp4_files = os.listdir("{}/FakeNewsGIF".format(path_mp4s))
	for mp4_file in tqdm(mp4_files):
		if mp4_file[0] == "." and ".mp4" not in "mp4_file":
			continue
		if mp4_file not in fakenews_mp4s:
			src = "{}/FakeNewsGIF/{}".format(path_mp4s, mp4_file)
			dst = "{}/removed_FakeNewsGIF/{}".format(path_mp4s, mp4_file)
			shutil.move(src, dst)
	'''

	## arrange mp4 label file
	input_path = "{}/final/merge/FakeNewsGIF_labels.json".format(args.result_path)
	json_obj = json.load(open(input_path))
	print(len(list(json_obj.items())))
	for mp4_file, categories in tqdm(list(json_obj.items())):
		if mp4_file not in fakenews_mp4s:
			del json_obj[mp4_file]
	print(len(list(json_obj.items())))

	output_path = "{}/final/merge/FakeNewsGIF_labels_new.json".format(args.result_path)
	json.dump(json_obj, open(output_path, "w"), indent=4)

def main(args):
	if args.merge_mp4s:
		merge_mp4s(args)
	elif args.mp4_frames:
		mp4_frames(args)
	elif args.gif_frames:
		gif_frames(args)
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
	elif args.label_from_EmotionGIF:
		label_from_EmotionGIF(args)
	elif args.label_from_top100:
		label_from_top100(args)
	elif args.write2gold:
		write2gold(args)
	elif args.arrange_mp4_files:
		arrange_mp4_files(args)

if __name__ == "__main__":
	args = parse_args()
	main(args)