import nltk
nltk.download('averaged_perceptron_tagger')
from wordcloud import WordCloud
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag
import random
import re
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.nlp.tokenizers import Tokenizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from flask import Flask, request, jsonify, after_this_request, url_for
import os
from collections import Counter
import pandas as pd
import uuid
from flask_cors import CORS , cross_origin
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# rest of your imports and code...

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "/Users/deepakrawat/Desktop/Anusandhan/static"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to remove stop words
def remove_stop_words(text):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text)
    filtered_words = [word for word in words if word.lower() not in stop_words]
    filtered_text = ' '.join(filtered_words)
    return filtered_text

def filter_stopwords(tokens):
    # Download the stopwords if they haven't been downloaded already
    if not nltk.corpus.stopwords.words('english'):
        nltk.download('stopwords')
    
    # Filter out the stopwords
    filtered_tokens = [token for token in tokens if token.lower() not in nltk.corpus.stopwords.words('english')]
    
    return filtered_tokens

# Function to filter non-zero compound score tokens
def filter_nonzero_compound_score(tokens):
    sia = SentimentIntensityAnalyzer()
    filtered_tokens = [token for token in tokens if sia.polarity_scores(token)['compound'] != 0]
    return filtered_tokens

# Function to filter negative compound score tokens
def filter_negative_compound_score(tokens):
    sia = SentimentIntensityAnalyzer()
    filtered_tokens = [token for token in tokens if sia.polarity_scores(token)['compound'] > 0]
    word_counts = Counter(filtered_tokens)
    top_5_positive_words = word_counts.most_common(5)
    top_5_positive_words_dict = dict(top_5_positive_words)
    return top_5_positive_words_dict

# Function to filter positive compound score tokens
def filter_positive_compound_score(tokens):
    sia = SentimentIntensityAnalyzer()
    filtered_tokens = [token for token in tokens if sia.polarity_scores(token)['compound'] < 0]
    word_counts = Counter(filtered_tokens)
    top_5_negative_words = word_counts.most_common(5)
    top_5_negative_words_dict = dict(top_5_negative_words)
    return top_5_negative_words_dict

# Function to extract nouns, adjectives, and verbs
def get_nouns_adjectives_verbs(word_list):
    tagged_words = pos_tag(word_list)
    nouns_adjectives_verbs = [word for word, tag in tagged_words if tag in ['NN', 'JJ', 'VB']]
    return nouns_adjectives_verbs

# Function to return dictionary of most frequent words
def most_frequent_words(tokens, num_most_frequent=5):
    word_count_dict = {}
    for token in tokens:
        if token in word_count_dict:
            word_count_dict[token] += 1
        else:
            word_count_dict[token] = 1
    
    most_frequent_words_dict = dict(sorted(word_count_dict.items(), key=lambda item: item[1], reverse=True)[:num_most_frequent])
    return most_frequent_words_dict

# Function to return dictionary of least frequent words
def least_frequent_words(tokens, num_most_frequent=5):
    word_count_dict = {}
    for token in tokens:
        if token in word_count_dict:
            word_count_dict[token] += 1
        else:
            word_count_dict[token] = 1
    
    most_frequent_words_dict = dict(sorted(word_count_dict.items(), key=lambda item: item[1], reverse=False)[:num_most_frequent])
    return most_frequent_words_dict

# positive wordcloud
def wordcloud_positive(word_count_dict, file_path):
    words = list(word_count_dict.keys())
    counts = list(word_count_dict.values())
    wordcloud = WordCloud(width=800, height=400, background_color='white', max_words=100, colormap='winter').generate_from_frequencies(word_count_dict)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig(file_path, bbox_inches='tight')
    plt.close()
    
# negative wordcloud
def wordcloud_negative(word_count_dict, file_path):
    words = list(word_count_dict.keys())
    counts = list(word_count_dict.values())
    wordcloud = WordCloud(width=800, height=400, background_color='white', max_words=100, colormap='hot').generate_from_frequencies(word_count_dict)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig(file_path, bbox_inches='tight')
    plt.close()

# create a horizontal barplot
def horizontal_barplot_high(word_count_dict, file_path):
    words = list(word_count_dict.keys())
    counts = list(word_count_dict.values())
    sorted_words_counts = sorted(word_count_dict.items(), key=lambda x: x[1], reverse=True)
    sorted_words = [word[0] for word in sorted_words_counts]
    sorted_counts = [word[1] for word in sorted_words_counts]
    num_bars = min(10, len(sorted_words))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(sorted_words[:num_bars], sorted_counts[:num_bars], color='limegreen')
    ax.set_title('Horizontal Bar Plot of Words and Their Counts', fontsize=14)
    ax.set_xlabel('Counts', fontsize=12)
    ax.set_ylabel('Words', fontsize=12)
    ax.tick_params(axis='y', which='major', labelsize=10, rotation=0)
    ax.grid(axis='x', color='lightgray', linestyle='--')
    plt.savefig(file_path, bbox_inches='tight')
    plt.close()  




# create a horizontal barplot
def horizontal_barplot_low(word_count_dict, file_path):
    words = list(word_count_dict.keys())
    counts = list(word_count_dict.values())
    sorted_words_counts = sorted(word_count_dict.items(), key=lambda x: x[1], reverse=True)
    sorted_words = [word[0] for word in sorted_words_counts]
    sorted_counts = [word[1] for word in sorted_words_counts]
    num_bars = min(10, len(sorted_words))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(sorted_words[:num_bars], sorted_counts[:num_bars], color='crimson')
    ax.set_title('Horizontal Bar Plot of Words and Their Counts', fontsize=14)
    ax.set_xlabel('Counts', fontsize=12)
    ax.set_ylabel('Words', fontsize=12)
    ax.tick_params(axis='y', which='major', labelsize=10, rotation=0)
    ax.grid(axis='x', color='lightgray', linestyle='--')
    plt.savefig(file_path, bbox_inches='tight')
    plt.close()          
    
