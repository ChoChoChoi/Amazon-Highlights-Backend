# Install the packages
# !pip install --upgrade google-api-python-client
# !pip install oauth2client
# !pip install -U yt-dlp
# !pip install ffmpeg

# Import the packages
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.tools import argparser
import youtube_dl
import os

# YouTube API Parameter
def build_youtube_search(developer_key):
    DEVELOPER_KEY = developer_key
    YOUTUBE_API_SERVICE_NAME="youtube"
    YOUTUBE_API_VERSION="v3"
    return build(YOUTUBE_API_SERVICE_NAME,YOUTUBE_API_VERSION,developerKey=DEVELOPER_KEY)
    
# Search Parameter
def get_search_response(youtube):
  search_response = youtube.search().list(
    order = "date",
    part = "snippet",
    maxResults = 2,
    channelId = "UCdoadna9HFHsxXWhafhNvKw"
    ).execute()
  return search_response
  
  
# Get Video Info
def get_video_info(search_response):
  result_json = {}
  idx =0
  for item in search_response['items']:
    if item['id']['kind'] == 'youtube#video':
      result_json[idx] = info_to_dict(item['id']['videoId'], item['snippet']['title'], item['snippet']['description'], item['snippet']['publishedAt'])
      idx += 1
  return result_json

# Convert into dict
def info_to_dict(videoId, title, description, date):
  result = {
      "videoId": videoId,
      "title": title,
      "description": description,
      "date": date
  }
  return result
  
# Get Video ID
def get_video_id(search_response):
    video_id = []
    for item in search_response['items']:
         video_id.append(item['id']['videoId'])
    return video_id
    
# Download video - https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/__init__.py
def download_video(video_id):
    url = 'https://youtube.com/watch?v='
    output = os.path.join('./', '%(title)s.%(ext)s')
    for id in video_id:
        video = str(url+id)
        ydl_opts = {
            'format' : 'bestaudio/best',
            'nocheckcertificate' : 'True',
            'outtmpl' : output,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',

            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video])
            
        print(video + ': Download Completed')
        
# Main
youtube = build_youtube_search("AIzaSyAvZuCRcx7sWA-OUiPjkml_Xv3F4aNXGEc")
response = get_search_response(youtube)
id_list = get_video_id(response)
download_video(id_list)