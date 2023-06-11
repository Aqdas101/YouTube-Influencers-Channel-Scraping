from googleapiclient.discovery import build
import streamlit as st
import pandas as pd
from streamlit import session_state
from time import sleep
from google.cloud import firestore
import json
from google.oauth2 import service_account
from datetime import datetime




def scrap(category, max_result):
    api_key = st.secrets['api_key']
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    request = youtube.search().list(
    part='snippet',
    type='channel',
    maxResults= max_result,
    order='videoCount',
    q = category,
    #topicId = categories[category]
    #location='US'
    )
    
    response = request.execute()
    
    channel_ids = [i['id']['channelId'] for i in response['items']]
    channel_links = [f'https://www.youtube.com/channel/{i}' for i in channel_ids ]
    channel_title = [i['snippet']['title'] for i in response['items']]
    channel_created = [i['snippet']['publishedAt'] for i in  response['items']]
    
    channel_stats = []
    for id in channel_ids:
        channel_stat = youtube.channels().list(
            part ='statistics',
            id = id
        ).execute()
        channel_stats.append(channel_stat)
        
    view_count = [i['items'][0]['statistics']['viewCount'] for i in  channel_stats]
    total_subs = [i['items'][0]['statistics']['subscriberCount'] for i in channel_stats]
    total_videos = [i['items'][0]['statistics']['videoCount'] for i in channel_stats]
    
    my_channels = []
    for title, date, subs, views, videos, link in zip(channel_title, channel_created, total_subs, view_count, total_videos, channel_links):  
        channel = [title, date, subs, views, videos, link]
        my_channels.append(channel)
        
    return my_channels

def user_feedback():
    key_dict = json.loads(st.secrets['textkey'])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds)
    
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<br><br><br>', unsafe_allow_html=True)
        st.markdown(
            "<h3 style='text-align: center;'>Would you like to share some quick feedback?</h3>",
            unsafe_allow_html=True
        )
#         st.image('feedback.png', width=150)
        with st.spinner():
            if st.button('Let Us Know'):
                st.success("Thank you so much for the feedback")
                doc_ref = db.collection('my_feedbacks').document(str(datetime.now()))
                doc_ref.set({'Name': name, 'feedback': feedback})

    with col2:
        name = st.text_input('Please enter your name')
        feedback = st.text_area('Provide your feedback')


    return name, feedback

def main():
    if 'df' not in session_state:
        session_state['df'] = None
    st.set_page_config(page_title='Youtube influencers Data Scrapper')
    st.title("Hi! I'm your YouTube scraper")

    def text_input(placeholder):
        input_text = st.text_input(placeholder)
        return input_text
    
    col1 , col2 = st.columns(2)
    
    with col1:
        category = text_input('Type of channel')
    with col2: 
        num_channels = st.number_input('Number of records',value=0, step=100, max_value=100, format="%d")
    
    col1,col2 = st.columns(2)
    
    df = None
    
    with col1: 
        if st.button('Extract'):
            with st.spinner('Please Wait'):
                channels = scrap(category, num_channels)
                session_state['df'] = pd.DataFrame(channels,
                                  columns=['Channel Name', 'Creation Date', 'Subscribers', 'Total Views', 'Total Videos', 'link'])
                st.balloons()
                st.success(f'Congrats! You successfully scrap {num_channels} channels!')
                st.dataframe(session_state['df'])
    with col2:
        if 'df' in session_state and session_state['df'] is not None:
            if st.button('Generate CSV'):
                progress_bar = st.progress(0)
                sleep(1)
                progress_bar.progress(40)
                sleep(1)
                progress_bar.progress(100)
                st.download_button(
                    label = 'Download CSV',
                    data = session_state['df'].to_csv().encode('utf-8'),
                    file_name = f'{category}.csv',
                    mime='text/csv'
                )
                st.success(f'CSV file "{category}.csv" generated successfully!')
                
    st.markdown("<br><br><br>", unsafe_allow_html=True)
                
    name, feedback = user_feedback()
                
              
                
main()
