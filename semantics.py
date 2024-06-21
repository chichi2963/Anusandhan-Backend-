import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from flask import Flask, request, jsonify, after_this_request, url_for
from collections import Counter
import pandas as pd
import uuid
import networkx as nx
import os
from flask_cors import CORS , cross_origin
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# rest of your imports and code...

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "/Users/deepakrawat/Desktop/Anusandhan/static"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_first_word(sentence):
    words = sentence.split()
    return words[0]

def list_of_words_to_string(word_list):
    return " ".join(word_list)

def get_rest(sentence):
    words = sentence.split()
    str_str = list_of_words_to_string(words[1:])
    return str_str


def find_closest_tags(s, target_word):
    
    tokens = word_tokenize(s)
    tagged_tokens = pos_tag(tokens)
    stop_words = set(stopwords.words('english'))
    tagged_tokens = [(word, tag) for word, tag in tagged_tokens if word not in stop_words and word.isalpha()]
    target_index = tokens.index(target_word)
    closest_tags = []
    for i in range(-3, 4):
        word_index = target_index + i
        if 0 <= word_index < len(tagged_tokens):
            word, tag = tagged_tokens[word_index]
            if tag in ['NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'JJ', 'JJR', 'JJS']:
                closest_tags.append(word)
                if len(closest_tags) == 3:
                    break

    return closest_tags
    
def plot_string_connections(file_path, target_string, string_list):

    G = nx.DiGraph()
    G.add_node(target_string)
    for string in string_list:
        G.add_node(string)

    for string in string_list:
        G.add_edge(target_string, string)

    pos = nx.spring_layout(G)  # Positions for all nodes
    nx.draw(G, pos, with_labels=True, node_size=1000, node_color="skyblue", font_size=10, font_weight="bold")
    plt.savefig(file_path)
    plt.close() 

@app.route('/semantic', methods=['POST'])
@cross_origin(origins='http://localhost:5173')
def semantic_analysis():
    if request.method == 'POST':
        text = request.form.get('text')
        if text:
            sentiment_word = get_first_word(text)
            corpse = get_rest(text)
            next_3 = find_closest_tags(corpse, sentiment_word) 
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], str(uuid.uuid4()) + '.png')
            plot_string_connections(file_path, sentiment_word, next_3)
            
            # Generate URL for the graph
            graph_url = url_for('static', filename=os.path.basename(file_path), _external=True)
            
            return jsonify({'status': 'success', 'closest_words': next_3, 'graph_url': graph_url})
    return jsonify({'status': 'error', 'message': 'No text provided'})

if __name__ == '__main__':
    app.run(debug=True, port=5091)