# =============================================
# ZIPSTER™ 2025 – FINAL WORKING VERSION
# HomeSchool Village Bot – FREE TIER SAFE
# Created by David X Gordon + Grok 3
# November 06, 2025 – THIS ONE RUNS FOREVER
# =============================================

import tweepy
import time
import re
import os

print("ZIPSTER™ 2025 BOOT SEQUENCE INITIATED")

# === ENV VARS ===
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
COMMUNITY_NAME = os.getenv("COMMUNITY_NAME", "HomeSchool Village")

# === CLIENT ===
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET,
    wait_on_rate_limit=True
)

offers = []
requests = []
seen_ids = set()

def extract(text):
    tag_match = re.search(r'#(Request|Offer|Meetup|RideTo|Venue|Group)\s*([^\s#]+)?', text, re.I)
    day_match = re.search(r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)', text, re.I)
    zip_match = re.search(r'\b(\d{5}(?:-\d{1,4}XX?|-\d{4})?)\b', text)
    location = zip_match.group(1) if zip_match else "87507"
    return {
        "skill": (tag_match.group(2) or "general").strip().lower() if tag_match else "general",
        "day": day_match.group(1) if day_match else "Any",
        "location": location,
        "type": tag_match.group(1).lower() if tag_match else ""
    }

print(f"Zipster™ 2025 LIVE in {COMMUNITY_NAME} | Ready to match")

if __name__ == "__main__":
    while True:
        try:
            query = 'context:community_id:1983369684708950288 (#Request OR #Offer OR #Meetup OR #RideTo OR #Group) lang:en -is:retweet'
            tweets = client.search_recent_tweets(query=query, max_results=10, tweet_fields=['author_id', 'conversation_id'])

            if not tweets.data:
                time.sleep(60)
                continue

            for tweet in tweets.data:
                tweet_id = tweet.id
                if tweet_id in seen_ids:
                    continue
                seen_ids.add(tweet_id)

                user = client.get_user(id=tweet.author_id).data
                username = user.username
                info = extract(tweet.text)

                # === BUILD ZIP TAG ===
                city = "SantaFe"
                zip_code = info["location"][:5] if info["location"][:5].isdigit() else "87507"
                reply_text = f"#{city} #{zip_code} [Location]"

                # === COMMUNITY CHECK ===
                is_community = False
                root_id = tweet.conversation_id if hasattr(tweet, 'conversation_id') else tweet_id
                if root_id != tweet_id:  # ← THIS IS != NOT ≠
                    try:
                        root = client.get_tweet(root_id, tweet_fields=['context_annotations'])
                        if root.data and root.data.context_annotations:
                            for ann in root.data.context_annotations:
                                if ann.get('type') == 'Community':
                                    is_community = True
                                    break
                    except:
                        pass

                # === POST ZIP TAG ===
                try:
                    if is_community:
                        client.create_tweet(text=reply_text, quote_tweet_id=tweet_id)
                        print(f"QUOTE-TWEETED: {tweet_id}")
                    else:
                        client.create_tweet(text=reply_text, in_reply_to_tweet_id=tweet_id, auto_populate_reply_metadata=True)
                        print(f"REPLIED: {tweet_id}")
                except Exception as e:
                    print(f"Post failed: {e}")

                # === OFFERS ===
                if info["type"] in ["offer", "venue", "group"]:
                    offers.append({**info, "user": username, "id": tweet_id})
                    msg = f"@{username} Added to village! {info['skill'].title()} on {info['day']} in {info['location']} #HSV"
                    try:
                        if is_community:
                            client.create_tweet(text=msg, quote_tweet_id=tweet_id)
                        else:
                            client.create_tweet(text=msg, in_reply_to_tweet_id=tweet_id, auto_populate_reply_metadata=True)
                    except: pass

                # === REQUESTS ===
                elif info["type"] in ["request", "meetup", "rideto"]:
                    requests.append({**info, "user": username, "id": tweet_id})
                    matches = [
                        o for o in offers
                        if (info["skill"] in o["skill"] or o["skill"] in info["skill"])
                        and (info["day"] == "Any" or o["day"] == "Any" or info["day"].lower() in o["day"].lower())
                        and (
                            '-' in info["location"] and o["location"].startswith(info["location"].split('-')[0])
                            or o["location"] == info["location"]
                        )
                    ]
                    if matches:
                        match_list = " | ".join([f"@{m['user']}" for m in matches[:3]])
                        reply = f"@{username} Found {len(matches)} match(es)! {match_list} → DM them! #HSV"
                    else:
                        reply = f"@{username} Logged! We'll notify when match appears #HSV"

                    try:
                        if is_community:
                            client.create_tweet(text=reply, quote_tweet_id=tweet_id)
                        else:
                            client.create_tweet(text=reply, in_reply_to_tweet_id=tweet_id, auto_populate_reply_metadata=True)
                    except: pass

            time.sleep(60)

        except Exception as e:
            print(f"Main error: {e}")
            time.sleep(60)