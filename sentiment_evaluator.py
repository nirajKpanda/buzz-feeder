import re
import sys
import json
import math
import string
import vincent
import operator 
import collections
from nltk import bigrams
from nltk.corpus import stopwords
from collections import defaultdict


try:
    fname = sys.argv[1] 
except Exception as e:
    print('Input file name where tweet streams are stored not provided.Hence exiting....')
    sys.exit(0)

emoticons_str = r"""
    (?:
        [:=;] # Eyes
        [oO\-]? # Nose (optional)
        [D\)\]\(\]/\\OpP] # Mouth
    )"""
 
regex_str = [
    emoticons_str,
    r'<[^>]+>', # HTML tags
    r'(?:@[\w_]+)', # @-mentions
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)", # hash-tags
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', # URLs 
    r'(?:(?:\d+,?)+(?:\.?\d+)?)', # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])", # words with - and '
    r'(?:[\w_]+)', # other words
    r'(?:\S)' # anything else
]

    
tokens_re = re.compile(r'('+'|'.join(regex_str)+')', re.VERBOSE | re.IGNORECASE)
emoticon_re = re.compile(r'^'+emoticons_str+'$', re.VERBOSE | re.IGNORECASE)

# add code to remove unicde as well
punctuation = list(string.punctuation)
stop = stopwords.words('english') + punctuation + ['rt', 'via']

def tokenize(s):
    return tokens_re.findall(s)
 
def preprocess(s, lowercase=False):
    tokens = tokenize(s)
    if lowercase:
        tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
    return tokens

# com : document frequency for the co-occurrences 
com = defaultdict(lambda : defaultdict(int))

# tokenizing tweets dump collected for the given query 
# finding most common terms on twiter for a common discussion or trend or hashtag
with open(fname, 'r') as f:
    count_all = collections.Counter()
    # n_docs is the total number of tweets/dataset
    # exception_lines variable to hold how many tweets been ignore due to bad config
    # from which sentiment to be evaluated
    n_docs, exception_lines = 0, 0
    for line in f:
        try:
            tweet = json.loads(line)
            # Create a list with all the terms
            terms_all = [ 
                term 
                for term in preprocess(tweet['text']) 
                if term not in stop or term.isalpha()
            ]
            
            # Build co-occurrence matrix
            for i in range(len(terms_all)-1):            
                for j in range(i+1, len(terms_all)):
                    w1, w2 = sorted([terms_all[i], terms_all[j]])
                    if w1 != w2:
                        com[w1][w2] += 1

            # Update the counter
            count_all.update(terms_all)
            n_docs += 1
        except (json.decoder.JSONDecodeError, KeyError) as e:
            exception_lines += 1
            continue


# sentiment analysis code satrts from here
# count_single : document frequency for single terms was stored in the dictionaries
# count_stop_single : document frequency for single terms was stored in the dictionaries
# (doesn’t store stop-words in count_stop_single)
# p_t : probabilities of terms found
# p_t_com : probalities based on co-ocurences matrices
p_t = {}
p_t_com = defaultdict(lambda : defaultdict(int))
 
for term, n in count_all.items():
    p_t[term] = n / n_docs
    for t2 in com[term]:
        p_t_com[term][t2] = com[term][t2] / n_docs


# declaring semantic operations positive & negative
positive_vocab = [
    'good', 'nice', 'great', 'awesome', 'outstanding',
    'fantastic', 'terrific', ':)', ':-)', 'like', 'love',
    'triumph', 'triumphal', 'triumphant', 'victory'
    # shall we also include game-specific terms?
]

negative_vocab = [
    'bad', 'terrible', 'crap', 'useless', 'hate', ':(', ':-(', 'defeat' 
]


# calculating pmi(Pointwise Mutual Information)
pmi = defaultdict(lambda : defaultdict(int))
for t1 in p_t:
    for t2 in com[t1]:
        try:
            denom = p_t[t1] * p_t[t2]
            pmi[t1][t2] = math.log2(p_t_com[t1][t2] / denom)
        except KeyError as e:
            continue
 
semantic_orientation = {}

for term, n in p_t.items():
    positive_assoc = sum(pmi[term][tx] for tx in positive_vocab)
    negative_assoc = sum(pmi[term][tx] for tx in negative_vocab)
    semantic_orientation[term] = positive_assoc - negative_assoc

# viewing semantic orientation as per our requirement
semantic_sorted = sorted(semantic_orientation.items(), 
                         key=operator.itemgetter(1), 
                         reverse=True)
top_pos = semantic_sorted[:10]
top_neg = semantic_sorted[-10:]
print('Top positive tweeet terms : \n {}'.format(top_pos[:10]))
print('Top negative tweeet terms : \n {}'.format(top_neg[:10]))

# TODO
# for insight vizualization with vincent
#labels, freq = zip(*word_freq)
#data = {'data': freq, 'x': labels}
#bar = vincent.Bar(data, iter_idx='x')
#bar.to_json('term_freq.json')
#bar.to_json('term_freq.json', html_out=True, html_path='chart1.html')

# TODO
# make the output more interactive