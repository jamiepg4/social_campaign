#!/home/ubuntu/social_campaign/venv/bin/python
# coding: utf-8

# In[76]:

#connect in terminal
#ssh -NL 27017:127.0.0.1:27017 fusion 

#import libraries
import datetime
from datetime import timedelta,datetime
import dateutil.relativedelta
import numpy as np
import pandas as pd
import plotly 
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import plotly.plotly as py
from plotly.graph_objs import *
from plotly.offline import download_plotlyjs, init_notebook_mode, iplot
import plotly.tools as tls
import requests
#from IPython.display import HTML
import json
from pandas.io.json import json_normalize
import time
from slackclient import SlackClient


# In[77]:

#set options
#%config IPCompleter.greedy=True
#pd.set_option('display.max_colwidth', -1)
#pd.set_option('display.max.row', 999)


# In[78]:

#set inline plotting
#%matplotlib inline
#plotly.offline.init_notebook_mode()
#plot matplot plots with plotly
mpl_fig_obj = plt.figure()


# In[79]:

py.sign_in("kstohr", "token")


# ## Get Timeseries Data

# In[80]:

#crowdtangle token
tokenID = 'token'


# In[81]:

#hard set end date 
#now = datetime(2016, 7, 29, 0, 13, 52, 87892)


# In[82]:

#set parameters 
url = 'https://api.crowdtangle.com/leaderboard'
acctIDs = [48801, 148861] #Donald Trump, #Hillary Clinton
now = datetime.now()
period = 60
start = (now - dateutil.relativedelta.relativedelta(days=period)).strftime('%Y-%m-%d')
rng = pd.date_range(start, periods=period, freq='d')


# In[83]:

start_week = (now - dateutil.relativedelta.relativedelta(days=7)).strftime('%Y-%m-%d')
end_week = now.strftime('%Y-%m-%d')
week = 7 


# In[89]:

data = []

try:
	for date in rng: 
		end = date+1
		payload = {'accountIds': acctIDs, 'token': tokenID, 'startDate': date.strftime('%Y-%m-%d'), 'endDate': end.strftime('%Y-%m-%d')}
		r = requests.get(url = url, params = payload)
		response = json_normalize(r.json()['result']['accountStatistics'])
		response['Date'] = date
		data.append(response)
		time.sleep(2.1)

	frames=[]
	for row in data:
		frames.append(pd.DataFrame(row))
		results = pd.concat(frames).reset_index().drop('index', axis = 1)

except ValueError: 
	token = 'xoxb-53518431175-kg1TAOzyOBsdoXxCMZxbVe7J'
	channel = '#edit-elections-data'
	sc = SlackClient(token)
	sc.api_call(
	"chat.postMessage", 
	channel=channel, 
	text="The Candidates Social Media Weekly Update: There has been an error retrieving the data from Crowdtangle", 
	as_user = True,
	username='tinker', 
	unfurl_links = 'true', 
	unfurl_media = 'true'
	)


# In[29]:

colors = {
	'Hillary Clinton': "rgb(31,120,180)", #blue
	'Bernie Sanders': "rgb(166,206,227)", #lt. blue
	'Donald J. Trump': "rgb(204,102,153)" #rasperry
}


# In[30]:

candidate_list = pd.unique(results['account.name'].ravel())


# In[31]:

#create plot.ly chart 
df = results


traces_likes = [] # the series in the graph - one trace for each candidate

for candidate in candidate_list:
		traces_likes.append({
				'x': df[df['account.name']==candidate]['Date'], 
				'y': df[df['account.name']==candidate]['summary.likeCount'].map('{:,.0f}'.format),
				#'text': 'Likes', 
				'name' : candidate,
				'mode': 'lines+markers',
				#'visible': visibility.get(candidate),
				'line': Line(color = colors.get(candidate)),
				'hoverinfo' : "name+x+y",
				'yaxis' : 'y','xaxis' : 'x', 
				'showlegend': False
				})

traces_shares = [] # the series in the graph - one trace for each candidate

for candidate in candidate_list:
		traces_shares.append({
				'x': df[df['account.name']==candidate]['Date'], 
				'y': df[df['account.name']==candidate]['summary.shareCount'].map('{:,.0f}'.format),
				#'text': 'Shares', 
				'name' : candidate,
				'mode': 'lines+markers',
				#'visible': visibility.get(candidate),
				'line': Line(color = colors.get(candidate)),
				'hoverinfo' : "name+x+y",
				'yaxis' : 'y','xaxis' : 'x', 
				'showlegend': False
				})

traces_posts = []

