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
#	-source_file no_covid_3.txt \
#	-reply_file no_covid_3_reply.txt

############
## Step 3 ##
############
python code/twitter_crawler.py \
	-app_name FakeNewsGIF3 \
	-find_gif true \
	-reply_file no_covid_3_reply.txt \
	-gif_reply_file no_covid_3_gif_reply.txt \
	-gif_dir no_covid_3_gif_tweets
#python code/twitter_crawler.py -rewrite_gif_tweets true

############
## Step 4 ##
############
#python code/twitter_crawler.py -fetch_gif true