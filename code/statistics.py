import argparse

def parse_args():
	parser = argparse.ArgumentParser(description="Statistics of FakeNewsGIF")
	parser.add_argument("-result_path", type=str, default="/mnt/hdd1/joshchang/datasets/FakeNewsGIF/results")

	args=parser.parse_args()
	
	return args

def statistics(args):
	def count(input_path, source_list, reply_list, not_accessed_list):
		f = open(input_path, "r")
		lines = f.readlines()
		f.close()

		flag = 0
		for line in lines:
			line = line.strip().rstrip()
			type, id = line.split("\t")[0], line.split("\t")[1]
			if type == "source":
				if id not in not_accessed_list:
					source_list.append(id)
					flag = 1
				else:
					flag = 0
			if type == "reply" and flag == 1:
				reply_list.append(id)

		return source_list, reply_list

	## Read not accessed source ids
	input_path = "{}/source/no_covid_gif_source_not_accessed.txt".format(args.result_path)
	f = open(input_path, "r")
	lines = f.readlines()
	f.close()

	no_covid_not_accessed_list = []
	for line in lines:
		source_id = line.strip().rstrip()
		no_covid_not_accessed_list.append(source_id)

	input_path = "{}/source/covid_gif_source_not_accessed.txt".format(args.result_path)
	f = open(input_path, "r")
	lines = f.readlines()
	f.close()

	covid_not_accessed_list = []
	for line in lines:
		source_id = line.strip().rstrip()
		covid_not_accessed_list.append(source_id)
	

	source_path = "{}/reply".format(args.result_path)
	## no_covid
	print("---no_covid---")
	source_list, reply_list = [], []
	input_path = "{}/no_covid_gif_reply.txt".format(source_path)
	source_list, reply_list = count(input_path, source_list, reply_list, no_covid_not_accessed_list)

	print("# of source (gif): {}".format(len(source_list)))
	print("# of reply  (gif): {}".format(len(reply_list)))

	## covid
	print("---covid---")
	source_list, reply_list = [], []
	input_path = "{}/covid_gif_reply.txt".format(source_path)
	source_list, reply_list = count(input_path, source_list, reply_list, covid_not_accessed_list)

	print("# of source (gif): {}".format(len(source_list)))
	print("# of reply  (gif): {}".format(len(reply_list)))

if __name__ == "__main__":
	args = parse_args()
	statistics(args)
	