for candidate in candidate_list:
		traces_posts.append(go.Bar(
				 x = df[df['account.name']==candidate]['Date'], 
				 y = df[df['account.name']==candidate]['summary.postCount'].map('{:,.0f}'.format),
				 text = 'Posts', 
				 name =	 candidate,
				 #mode =  bar
				#'visible': visibility.get(candidate),
				 marker = Marker(color = colors.get(candidate)),
				 yaxis='y2', 
				 xaxis = 'x2', 
				#'hoverinfo' : "text+name+x"
				))

annotations = [

		#likes per day
		dict(
			x=.5,
			y=1.02,
			xref='paper',
			yref='paper',
			text='<b>Number of Likes</b>',
			font = dict(size = 14),
			showarrow=False,
		), 


		#shares per day
		dict(
			x=.5,
			y=.6,
			xref='paper',
			yref='paper',
			text='<b>Number of Shares</b>',
			font = dict(size = 14),
			showarrow=False,
		), 
		#posts per day 
		dict(
			x=.5,
			y=.18,
			xref='paper',
			yref='paper',
			text='<b>Number of Posts</b>',
			font = dict(size = 14),
			showarrow=False,
		),

		#Source
		dict(
			x=0,
			y=-.2,
			xref='paper',
			yref='paper',
			text="Last updated: "+end_week,
			showarrow=False,
			align='left',
		),
	]

#demarcate past week with a line
shapes = [{
			'type': 'line',
			'x0': start_week,
			'y0': 0,
			'x1': start_week,
			'y1': 1,
			'xref': 'x',
			'yref': 'paper',
			'line': {
				'color': 'rgb(128, 0, 128)',
				'width': 3,
				'dash': 'dot',}
	}, 
		 {
			'type': 'rect',
			'x0': start,
			'y0': 0,
			'x1': start_week,
			'y1': 1,
			'xref': 'x',
			'yref': 'paper',
			'fillcolor': 'rgba(224, 224, 220, 0.3)',	
			'line': {
				'color': 'rgba(224, 224, 220, 0.3)',
				'width': 1,
		}
	}
		 ]


# In[32]:

date = now.strftime('%Y-%m-%d')

fig = tls.make_subplots(rows=5, 
						cols=1, 
						specs=[[{'rowspan': 2}], [None],[{'rowspan': 2}],[None], [{}]],
						shared_xaxes=True, 
						shared_yaxes=False,
						vertical_spacing=0.01)

for trace in traces_likes: 
	fig.append_trace(trace, 1, 1)

for trace in traces_shares: 
	fig.append_trace(trace, 3, 1)
	
for trace in traces_posts: 
	fig.append_trace(trace, 5, 1)

fig['layout'].update(height=750, 
					 width=600, 
					 #yaxis = dict(showticklabels = True), 
					 yaxis2 = dict(showticklabels = True), 
					 title = "Candidates' Popularity on Facebook", 
					 showlegend = True, 
					 legend = dict(orientation= "v", 
								   x=.95,
								   y=1, 
								   bgcolor='rgba(224, 224, 220, 0.0)'),
					 margin= Margin(l=30, r=30, b=110, t=80, pad=10),
					 annotations = annotations, 
					 shapes = shapes
					 )

chart = py.plot(fig, filename='social_campaign/'+date+'-candidate_interactions_per_day')

# In[33]:

#save png file of chart
#chart = date+'-candidate_interactions_per_day.png'
#py.image.save_as(fig, chart)


# ## Top Posts

# In[34]:

#open mongodb connection
from pymongo import MongoClient 
client = MongoClient()


# In[35]:

#SET A SPECIFIC END DATE
#end = now
#end


# In[36]:

#set start date
period = 7 
end = datetime.now() 
start = now - dateutil.relativedelta.relativedelta(days=period)

# In[37]:

#select candidates
greenlist = ['clinton', 'trump']


# In[38]:

#query database
try: 
	db = client.scrape2
	input_data = db.posts
	data = pd.DataFrame(list(input_data.find(
				{"$and": [{"created_at": {"$gte": start}},{"created_at": {"$lte": end}},{"candidate": {"$in": greenlist}}]},
				{"first_seen_at":0, "media": 0, "raw":0, "popularity_history":0} 
			)
							))


	#unnest nested fields 
	#pull "popularity" field, reimport as dataframe
	pop = pd.DataFrame(list(data.popularity))

	#cbind unnested "popularity" table with dataframe
	df = pd.concat([data, pop], axis=1)
	df = df.drop('popularity', axis =1)

except ValueError: 
	token = 'xoxb-53518431175-kg1TAOzyOBsdoXxCMZxbVe7J'
	channel = '#edit-elections-data'
	sc = SlackClient(token)
	sc.api_call(
	"chat.postMessage", 
	channel=channel, 
	text="The Candidates Social Media Weekly Update: There has been an error retrieving the data from Scraper2/MongoDB", 
	as_user = True,
	username='tinker', 
	unfurl_links = 'true', 
	unfurl_media = 'true'
	)

