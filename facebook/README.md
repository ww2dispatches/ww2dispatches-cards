# Facebook queue

One JSON file per posting day (`YYYY-MM-DD.json`) with the day's 8 a.m. still card: `date`, `dispatch`, `image` (the 1080 x 1350 card), and `caption` (the long story caption plus #OnThisDay #WW2).

A Make scenario runs every morning at 8 a.m. Mountain, fetches today's file from raw.githubusercontent.com, and posts the photo with its caption to the WW2 Dispatches Facebook Page. No file means no post.

Built by `python3 renderer/facebook_queue.py <first-day> <last-day>`, which the Friday batch runs for the coming week. Facebook gets one post a day (the 8 a.m. dispatch); noon living cards and second dispatches stay on X, Instagram, and Threads.
