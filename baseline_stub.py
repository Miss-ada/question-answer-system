#!/usr/bin/env python
'''
Created on May 14, 2014
@author: reid
Brian Schwarzmann, Ada Ma, and Nathaniel Suriawijaya
Modified on May 21, 2015
'''

import sys, nltk, operator, collections
from qa_engine.base import QABase
from dependency_demo_stubV1 import *
import gensim
import string
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
from collections import deque

model = gensim.models.KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)
#from word2vec_extractor import Word2vecExtractor
#w2vecextractor = Word2vecExtractor("GoogleNews-vectors-negative300.bin")
punct = set(string.punctuation)
porter = PorterStemmer()
wl = WordNetLemmatizer()

# The standard NLTK pipeline for POS tagging a document
def get_sentences(text):
    sentences = nltk.sent_tokenize(text)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    return sentences    

def get_answer(text):
    sentences = get_sentences(text)
    tagged_txt = " ".join(sentences)
    pass

def get_bow(tagged_tokens):
    stopwords = set(nltk.corpus.stopwords.words("english"))
    return set([t[0].lower() for t in tagged_tokens if t[0].lower() not in stopwords])

def find_phrase(tagged_tokens, qbow):
    for i in range(len(tagged_tokens) - 1, 0, -1):
        word = (tagged_tokens[i])[0]
        # print(word)
        if word in qbow:
            return tagged_tokens[i+1:]

# qtokens: is a list of pos tagged question tokens with SW removed
# sentences: is a list of pos tagged story sentences
# stopwords is a set of stopwords
def baseline(qbow, sentences):
    # Collect all the candidate answers
    answers = []
    for sent in sentences:
        # A list of all the word tokens in the sentence
        sbow = get_bow(sent)

        # print(sbow)
        # Count the # of overlapping words between the Q and the A
        # & is the set intersection operator
        overlap = len(qbow & sbow)

        answers.append((overlap, sent))
        # print(answers)
        
    # Sort the results by the first element of the tuple (i.e., the count)
    # Sort answers from smallest to largest by default, so reverse it
    answers = sorted(answers, key=operator.itemgetter(0), reverse=True)

    # Return the best answer
    best_answer = (answers[0])[1]    
    return best_answer

def get_address(node, rel):
    if node['deps'][rel]:
        return node['deps'][rel][0]
    return None

def add_dependency(node, qgraph):
    if len(node['deps']) > 0:
        deps = get_dependents(node, qgraph)
        deps = sorted(deps, key=operator.itemgetter("address"))
        return " ".join(dep["lemma"] for dep in deps)
    return node['lemma']


def node_depth_first_iter(node, graph):
    stack = deque([node])
    while stack:
        # Pop out the first element in the stack
        node = stack.popleft()
        yield node
        # push children onto the front of the stack.
        # Note that with a deque.extendleft, the first on in is the last
        # one out, so we need to push them in reverse order.
        children = []
        for item in node["deps"]:
            if len(node["deps"][item]) > 0:
               address = node["deps"][item][0]
               dep = graph.nodes[address]
               children.append(dep)
        stack.extendleft(reversed(children))
        
def get_dependents(node, graph):
    return [n for n in node_depth_first_iter(node, graph)]


def parse_question(qgraph):
    qmain = find_main(qgraph)
    qword = qmain["lemma"]
    qnode = find_node(qword, qgraph)
    dependencies = get_dependents(qnode, qgraph)
    
    nsubj = None
    nsubjpass = None, 
    auxpass = None,
    dobj = None
    iobj =None
    nmod = None
    loc = None
    be = None
    verb = None
    neg = None
    advcl = None
    conj = None
    nmodt = None
    
    nsubj_address = get_address(qnode, 'nsubj')
    nsubjpass_address = get_address(qnode, 'nsubjpass')
    auxpass_address = get_address(qnode, 'auxpass')
    dobj_address = get_address(qnode, 'dobj')
    iobj_address = get_address(qnode, 'iobj')
    loc_address = get_address(qnode, 'loc')
    nmod_address = get_address(qnode, 'nmod')
    be_address = get_address(qnode, 'cop')
    neg_address = get_address(qnode, 'neg')
    verb_address = None
    advcl_address = get_address(qnode, 'advcl')
    conj_address = get_address(qnode, 'conj')
    nmodt_address = get_address(qnode, 'nmod:tmod')

    if be_address is None:
        verb = qword

    
    for node in dependencies:
        if node['address'] == nsubj_address:
            nsubj = add_dependency(node,qgraph)
        elif node['address'] == nsubjpass_address:
            nsubjpass = add_dependency(node,qgraph)
        elif node['address'] == auxpass_address:
            auxpass = add_dependency(node,qgraph)
        elif node['address'] == dobj_address:
            dobj = add_dependency(node,qgraph)
        elif node['address'] == iobj_address:
            iobj = add_dependency(node,qgraph)
        elif node['address'] == loc_address:
            loc = add_dependency(node,qgraph)
        elif node['address'] == nmod_address:
            nmod = add_dependency(node,qgraph)
        elif node['address'] == be_address:
            be = add_dependency(node,qgraph)
        elif node['address'] == neg_address:
            neg = add_dependency(node,qgraph)
        elif node['address'] == advcl_address:
            advcl = add_dependency(node,qgraph)
        elif node['address'] == conj_address:
            conj = node['lemma']
        elif node['address'] == nmodt_address:
            nmodt = add_dependency(node,qgraph)
        
    return qnode, dependencies, nsubj, nsubjpass, auxpass, dobj, iobj, nmod, loc, be, verb, neg, advcl, conj, nmodt
    

