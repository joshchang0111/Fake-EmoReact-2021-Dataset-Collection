##################
## Fetch Source ##
##################
#python code/twitter_crawler.py -fetch_source true -query "(#FakeNews) min_replies:5 lang:en"
#python code/twitter_crawler.py -fetch_source true -query "covid (#FakeNews) min_replies:5 lang:en"

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
#python code/statistics.py -total_count true
#python code/statistics.py -count_by_txt true