# In[40]:

pop_week = df


# In[41]:

#get time since post created
hours = now - pop_week['created_at']
#convert to hours elapsed 
pop_week['time'] = hours/timedelta(hours=1)
#get number of hours in a week 
period_d = 7*24
#adj engagement = number of likes * (time since post/hours in period)*weight
pop_week['adj_engagement'] = (pop_week.likes*(1/pop_week.time)*(pop_week.time/period_d)*1)+							(pop_week.shares*(1/pop_week.time)*(pop_week.time/period_d)*1)+(pop_week.comments*(1/pop_week.time)*(pop_week.time/period_d)*.25)
		
pop_week['total_engagement'] = pop_week.likes + pop_week.shares + pop_week.comments


# In[42]:

pop_week.loc[:,'created_date'] = list(pop_week.loc[:,'created_at'].values.astype('datetime64[D]'))


# In[43]:

platforms = pd.unique(pop_week.platform.ravel())


# ## Get Top YouTube Posts

# In[44]:

yt_week = pop_week[pop_week['platform'] == 'youtube']


# In[45]:

#Most pop vid of the week
yt_week.loc[:,'likes_per_time'] = yt_week['dislikes'] / yt_week['time']

#trump most pop vid
trump_vids = yt_week[yt_week['candidate'] == 'trump']
trump_most_pop_vid = trump_vids[trump_vids['likes_per_time'] == trump_vids.likes_per_time.max()]

#clinton most pop vid
clinton_vids = yt_week[yt_week['candidate'] == 'clinton']
clinton_most_pop_vid = clinton_vids[clinton_vids['likes_per_time'] == clinton_vids.likes_per_time.max()]


# ## Get Top Facebook Posts

# In[46]:

#remove other platforms
pop_week = pop_week[pop_week['platform'] == 'facebook']


# In[61]:

#trump avg total daily engagement 
trump_posts = pop_week[pop_week['candidate'] == 'trump']
trump_by_day = trump_posts.groupby('created_date')['total_engagement'].sum()


# In[62]:

#trump avg likes per post 
trump_by_post = trump_posts.groupby('created_at')['total_engagement'].mean()


# In[63]:

#trump weekly total likes
trump_wkly_total = trump_posts['likes'].sum()


# In[64]:

#clinton avg total daily engagement 
clinton_posts = pop_week[pop_week['candidate'] == 'clinton']
clinton_by_day = clinton_posts.groupby('created_date')['total_engagement'].sum()


# In[65]:

#clinton avg likes per post
clinton_by_post = clinton_posts.groupby('created_at')['total_engagement'].mean()


# In[66]:

#clinton weekly total likes
clinton_wkly_total = clinton_posts['likes'].sum()


# In[67]:

#create a table of the 10 posts with the most total interactions given the time period since it went live
pop_week.loc[:,'likes_per_time'] = pop_week['likes'] / pop_week['time']
top_posts = pop_week.sort_values(by='likes_per_time', ascending = False)[['created_at', 'candidate', 'likes', 'comments', 'shares', 'time', 'total_engagement', 'text', 'url']].head(10)


# In[68]:

#create bot text of top 10 posts 
top_posts_text = []
for i in range(len(top_posts)): 
		tr = str(top_posts.iloc[i, :].created_at) + '  '+ str(top_posts.iloc[i, :].total_engagement) + '  '+ str(top_posts.iloc[i, :].url)
		top_posts_text.append(tr)																						 


# In[69]:

#get the most liked posts for each candidate given the time period since it went live
top_clinton = pop_week[pop_week['candidate'] == 'clinton'].sort_values(by = 'likes_per_time', ascending = False).head(1)
top_trump = pop_week[pop_week['candidate'] == 'trump'].sort_values(by = 'likes_per_time', ascending = False).head(1)


# In[70]:

#get least shared candidate posts given the time period since it went live
least_clinton = pop_week[pop_week['candidate'] == 'clinton'].sort_values(by = 'likes_per_time', ascending = True).head(1)
least_trump = pop_week[pop_week['candidate'] == 'trump'].sort_values(by = 'likes_per_time', ascending = True).head(1)


# In[71]:

#get most shared candidate posts given the time period since it went live
pop_week.loc[:,'shares_per_time'] = pop_week['shares'] / pop_week['time']
shared_clinton = pop_week[pop_week['candidate'] == 'clinton'].sort_values(by = 'shares_per_time', ascending = False).head(1)
shared_trump = pop_week[pop_week['candidate'] == 'trump'].sort_values(by = 'shares_per_time', ascending = False).head(1)


