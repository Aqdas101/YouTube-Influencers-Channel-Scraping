#!/usr/bin/env python
# coding: utf-8

# In[29]:


import os
from googleapiclient.discovery import build
import csv


# # User Input

# In[65]:


api = input('Please Input your API key: ')
target_subscriber_count = int(input('Please enter the minimum subcribers limit: '))
num_channels = int(input('Please enter the number of channels link you want to get: '))
category = input('Input category name, if multiple categories, seprate them with comma: ')
# category = input('''
# Please select from any of these categories:
# - music
# - gaming
# - sports
# - comedy
# - education
# - news
# - technology
# - fashion
# - travel
# - science 
# - productivity

# ''')


# # Extraction

# In[67]:


def get_channels_by_subscriber_count(target_subscriber_count, category, num_channels, api):
    api_key = api
    youtube = build('youtube', 'v3', developerKey=api_key)
    
#     categories = {'music' : '/m/04rlf', 'gaming' : '/m/0bzvm2', 
#               'sports' : '/m/06ntj', 'comedy' : '/m/09kqc', 'education' : '/m/02jj',
#              'news' : '/m/056j4', 'technology' : '/m/07c1v', 'fashion' : '/m/03glg',
#               'travel' : '/m/07bxq', 'science' : '/m/0bzvm2', 'productivity' : '/m/0283dt1',
#             'film: /m/02vxn', 'animation: /m/05q4t', 'pets and animals' : '/m/068hy', ''
#              }
    
    
    result_channels = []  # To store the resulting YouTube channels
    total_channels = 0  # Counter for the number of channels found
    
    while total_channels < num_channels:
        # Call the API to search for channels in the specified category
        request = youtube.search().list(
            part='snippet',
            type='channel',
            maxResults=50,
            order='videoCount',
            q = category
#             topicId = categories[category]
#             location='US'
            
        )
        response = request.execute()
        
        for item in response['items']:
            channel_id = item['id']['channelId']
            
            # Call the API to retrieve channel statistics
            channel_response = youtube.channels().list(
                part='statistics',
                id=channel_id
            ).execute()
            
            # Get the subscriber count for the channel
            subscriber_count = int(channel_response['items'][0]['statistics']['subscriberCount'])
            
            # Filter channels based on subscriber count (target threshold)
            if subscriber_count >= target_subscriber_count:
                
                total_channels += 1
                channel_title = item['snippet']['title']
                channel_link = f'https ://www.youtube.com/channel/{channel_id}'
                
                result_channels.append({
                    'title': channel_title,
                    'link': channel_link,
                    'subscriber_count': subscriber_count
                })
                
                if total_channels == num_channels:
                    break
        
        if 'nextPageToken' in response:
            request = youtube.search().list_next(request, response)
        else:
            break
    
    return result_channels


# # Main

# In[68]:


def main(target_subscriber_count, category, num_channels, api):
    category = category.split(',')
    category = [i.strip() for i in category]
    category = [i.lower() for i in category]
    
    for find_cat in category:    
        channels = get_channels_by_subscriber_count(target_subscriber_count, find_cat , num_channels, api)
        my_channels = []
        for channel in channels:
            my_channels.append(channel['link'])
        with open(f'{find_cat}.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            for links in my_channels:
                writer.writerow([links])
            
    return 'Congratulations! Scraped Successfully'


# In[69]:


main(target_subscriber_count,category,num_channels, api)


# In[ ]:





# In[ ]:




