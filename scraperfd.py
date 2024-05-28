import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def remove_ordinal_suffix(date_str):
    return re.sub(r'(\d)(st|nd|rd|th)', r'\1', date_str)

def fetch_page_data(url):
    response = requests.get(url)
    topics = []

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        topic_items = soup.find_all('li', class_='row topic')

        for topic in topic_items:
            title_anchor = topic.find('a', class_='topic_title_link')
            retailer_anchor = topic.find('a', class_='topictitle_retailer')
            total_count_dd = topic.find('dd', class_='total_count')
            first_post_time_span = topic.find('span', class_='first-post-time')
            
            if title_anchor and retailer_anchor and total_count_dd and first_post_time_span:
                retailer_name = retailer_anchor.text.strip()
                topic_title = title_anchor.text.strip()
                total_count = int(total_count_dd.text.strip().replace(',', ''))  # Remove commas and convert to int
                first_post_time_str = first_post_time_span.text.strip()
                
                # Remove ordinal suffix from the date string
                first_post_time_str = remove_ordinal_suffix(first_post_time_str)
                
                # Convert first_post_time to a datetime object
                first_post_time = datetime.strptime(first_post_time_str, '%b %d, %Y %I:%M %p')

                topics.append((retailer_name, topic_title, total_count, first_post_time))

    return topics

# Base URL of the forum
base_url = "https://forums.redflagdeals.com/hot-deals-f9/"

# Collect data from the first 6 pages (including the first page)
all_topics = []
for page_num in range(1, 5):
    url = f"{base_url}{page_num}/?st=0&rfd_sk=tt&sd=d"
    all_topics.extend(fetch_page_data(url))

# Remove duplicates
unique_topics = list({(retailer_name, topic_title, total_count, first_post_time) for retailer_name, topic_title, total_count, first_post_time in all_topics})

# Sort the topics by first-post-time in descending order
sorted_topics = sorted(unique_topics, key=lambda x: x[3], reverse=True)

# Print the sorted topics
for retailer_name, topic_title, total_count, first_post_time in sorted_topics:
    formatted_topic = f"{retailer_name} <-> {topic_title} <-> [[{total_count}]]"
    print(formatted_topic)
