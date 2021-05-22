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
	parser.add_argument("-package3", type=str2bool, default=False)
	parser.add_argument("-phase2_test", type=str2bool, default=False)
	parser.add_argument("-check", type=str2bool, default=False)

	# other arguments
	parser.add_argument("-result_path", type=str, default="/mnt/hdd1/joshchang/datasets/FakeNewsGIF")
	parser.add_argument("-date_dir", type=str, default="20210301")

	args=parser.parse_args()
	
	return args

def package3(args):
	real_data, fake_data = {}, {}
	real_idxs, fake_idxs = [], []
	
	## real_data
	input_path = "{}/package2/20210330_gold.json".format(args.result_path)
	for line in tqdm(open(input_path, encoding="utf-8").readlines()):
		line = line.strip().rstrip()
		json_obj = json.loads(line)
		if json_obj["idx"] not in real_data:
			real_data[json_obj["idx"]] = []
			real_idxs.append(json_obj["idx"])
		real_data[json_obj["idx"]].append(json_obj)
	print(len(real_data.items()))

	## real_data for package3
	real_idxs_pk3 = real_idxs[1200:]
	print(len(real_idxs_pk3))

	## check if real_idxs_pk3's mp4s are all in package3/mp4s/real
	check = []
	real_mp4s = os.listdir("{}/package3/mp4s/real".format(args.result_path))
	for idx in tqdm(real_idxs_pk3):
		for data_pair in real_data[idx]:
			if data_pair["mp4"] != "":
				## check
				if data_pair["mp4"] not in real_mp4s:
					check.append(data_pair["idx"])
					print(data_pair["idx"])
	print(len(check))

	## remove idx that has disappeared mp4s
	real_idxs_pk3 = [idx for idx in real_idxs_pk3 if idx not in check]
	print(len(real_idxs_pk3))

	print(real_data[real_idxs_pk3[0]][0].keys())

	## write file
	print("WRITE FILE")
	fw = open("{}/package3/real_gold.json".format(args.result_path), "w", encoding="utf-8")
	for idx in tqdm(real_idxs_pk3):
		for data_pair in real_data[idx]:
			fw.write(json.dumps(data_pair, ensure_ascii=False))
			fw.write("\n")
	fw.close()
	
	## fake_data
	golds = ["20210318", "20210413", "20210415", "package1"]
	for gold in golds:
		input_path = "{}/package2/{}_gold.json".format(args.result_path, gold)
		for line in tqdm(open(input_path, encoding="utf-8").readlines()):
			line = line.strip().rstrip()
			json_obj = json.loads(line)
			if json_obj["idx"] not in fake_data:
				fake_data[json_obj["idx"]] = []
				fake_idxs.append(json_obj["idx"])
			fake_data[json_obj["idx"]].append(json_obj)
			#if json_obj["mp4"] != "":
			#	gifs.append(json_obj["mp4"])
	print(len(list(fake_data.items())))
	print(len(fake_idxs))

	fake_idxs_pk3 = fake_idxs[1200:]
	#fake_mp4s = os.listdir("{}/package2/mp4s/20210415".format(args.result_path)) + os.listdir("{}/package2/mp4s/test_mp4s".format(args.result_path))
	fake_mp4s = os.listdir("{}/package3/mp4s/fake".format(args.result_path))
	print(len(fake_mp4s))
	print(len(fake_idxs_pk3))

	## count gif and check if they are all in package3/mp4s/fake
	fake_gifs, check = [], []
	for idx in tqdm(fake_idxs_pk3):
		for data_pair in fake_data[idx]:
			if data_pair["mp4"] != "":
				fake_gifs.append(data_pair)
				## check
				if data_pair["mp4"] in fake_mp4s:
					check.append(data_pair["idx"])
					#print(data_pair["idx"])
	print(len(fake_gifs))
	print(len(check))
	print(fake_gifs[1000].keys())

	## write file
	print("WRITE FILE")
	fw = open("{}/package3/fake_gold.json".format(args.result_path), "w", encoding="utf-8")
	for idx in tqdm(fake_idxs_pk3):
		for data_pair in fake_data[idx]:
			fw.write(json.dumps(data_pair, ensure_ascii=False))
			fw.write("\n")
	fw.close()