def parsed_question_dic(qgraph):
    qnode, dependencies, nsubj, nsubjpass, auxpass, dobj, iobj, nmod, loc, be, verb, neg, advcl, conj, nmodt = parse_question(qgraph)
    dic = {}
    dic['nsubj'] = nsubj
    dic['nsubjpass'] = nsubjpass
    dic['auxpass'] = auxpass
    dic['dobj'] = dobj
    dic['iobj'] = iobj
    dic['nmod'] = nmod
    dic['loc'] = loc
    dic['be'] = be
    dic['verb'] = verb
    dic['neg'] = neg
    dic['advcl'] = advcl
    dic['conj'] = conj
    dic['nmod:tmod'] = nmodt
    return dic

def reformulate_question(q):
    qgraph = q['dep']
    qnode, dependencies, nsubj, nsubjpass, auxpass, dobj, iobj, nmod, loc, be, verb, neg, advcl, conj, nmodt = parse_question(qgraph)
    
    if nsubj == None:
        nsubj = ''
    if nsubjpass == None:
        nsubjpass = ''
    if auxpass == None:
        auxpass = ''
    if dobj == None:
        dobj = ''
    if iobj == None:
        iobj = ''
    if nmod == None:
        nmod = ''
    if loc == None:
        loc = ''
    if be == None:
        be = ''
    if verb == None:
        verb = ''
    if neg == None:
        neg = ''
    if advcl == None:
        advcl = ''
    if conj == None:
        conj = ''
    if nmodt == None:
        nmodt = ''
        
    question = q['text']
    #where
    reformulatedQ = ''
    if "Where" in question or "where" in question:
        #a. where is nsubj.?/#b. where did nsubj do something? 
        reformulatedQ = " ".join([nsubj, verb, "somewhere", nmod])
    elif "When" in question or "when" in question:
        reformulatedQ = " ".join([nsubj, verb, "sometime"])
    elif "Who" in question or "who" in question:
        #a. who did something?
        if verb is not '':
            if dobj != "Who" and dobj != "who":
                reformulatedQ = " ".join(["someone", verb, dobj])
            else:
                reformulatedQ = " ".join([nsubj, verb, "someone"])
        #b. who is nsubj. about?  qword == "Who"
        else:
            reformulatedQ = " ".join([nsubj, be, nmod, "someone"])
    elif "What" in question or "what" in question:
        #a. what is somebody doing? question on verb
        
        #b. what did nsubj. eat? question on direct object
        if dobj == "what": 
            reformulatedQ = " ".join([nsubj, verb, "something", nmod])
        #c. what was fired at dobj / what was burned? 
        elif nsubjpass == "what":
            reformulatedQ = " ".join(["something", auxpass, verb, nmod])
        else:
            reformulatedQ = " ".join([nsubj, verb, "something"])
        
    elif "Why" in question or "why" in question:
        reformulatedQ = " ".join([nsubj, neg, verb, iobj, dobj, nmod, "somewhy"])
    
    elif "How" in question or "how" in question:
        reformulatedQ = " ".join([nsubj, neg, verb, iobj, dobj, nmod, "somehow"])
    
    elif question.startswith("Did") or question.startswith("did"):
         reformulatedQ = question[:-1][3:] #find the key word without question mark or did
        
        
    return reformulatedQ

def get_tex_without_POS_or_quotes(text):
    pattern = r'(\,\s)?("\w.*")|(\'\w.*\')'
    text = re.sub(pattern, '.', text)
    return nltk.sent_tokenize(text)


def lemmatized(sentence):
    lemmatized_tokens = []
    tokens = [token.lower() for token in nltk.word_tokenize(sentence) if token not in punct]
    word_pos_tuples = nltk.pos_tag(tokens)
    for tup in word_pos_tuples:
        word = tup[0]
        pos = tup[1]
        if(pos.startswith('VB')):
            lemmatized_tokens.append(wl.lemmatize(word, pos = 'v'))
        else:
            lemmatized_tokens.append(wl.lemmatize(word))
    sentence = " ".join(lemmatized_tokens)
    return sentence

def QAmatching_reformulate(q,text):    
    reformulated_question = reformulate_question(q)
    sentences = nltk.sent_tokenize(text)
    closest_sentence = ''
    max_overlap = 0
    for sentence in sentences:
        lemmatized_sentence = lemmatized(sentence)
        lemmatized_question = lemmatized(reformulated_question)
        overlap = len(set(lemmatized_sentence.split()) & set(lemmatized_question.split()))
        # overlap = len(set(lemmatized_sentence.split()) & set(reformulated_question.split()))
        if overlap > max_overlap:
            max_overlap = overlap
            closest_sentence = sentence
            print (closest_sentence, overlap)
    return closest_sentence

def QAmatching_word_embedding(question, text):    
    sentences = nltk.sent_tokenize(text)
    lowest_distance = 10
    closest_sentence = ''
    for sentence in sentences:
        distance = model.wmdistance(question, sentence)
        if distance < lowest_distance:
            lowest_distance = distance
            closest_sentence = sentence
    print (closest_sentence, "distance = %.3f" % lowest_distance)
    return closest_sentence

def QAmatching_baseline(question, text):
    qbow = get_bow(get_sentences(question)[0])
    sentences = get_sentences(text)
    best = baseline(qbow, sentences)
    best_sentence = ' '.join(word[0] for word in best)[:-2]+'.'  
    return best_sentence
    
def QAmatching_combined(q, text):
    baseline = QAmatching_baseline(q['text'], text)
    reformulate = QAmatching_reformulate(q, text)
    wordemb = QAmatching_word_embedding(q['text'], text)
    if reformulate == wordemb:
        return reformulate
    elif wordemb == baseline:
        return wordemb
    elif reformulate == '':
        return wordemb
    return reformulate