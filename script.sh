##################
## Fetch Source ##
##################
#python code/twitter_crawler.py -fetch_source true -query "(#FakeNews) min_replies:5 lang:en"
#python code/twitter_crawler.py -fetch_source true -query "covid (#FakeNews) min_replies:5 lang:en"
#python code/twitter_crawler.py -fetch_source true -date_dir 20210310 -query "min_replies:5 lang:en"

###################
## Fetch Replies ##
###################
#python code/twitter_crawler.py -install_chrome_driver true
#python3 code/twitter_crawler.py \
#	-fetch_replies true \
#	-source_file source.txt \
#	-reply_file reply.txt

##############
## Find GIF ##
##############
#python code/twitter_crawler.py \
#	-app_name AgainstRumor \
#	-find_gif true \
#	-reply_file reply.txt \
#	-gif_reply_file gif_reply.txt \
#	-gif_dir gif_reply
#
#
#python code/twitter_crawler.py \
#	-app_name AgainstRumor \
#	-find_gif true \
#	-reply_file no_covid_4_reply.txt \
#	-gif_reply_file no_covid_4_gif_reply.txt \
#	-gif_dir no_covid_4_gif_tweets
#python code/twitter_crawler.py -rewrite_gif_tweets true

###############
## Fetch GIF ##
###############
#python code/twitter_crawler.py -fetch_gif true -date_dir 20210218
#python code/twitter_crawler.py -fetch_gif true -date_dir 20210301

####################
## Get GIF Source ##
####################
#python code/twitter_crawler.py -get_gif_source true

#######################
## Write Source Text ##
#######################
#python code/twitter_crawler.py -write_source_text true

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

#################
## Data Format ##
#################
#python code/data_format.py -txt2json true -date_dir 20210217 -txt_file reply.txt -json_file reply.json
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

###########################
## Label mp4s categories ##
###########################
#python code/label_gif.py -merge_mp4s true
#python code/label_gif.py -mp4_frames true
#python code/label_gif.py -find_similar_img true -part 0
#python code/label_gif.py -construct_categories_table true
#python code/label_gif.py -merge_EmotionGIF_mp4s true
#python code/label_gif.py -merge_10_json true
python code/label_gif.py -analyze_FakeNewsGIF_labels true
#python code/label_gif.py -labeling_mp4s true -part 0