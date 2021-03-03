############
## Step 1 ##
############
#python code/twitter_crawler.py -fetch_source true -query "(#FakeNews) min_replies:5 lang:en"
#python code/twitter_crawler.py -fetch_source true -query "covid (#FakeNews) min_replies:5 lang:en"

############
## Step 2 ##
############
#python code/twitter_crawler.py -install_chrome_driver true
python3 code/twitter_crawler.py \
	-fetch_replies true \
	-source_file source.txt \
	-reply_file reply.txt

############
## Step 3 ##
############
python code/twitter_crawler.py \
	-app_name AgainstRumor \
	-find_gif true \
	-reply_file reply.txt \
	-gif_reply_file gif_reply.txt \
	-gif_dir gif_reply
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
#python code/statistics.py -total_count true
#python code/statistics.py -count_by_txt true

#######################
## write source text ##
#######################
#python code/twitter_crawler.py -write_source_text true