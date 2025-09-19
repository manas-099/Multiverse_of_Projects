from googleapiclient.discovery import build
from dotenv import load_dotenv
load_dotenv
import os
you_tube_api_key=os.getenv("YOUTUBE_API_KEY")

youtube = build("youtube", "v3", developerKey=you_tube_api_key)

request = youtube.search().list(
    part="snippet",
    q="mcp",
    maxResults=2
)
response = request.execute()
print("---"*50)
print(response)
print("---"*50)

for item in response["items"]:
    print(item["snippet"]["title"])
