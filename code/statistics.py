import argparse

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

	# other arguments
	parser.add_argument("-result_path", type=str, default="/mnt/hdd1/joshchang/datasets/FakeNewsGIF/results")
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
	source_list, reply_list = [], []
	input_path = "{}/reply/{}/gif_reply.txt".format(args.result_path, args.date_dir)
	source_list, reply_list = count(input_path, source_list, reply_list)

	print("# of source (gif): {}".format(len(source_list)))
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

def main(args):
	if args.total_count:
		total_count(args)
	elif args.gif_source_total_reply:
		gif_source_total_reply(args)
	elif args.count_by_txt:
		count_by_txt(args)

if __name__ == "__main__":
	args = parse_args()
	main(args)
	