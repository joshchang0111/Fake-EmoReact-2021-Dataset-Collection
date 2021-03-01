############
## Step 1 ##
############
#python code/twitter_crawler.py -fetch_source true -query "(#FakeNews) min_replies:5 lang:en"
#python code/twitter_crawler.py -fetch_source true -query "covid (#FakeNews) min_replies:5 lang:en"

############
## Step 2 ##
############
#python code/twitter_crawler.py -install_chrome_driver true
#python code/twitter_crawler.py \
#	-fetch_replies true \
#	-source_file no_covid_0.txt \
#	-reply_file no_covid_0_reply.txt

############
## Step 3 ##
############
#python code/twitter_crawler.py \
#	-app_name AgainstRumor \
#	-find_gif true \
#	-reply_file no_covid_0_reply.txt \
#	-gif_reply_file no_covid_0_gif_reply.txt \
#	-gif_dir no_covid_0_gif_tweets
#
#
#python code/twitter_crawler.py \
#	-app_name AgainstRumor \
#	-find_gif true \
#	-reply_file no_covid_4_reply.txt \
#	-gif_reply_file no_covid_4_gif_reply.txt \
#	-gif_dir no_covid_4_gif_tweets
#python code/twitter_crawler.py -rewrite_gif_tweets true

############
## Step 4 ##
############
#python code/twitter_crawler.py -fetch_gif true -gif_dir covid_gif_reply
#python code/twitter_crawler.py -fetch_gif true -gif_dir no_covid_gif_reply

################
## Statistics ##
################
#python code/statistics.py

#########################
## rewrite data format ##
#########################
#python code/twitter_crawler.py -rewrite_data_format true -reply_file covid_gif_reply.txt -gif_dir no_covid_gif_tweets -app_name AgainstRumor
#python code/twitter_crawler.py -rewrite_data_format true -reply_file no_covid_gif_reply.txt -gif_dir no_covid_gif_tweets -app_name FakeNewsGIF1
#python code/twitter_crawler.py -rewrite_data_format true -reply_file no_covid_0_gif_reply.txt -gif_dir no_covid_0_gif_tweets -app_name FakeNewsGIF2
#python code/twitter_crawler.py -rewrite_data_format true -reply_file no_covid_1_gif_reply.txt -gif_dir no_covid_1_gif_tweets -app_name FakeNewsGIF3
#python code/twitter_crawler.py -rewrite_data_format true -reply_file no_covid_2_gif_reply.txt -gif_dir no_covid_2_gif_tweets -app_name FakeNewsGIF4
#python code/twitter_crawler.py -rewrite_data_format true -reply_file no_covid_3_gif_reply.txt -gif_dir no_covid_3_gif_tweets -app_name FakeNewsGIF5
#python code/twitter_crawler.py -rewrite_data_format true -reply_file no_covid_4_gif_reply.txt -gif_dir no_covid_4_gif_tweets -app_name FakeNewsGIF6