def phase2_test(args):
	real_data, fake_data = {}, {}
	real_idxs, fake_idxs = [], []

	## real_data
	input_path = "{}/package3/real_gold.json".format(args.result_path)
	for line in tqdm(open(input_path, encoding="utf-8").readlines()):
		line = line.strip().rstrip()
		json_obj = json.loads(line)
		if json_obj["idx"] not in real_data:
			real_data[json_obj["idx"]] = []
			real_idxs.append(json_obj["idx"])
		real_data[json_obj["idx"]].append(json_obj)
	print(len(real_data.items()))

	## fake_data
	input_path = "{}/package3/fake_gold.json".format(args.result_path)
	for line in tqdm(open(input_path, encoding="utf-8").readlines()):
		line = line.strip().rstrip()
		json_obj = json.loads(line)
		if json_obj["idx"] not in fake_data:
			fake_data[json_obj["idx"]] = []
			fake_idxs.append(json_obj["idx"])
		fake_data[json_obj["idx"]].append(json_obj)
		#if json_obj["mp4"] != "":
		#	gifs.append(json_obj["mp4"])
	print(len(fake_data.items()))

	## move mp4 file of first 2000 real_data to package3/phase2_test/mp4s
	check = []
	real_mp4s = os.listdir("{}/package3/mp4s/real".format(args.result_path))
	for idx in tqdm(real_idxs[:2000]):
		for data_pair in real_data[idx]:
			if data_pair["mp4"] != "":
				try:
					shutil.move("{}/package3/mp4s/real/{}".format(args.result_path, data_pair["mp4"]), "{}/package3/phase2_test/mp4s/{}".format(args.result_path, data_pair["mp4"]))
				except:
					continue
				## check
				if data_pair["mp4"] not in real_mp4s:
					check.append(data_pair["mp4"])
	print(len(set(check)))

	## write file
	phase2_idxs = fake_idxs + real_idxs[:2000]
	all_data = real_data.copy()
	all_data.update(fake_data)
	print("WRITE FILE")
	fw = open("{}/package3/phase2_test/test_gold.json".format(args.result_path), "w", encoding="utf-8")
	for idx, phase2_idx in enumerate(tqdm(phase2_idxs)):
		for data_pair in all_data[phase2_idx]:
			data_pair["idx"] = idx
			fw.write(json.dumps(data_pair, ensure_ascii=False))
			fw.write("\n")
	fw.close()

def check(args):
	test_data, test_idxs = {}, []
	## test_data
	input_path = "{}/package3/phase2_test/test_gold.json".format(args.result_path)
	for line in tqdm(open(input_path, encoding="utf-8").readlines()):
		line = line.strip().rstrip()
		json_obj = json.loads(line)
		if json_obj["idx"] not in test_data:
			test_data[json_obj["idx"]] = []
			test_idxs.append(json_obj["idx"])
		test_data[json_obj["idx"]].append(json_obj)
	print(len(test_data.items()))

	test_mp4s = os.listdir("{}/package3/phase2_test/mp4s".format(args.result_path))
	real, fake = 0, 0
	check = []
	for idx in tqdm(test_idxs):
		if test_data[idx][0]["label"] == "fake":
			fake += 1
		else:
			real += 1

		for data_pair in test_data[idx]:
			if data_pair["mp4"] != "":
				## check
				if data_pair["mp4"] not in test_mp4s:
					check.append(data_pair["mp4"])

	print(len(check))
	print("real: {}, fake: {}".format(real, fake))

def main(args):
	if args.package3:
		package3(args)
	elif args.phase2_test:
		phase2_test(args)
	elif args.check:
		check(args)

if __name__ == "__main__":
	args = parse_args()
	main(args)