# add punctuations    
def add_punctuation(text, punctuation_chance=0.1):
    punctuations = ['.']
    modified_text = ''
    for word in re.findall(r"[\w']+|[.,!?;:]", text):
        modified_text += word
        if word not in punctuations and random.random() < punctuation_chance:
            modified_text += random.choice(punctuations)
        modified_text += ' '
    return modified_text.strip()

# add punctuation
def before_I(text):
    words = text.split()
    modified_text = []
    for word in words:
        if word.lower() == 'i':
            modified_text.append('.')
        modified_text.append(word)
    return ' '.join(modified_text)


#text summary
def summarize_text(text, num_sentences=3):
    
    tokenizer = Tokenizer('english')
    # Create a PlaintextParser object
    parser = PlaintextParser.from_string(text, tokenizer)
    # Initialize the LsaSummarizer
    summarizer = LsaSummarizer()
    # Get the summary
    summary = summarizer(parser.document, num_sentences)
    # Format the summary as a string
    text_summary = ''
    for sentence in summary:
        text_summary += str(sentence) + ' '

    return text_summary
 
@app.route('/barplot/high', methods=['POST'])
def barplot_high():
    if request.method == 'POST':
        text = request.form.get('text')
        if text:
            clean_data = remove_stop_words(text)
            tokens = word_tokenize(clean_data)
            significant_words = get_nouns_adjectives_verbs(tokens)
            filtered_tokens = filter_nonzero_compound_score(significant_words)
            word_frequencies = most_frequent_words(filtered_tokens)
            
            @after_this_request
            def add_barplot_high(response):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], str(uuid.uuid4()) + '.png')
                horizontal_barplot_high(word_frequencies, file_path)
                
                # Modify the graph URL to include the local host address and port
                graph_url = 'http://localhost:5090/static/' + os.path.basename(file_path)
                
                return jsonify({'status': 'success', 'word_frequencies': word_frequencies, 'graph_url': graph_url})
            return jsonify({'status': 'error', 'message': 'Failed to create graph'})

@app.route('/barplot/low', methods=['POST'])
def barplot_low():
    if request.method == 'POST':
        text = request.form.get('text')
        if text:
            clean_data = remove_stop_words(text)
            tokens = word_tokenize(clean_data)
            significant_words = get_nouns_adjectives_verbs(tokens)
            filtered_tokens = filter_nonzero_compound_score(significant_words)
            word_frequencies = least_frequent_words(filtered_tokens)
            
            @after_this_request
            def add_barplot_low(response):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], str(uuid.uuid4()) + '.png')
                horizontal_barplot_low(word_frequencies, file_path)
                
                # Modify the graph URL to include the local host address and port
                graph_url = 'http://localhost:5090/static/' + os.path.basename(file_path)
                
                return jsonify({'status': 'success', 'word_frequencies': word_frequencies, 'graph_url': graph_url})
            return jsonify({'status': 'error', 'message': 'Failed to create graph'})

@app.route('/wordcloud/pos', methods=['POST'])
def wordcloud_pos():
    if request.method == 'POST':
        text = request.form.get('text')
        if text:
            clean_data = remove_stop_words(text)
            tokens = word_tokenize(clean_data)
            word_frequencies = filter_negative_compound_score(tokens)
            
            @after_this_request
            def add_wordcloud_pos(response):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], str(uuid.uuid4()) + '.png')
                wordcloud_positive(word_frequencies, file_path)
                
                # Modify the graph URL to include the local host address and port
                graph_url = 'http://localhost:5090/static/' + os.path.basename(file_path)
                
                return jsonify({'status': 'success', 'word_frequencies': word_frequencies, 'graph_url': graph_url})
            return jsonify({'status': 'error', 'message': 'Failed to create graph'})

@app.route('/wordcloud/neg', methods=['POST'])
@cross_origin(origins='http://localhost:5173')
def wordcloud_neg():
    if request.method == 'POST':
        text = request.form.get('text')
        if text:
            clean_data = remove_stop_words(text)
            tokens = word_tokenize(clean_data)
            word_frequencies = filter_positive_compound_score(tokens)
            
            @after_this_request
            def add_wordcloud_neg(response):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], str(uuid.uuid4()) + '.png')
                wordcloud_negative(word_frequencies, file_path)
                
                # Modify the graph URL to include the local host address and port
                graph_url = 'http://localhost:5090/static/' + os.path.basename(file_path)
                
                return jsonify({'status': 'success', 'word_frequencies': word_frequencies, 'graph_url': graph_url})
            return jsonify({'status': 'error', 'message': 'Failed to create graph'})

@app.route('/text', methods=['POST'])
def text():
    if request.method == 'POST':
        text = request.form.get('text')
        if text:
            summary = before_I(text) 
            return jsonify({'status': 'success', 'summary': summary})
    return jsonify({'status': 'error', 'message': 'No text provided'})

@app.route('/text/summ', methods=['POST'])
def text_summ():
    if request.method == 'POST':
        text = request.form.get('text')
        if text:
            punc = before_I(text) 
            summary = summarize_text(punc)
            return jsonify({'status': 'success', 'word_frequencies': summary})
    return jsonify({'status': 'error', 'message': 'No text provided'})

if __name__ == '__main__':
    app.run(debug=True, port=5090)