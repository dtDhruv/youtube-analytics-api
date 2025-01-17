from googleapiclient.discovery import build
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_channel_stats(youtube, channel_id):
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    )
    response = request.execute()
    return response['items']

def get_video_list(youtube, upload_id):
    video_list = []
    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=upload_id,
        maxResults=50
    )
    next_page = True
    while next_page:
        response = request.execute()
        data = response['items']

        for video in data:
            video_id = video['contentDetails']['videoId']
            if video_id not in video_list:
                video_list.append(video_id)

        # Do we have more pages?
        if 'nextPageToken' in response.keys():
            next_page = True
            request = youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=upload_id,
                pageToken=response['nextPageToken'],
                maxResults=50
            )
        else:
            next_page = False

    return video_list

def get_video_details(youtube, video_list):
    stats_list=[]

    # Can only get 50 videos at a time.
    for i in range(0, len(video_list), 50):
        request= youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_list[i:i+50]
        )

        data = request.execute()
        for video in data['items']:
            title=video['snippet']['title']
            published=video['snippet']['publishedAt']
            description=video['snippet']['description']
            # tag_count= len(video['snippet']['tags'])
            view_count=video['statistics'].get('viewCount',0)
            like_count=video['statistics'].get('likeCount',0)
            dislike_count=video['statistics'].get('dislikeCount',0)
            comment_count=video['statistics'].get('commentCount',0)
            stats_dict=dict(title=title, description=description, published=published, view_count=view_count, like_count=like_count, dislike_count=dislike_count, comment_count=comment_count)
            stats_list.append(stats_dict)

    return stats_list

def get_data(CHANNEL_ID):
    channel_stats = get_channel_stats(youtube, CHANNEL_ID)
    upload_id = channel_stats[0]['contentDetails']['relatedPlaylists']['uploads']
    video_list = get_video_list(youtube, upload_id)
    video_data = get_video_details(youtube, video_list)
    df=pd.DataFrame(video_data)
    df['title_length'] = df['title'].str.len()
    df["view_count"] = pd.to_numeric(df["view_count"])
    df["like_count"] = pd.to_numeric(df["like_count"])
    df["dislike_count"] = pd.to_numeric(df["dislike_count"])
    df["comment_count"] = pd.to_numeric(df["comment_count"])
    df["reactions"] = df["like_count"] + df["dislike_count"] + df["comment_count"] + df["comment_count"]
    df.to_csv("data.csv")
    