# In[72]:

#get most commented candidate posts given the time period since it went live
pop_week.loc[:,'comments_per_time'] = pop_week['comments'] / pop_week['time']
comments_clinton = pop_week[pop_week['candidate'] == 'clinton'].sort_values(by = 'comments_per_time', ascending = False).head(1)
comments_trump = pop_week[pop_week['candidate'] == 'trump'].sort_values(by = 'comments_per_time', ascending = False).head(1)


# ### Check for null values and replace with error message

# In[73]:

post_links = [trump_most_pop_vid, clinton_most_pop_vid]
for i in post_links: 
	if len(i) == 0: 
		try:
			i.loc[0,'url'] = "No link available this week"
		except: 
			pass 

# ## Post to Bot

# In[74]:

# post to slack 

#top facebook and youtube posts 
attachment =  [
		{
		"fallback": "Links attached", 
		"author_name": "Facebook likes and shares for the week ending "+end_week+" (Plot.ly chart)",
		"author_icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Plotly_logo_for_digital_final_(6).png/220px-Plotly_logo_for_digital_final_(6).png",
		"text": 'https://plot.ly/organize/kstohr:792'
		},
		{
		"text": "Top posts reflect posts with the most likes/interactions given the time since posted"
		},
		{
		"fallback": "Links attached", 
		"title": "Most Liked YouTube video of the Week",
		"author_name": "Hillary Clinton",
		"author_icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/06/YouTube_logo_2013.svg/220px-YouTube_logo_2013.svg.png",
		"text": clinton_most_pop_vid.url.values[0]
		}, 
		{
		"fallback": "Links attached", 
		"title": "Most Liked YouTube video of the Week",
		"author_name": "Donald Trump",
		"author_icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/06/YouTube_logo_2013.svg/220px-YouTube_logo_2013.svg.png",
		"text": trump_most_pop_vid.url.values[0]
		}, 
		{
		"fallback": "Links attached", 
		"title": "Most Liked Post",
		"author_name": "Hillary Clinton",
		"author_icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/F_icon.svg/20px-F_icon.svg.png",
		"text": top_clinton.url.values[0] 
		}, 
		{
		"fallback": "Links attached", 
		"title": "Most Shared Post",
		"text": shared_clinton.url.values[0]
		}, 
		{
		"fallback": "Links attached", 
		"title": "Most Commented Post",
		"text": comments_clinton.url.values[0]
		},
		{
		"fallback": "Links attached", 
		"title": "Least Liked Post",
		"text": least_clinton.url.values[0]
		},
		{
		"fallback": "Links attached", 
		"title": "Avg Total Daily Interactions",
		"text": clinton_by_day.mean()
		},
		{
		"fallback": "Links attached", 
		"title": "Avg Likes Per Post",
		"text": clinton_by_post.mean()
		},
		{
		"fallback": "Links attached", 
		"title": "Weekly Total Likes",
		"text": clinton_wkly_total
		},
		{
		"fallback": "Links attached", 
		"title": "Most Liked Post",
		"author_name": "Donald Trump",
		"author_icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/F_icon.svg/20px-F_icon.svg.png",
		"text": top_trump.url.values[0]
		}, 
		{
		"fallback": "Links attached", 
		"title": "Most Shared Post",
		"text": shared_trump.url.values[0]
		}, 
		{
		"fallback": "Links attached", 
		"title": "Most Commented Post",
		"text": comments_trump.url.values[0]
		}, 
		{
		"fallback": "Links attached", 
		"title": "Least Liked Post",
		"text": least_trump.url.values[0]
		},
		{
		"fallback": "Links attached", 
		"title": "Avg Total Daily Interactions",
		"text": trump_by_day.mean()
		},	
		{
		"fallback": "Links attached", 
		"title": "Avg Likes Per Post",
		"text": trump_by_post.mean()
		},
		{
		"fallback": "Links attached", 
		"title": "Weekly Total Likes",
		"text": trump_wkly_total
		},
		{			
		"fallback": "Links attached", 
		"title": "Top 10 Candidate Facebook Posts (by total interaction)",
		"author_name": "Overall",
		"author_icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/F_icon.svg/20px-F_icon.svg.png",
		"text": str(top_posts_text),
		}
		]

attachment = json.dumps(attachment)

# In[75]:

#post top links 
token = ''
channel = '#edit-elections-data'
sc = SlackClient(token)
sc.api_call(
	"chat.postMessage", 
	channel=channel, 
	text="The Candidates Social Media Weekly Update", 
	attachments=attachment,
	as_user = True,
	username='tinker', 
	unfurl_links = 'true', 
	unfurl_media = 'true'
)

	
