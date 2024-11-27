import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import pytz

def remove_ordinal_suffix(date_str):
    return re.sub(r'(\d)(st|nd|rd|th)', r'\1', date_str)

def fetch_page_data(url):
    # print(f"Fetching data from URL: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    topics = []

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        topic_items = soup.find_all('li', class_='row topic')

        for topic in topic_items:
            title_anchor = topic.find('a', class_='topic_title_link')
            retailer_anchor = topic.find('a', class_='topictitle_retailer')
            if not retailer_anchor:
                retailer_anchor = topic.find('h3', class_='topictitle')
                if retailer_anchor:
                    retailer_text = retailer_anchor.text.strip()
                    retailer_text = re.sub(r'\s*\(merged\)\s*', '', retailer_text, flags=re.IGNORECASE)
                    retailer_anchor.string = re.search(r'\[(.*?)\]', retailer_text).group(1) if re.search(r'\[(.*?)\]', retailer_text) else retailer_text
            total_count_dd = topic.find('dd', class_='total_count')
            first_post_time_span = topic.find('span', class_='first-post-time')
            holiday_anchor = topic.find('a', class_='topictitle_holiday')
            
            if title_anchor and retailer_anchor and first_post_time_span:
                retailer_name = retailer_anchor.text.strip()
                topic_title = title_anchor.text.strip()
                total_count = int(total_count_dd.text.strip().replace(',', '')) if total_count_dd else 0  # Remove commas and convert to int, default to 0 if None
                first_post_time_str = first_post_time_span.text.strip()
                
                # Remove ordinal suffix from the date string
                first_post_time_str = remove_ordinal_suffix(first_post_time_str)
                
                # Convert first_post_time to a datetime object
                first_post_time = datetime.strptime(first_post_time_str, '%b %d, %Y %I:%M %p')
                
                # Assume the original time is in EST and convert it to PST timezone
                est = pytz.timezone('America/New_York')
                pst = pytz.timezone('America/Los_Angeles')
                first_post_time_est = est.localize(first_post_time)
                first_post_time_pst = first_post_time_est.astimezone(pst)

                holiday_name = holiday_anchor.text.strip() if holiday_anchor else "N/A"
                topics.append((retailer_name, topic_title, total_count, first_post_time_pst, holiday_name))
                # print(f"Added topic: {retailer_name} <-> {topic_title} <-> [[{total_count}]] at {first_post_time_pst.strftime('%Y-%m-%d %I:%M %p %Z')}")

    else:
        print(f"Failed to fetch data from URL: {url} with status code: {response.status_code}")

    return topics

# Base URL of the forum
base_url = "https://forums.redflagdeals.com/hot-deals-f9/"

# Collect data from the first 6 pages (including the first page)
all_topics = []
for page_num in range(1, 7):
    if page_num == 1:
        url = f"{base_url}?c=-5121&rfd_sk=tt"
    else:
        url = f"{base_url}{page_num}/?c=-5121&rfd_sk=tt"
    all_topics.extend(fetch_page_data(url))

# Remove duplicates
unique_topics = list({(retailer_name, topic_title, total_count, first_post_time, holiday_name) for retailer_name, topic_title, total_count, first_post_time, holiday_name in all_topics})

# Sort the topics by first-post-time in descending order
sorted_topics = sorted(unique_topics, key=lambda x: x[3], reverse=True)

# Print the sorted topics
print("Sorted topics by first-post-time:")
for retailer_name, topic_title, total_count, first_post_time, holiday_name in sorted_topics:
    formatted_topic = f"{retailer_name} <-> {topic_title} <-> [[{total_count}]] <-> {first_post_time.strftime('%Y-%m-%d %I:%M %p %Z')} <-> {holiday_name}"
    print(formatted_topic)

# Sort the topics by total_count in descending order and print the top 10
sorted_by_total_count = sorted(unique_topics, key=lambda x: x[2], reverse=True)
print("\nTop 10 topics with highest scores:")
for retailer_name, topic_title, total_count, first_post_time, holiday_name in sorted_by_total_count[:10]:
    formatted_topic = f"{retailer_name} <-> {topic_title} <-> [[{total_count}]] <-> {first_post_time.strftime('%Y-%m-%d %I:%M %p %Z')} <-> {holiday_name}"
    print(formatted_topic)

# Print all Black Friday topics
black_friday_topics = [topic for topic in unique_topics if topic[4] == "Black Friday"]
print("\nAll Black Friday topics:")
for retailer_name, topic_title, total_count, first_post_time, holiday_name in black_friday_topics:
    formatted_topic = f"{retailer_name} <-> {topic_title} <-> [[{total_count}]] <-> {first_post_time.strftime('%Y-%m-%d %I:%M %p %Z')} <-> {holiday_name}"
    print(formatted_topic)