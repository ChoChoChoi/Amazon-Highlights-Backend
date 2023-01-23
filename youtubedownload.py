# Required packages
# (1) Add layer - https://aws.amazon.com/ko/premiumsupport/knowledge-center/lambda-import-module-error-python/
# (2) CDK requirements
# !pip install --upgrade google-api-python-client
# !pip install oauth2client
# !pip install -U yt-dlp
# !pip install ffmpeg

# Import the packages
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.tools import argparser
from botocore.exceptions import ClientError
import os
import subprocess
import boto3
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

# connect s3
s3 = boto3.client('s3')
bucket = 'youtubeweekly'
# BUCKET_ARN = os.environ['BUCKET_ARN']

# YouTube DATA API v3 Parameter - https://developers.google.com/youtube/v3/docs/
def build_youtube_search(developer_key):
    DEVELOPER_KEY = developer_key
    YOUTUBE_API_SERVICE_NAME="youtube"
    YOUTUBE_API_VERSION="v3"
    return build(YOUTUBE_API_SERVICE_NAME,YOUTUBE_API_VERSION,developerKey=DEVELOPER_KEY)
    
# Search Parameter
def get_search_response(youtube, lastcall):
  search_response = youtube.search().list(
    order = "date",
    part = "snippet",
    publishedAfter = lastcall,
    maxResults = 10,
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
    # output = os.path.join('/tmp/youtubevideos/', '%(title)s.%(ext)s')
    for id in video_id:
      subprocess.call('yt-dlp -f bestvideo+bestaudio --merge-output-format mp4 https://www.youtube.com/watch\?v\='+id, shell="True")
    # for id in video_id:
    #     video = str(url+id)
    #     ydl_opts = {
    #         'format' : 'bestaudio/best',
    #         'nocheckcertificate' : 'True',
    #         'postprocessors': [{
    #           'key': 'FFmpegExtractAudio',
    #           'preferredcodec': 'mp3',
    #           'preferredquality': '320',
    #       }],
    #         'outtmpl' : output,
    #     }
    #     with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    #         ydl.download([video])
            
    #     print(video + ': Download Completed')

# upload file to s3 - need to add permission
def upload_file(file_name, bucket, key, object_name=None):

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    try:
        # response = s3.put_object(Bucket=bucket, Key=key+'/'+file_name)
        response = s3.upload_file(file_name, bucket, key+'/'+object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True
    

#def lambda_handler(event, context):

# get the date 7 days ago 
d = datetime.now() + relativedelta(days=-7)
lastcall = str(d.isoformat('T'))[0:19] + 'Z'

t = datetime.now()
today = str(t.isoformat('T'))[0:19] + 'Z'
    
# get video info
youtube = build_youtube_search("AIzaSyAvZuCRcx7sWA-OUiPjkml_Xv3F4aNXGEc")
video_info = get_search_response(youtube, lastcall)
video_id = get_video_id(video_info)

# make a directory
if not os.path.exists(os.path.join(today)):
 os.makedirs(today)

# change current directory (default: /var/task)
os.chdir(today)

# download video - Time out
download_video(video_id)
tmp = os.listdir('./')

# upload video to s3 - Need multi part upload (more than 100 MB)
for item in tmp:
  upload_file(item, bucket, today, item)
    
# Remove video
os.chdir('..')
subprocess.call('sudo rm -rf '+today, shell="True")
    #return tmp
