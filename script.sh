##################
## Fetch Source ##
##################
#python code/main_crawler.py -fetch_source true -data_type with_FakeNews -date_dir 20210415 -query "(#FakeNews) min_replies:5 lang:en"
#python code/main_crawler.py -fetch_source true -query "covid (#FakeNews) min_replies:5 lang:en"
#python code/main_crawler.py -fetch_source true -data_type wo_FakeNews -date_dir 20210330 -query "min_replies:5 lang:en"

###################
## Fetch Replies ##
###################
#python code/main_crawler.py -install_chrome_driver true
#python3 code/main_crawler.py \
#	-fetch_replies true \
#	-source_file source.txt \
#	-reply_file reply.txt

##############
## Find GIF ##
##############
#python code/main_crawler.py \
#	-app_name AgainstRumor \
#	-date_dir 20210415 \
#	-find_gif true \
#	-reply_file reply.json \
#	-part 0
#
#
#python code/main_crawler.py \
#	-app_name AgainstRumor \
#	-find_gif true \
#	-reply_file no_covid_4_reply.txt \
#	-gif_reply_file no_covid_4_gif_reply.txt \
#	-gif_dir no_covid_4_gif_tweets
#python code/main_crawler.py -rewrite_gif_tweets true

###############
## Fetch GIF ##
###############
#python code/main_crawler.py -fetch_gif true -date_dir 20210413 -part 0
#python code/main_crawler.py -fetch_gif true -date_dir 20210301

####################
## Get GIF Source ##
####################
#python code/main_crawler.py -get_gif_source true

#######################
## Write Source Text ##
#######################
#python code/main_crawler.py -write_source_text true

################
## Statistics ##
################
#python code/statistics.py -gif_source_total_reply true -date_dir 20210217
#python code/statistics.py -gif_source_total_reply true -date_dir 20210218
#python code/statistics.py -gif_source_total_reply true -date_dir 20210301
#python code/statistics.py -total_count true -date_dir 20210217
#python code/statistics.py -total_count true -date_dir 20210218
#python code/statistics.py -total_count true -date_dir 20210301
#python code/statistics.py -count_by_txt true

#python code/statistics.py -count_miss_gif true -date_dir 20210217
#python code/statistics.py -count_miss_gif true -date_dir 20210218
#python code/statistics.py -count_miss_gif true -date_dir 20210301

#python code/statistics.py -insert_missing true -date_dir 20210217
#python code/statistics.py -insert_missing true -date_dir 20210218
#python code/statistics.py -insert_missing true -date_dir 20210301

#python code/statistics.py -read_final_and_test true
#python code/statistics.py -detect_source true
#python code/statistics.py -check true
#python code/statistics.py -package2 true
#python code/statistics.py -count_package2 true
python code/statistics.py -phase1_from_package2 true

#################
## Data Format ##
#################
#python code/data_format.py -txt2json true -date_dir 20210415 -txt_file reply.txt -json_file reply.json
#python code/data_format.py -txt2json true -date_dir 20210217 -txt_file gif_reply.txt -json_file gif_reply.json
#python code/data_format.py -txt2json true -date_dir 20210218 -txt_file reply.txt -json_file reply.json
#python code/data_format.py -txt2json true -date_dir 20210218 -txt_file gif_reply.txt -json_file gif_reply.json
#python code/data_format.py -txt2json true -date_dir 20210218 -txt_file all_gif_reply.txt -json_file all_gif_reply.json
#python code/data_format.py -txt2json true -date_dir 20210301 -txt_file reply.txt -json_file reply.json
#python code/data_format.py -txt2json true -date_dir 20210301 -txt_file gif_reply.txt -json_file gif_reply.json
#python code/data_format.py -txt2json true -date_dir 20210301 -txt_file all_gif_reply.txt -json_file all_gif_reply.json

#python code/data_format.py -all2json true -date_dir 20210217 -json_file_index 0 -app_name AgainstRumor
#python code/data_format.py -all2json true -date_dir 20210218 -app_name AgainstRumor
#python code/data_format.py -all2json true -date_dir 20210301

#python code/data_format.py -write10json true -date_dir 20210217 -json_file all_gif_reply.json

#python code/data_format.py -final_format true -date_dir 20210217
#python code/data_format.py -final_format true -date_dir 20210218
#python code/data_format.py -final_format true -date_dir 20210301
#python code/data_format.py -final_format true
#python code/data_format.py -from_EmotionGIF true
#python code/data_format.py -for_lab1 true
#python code/data_format.py -merge true
#python code/data_format.py -split_context_GIF true

#python code/data_format.py -remove_corrupted_mp4 true
#python code/data_format.py -merge10txt true

###########################
## Label mp4s categories ##
###########################
#python code/label_gif.py -merge_mp4s true
#python code/label_gif.py -mp4_frames true
#python code/label_gif.py -gif_frames true
#python code/label_gif.py -find_similar_img true -part 0
#python code/label_gif.py -construct_categories_table true
#python code/label_gif.py -merge_EmotionGIF_mp4s true
#python code/label_gif.py -merge_10_json true
#python code/label_gif.py -analyze_FakeNewsGIF_labels true
#python code/label_gif.py -label_from_EmotionGIF true -part 0
#python code/label_gif.py -label_from_top100 true -part 0
#python code/label_gif.py -write2gold true
#python code/label_gif.py -arrange_mp4_files true

########################################
## Crawl top 100 GIF of each category ##
########################################
#python code/top100GIF.py -fetch_100GIF_file true -part 0