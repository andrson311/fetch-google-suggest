import os
import string
import json
import requests
import argparse
import pandas as pd

import nltk
nltk.download('stopwords')

from nltk.corpus import stopwords

ROOT = os.path.dirname(__file__)

def get_suggestions(keywords):
    
    char_list = list(string.ascii_lowercase)
    headers = {'User-agent': 'Mozilla/5.0'}

    keyword_suggestions = []
    for keyword in keywords:
        for char in char_list:
            url = f"http://suggestqueries.google.com/complete/search?client=firefox&hl=en&q={keyword} {char}"
            response = requests.get(url, headers=headers)
            result = json.loads(response.content.decode('utf-8'))
            
            keyword_suggestions.append(keyword)
            for word in result[1]:
                if word != keyword:
                    keyword_suggestions.append(word)
    
    return list(set(keyword_suggestions))

def cluster_keywords(keywords, seed_words):

    _words = []
    stop_words = list(set(stopwords.words('english')))
    
    for keyword in keywords:
        words = nltk.word_tokenize(str(keyword).lower())
        for word in words:
            if (word not in stop_words 
                and not any(word in s for s in seed_words) 
                and len(word) > 1):
                _words.append(word)
    
    top_common_words = [word for word, word_count in nltk.Counter(_words).most_common(200)]

    clusters = []

    for common_word in top_common_words:
        for keyword in keywords:
            if (common_word in str(keyword)):
                clusters.append([keyword, common_word])
    
    df = pd.DataFrame(clusters, columns=['Keyword', 'Cluster'])
    df.to_csv(os.path.join(ROOT, 'keywords.csv'), index=False)

def list_of_items(arg):
    return arg.split(',')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Returns suggested long tail keywords from Google.'
    )

    parser.add_argument(
        '-k',
        '--keywords',
        type=list_of_items,
        required=True,
        help='List of seed keywords'
    )

    args = parser.parse_args()
    seed_words = args.keywords
    
    suggestions = get_suggestions(seed_words)
    cluster_keywords(suggestions, seed_words)


