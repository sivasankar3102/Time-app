from flask import Flask, jsonify
import requests
import re
from datetime import datetime

app = Flask(__name__)

@app.route('/getTimeStories', methods=['GET'])
def get_time_stories():
    url = 'https://time.com'
    response = requests.get(url)
    
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch the webpage'}), 500

    html_content = response.text

    stories = extract_stories(html_content)
    stories.sort(key=lambda x: x['date'], reverse=True)

    latest_stories = stories[:6]
    for story in latest_stories:
        del story['date']

    return jsonify(latest_stories)

def extract_stories(html):
    stories = []
    start_marker = '<article class="slide">'
    end_marker = '</article>'
    start_index = 0

    while start_index != -1:
        start_index = html.find(start_marker, start_index)
        if start_index == -1:
            break

        end_index = html.find(end_marker, start_index) + len(end_marker)
        article_html = html[start_index:end_index]
        start_index = end_index
        title = extract_title(article_html)
        url = extract_url(article_html)
        date = extract_date(article_html)

        if title and url and date:
            stories.append({
                'title': title,
                'url': url,
                'date': date
            })

    return stories

def extract_title(html_content):
    match = re.search(r'<h3 class="title no-eyebrow">([^<]+)</h3>', html_content)
    if match:
        return match.group(1).strip()
    return "Title not found"

def extract_url(html_content):
    match = re.search(r'href="(/[^"]+)"', html_content)
    if match:
        relative_url = match.group(1).strip()
        return f'https://time.com{relative_url}'
    return "URL not found"

def extract_date(html_content):
    match = re.search(r'<time class="timestamp published-date display-inline">([^<]+)</time>', html_content)
    if match:
        date_str = match.group(1).strip()
        try:
            return datetime.strptime(date_str, '%B %d, %Y • %I:%M %p EDT')
        except ValueError:
            return None
    return None

if __name__ == '__main__':
    app.run(debug=True)
