#!/usr/bin/env python
'''
Created on May 14, 2014
@author: reid

Modified on May 21, 2015
'''

import sys, nltk, operator, collections
from qa_engine.base import QABase
from dependency_demo_stub import *
import gensim
model = gensim.models.KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)
#from word2vec_extractor import Word2vecExtractor
#w2vecextractor = Word2vecExtractor("GoogleNews-vectors-negative300.bin")

# The standard NLTK pipeline for POS tagging a document
def get_sentences(text):
    sentences = nltk.sent_tokenize(text)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    
    return sentences	

def get_bow(tagged_tokens, stopwords):
    # return collections.OrderedDict([t[0].lower() for t in tagged_tokens if t[0].lower() not in stopwords])
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
def baseline(qbow, sentences, stopwords):
    # Collect all the candidate answers
    answers = []
    for sent in sentences:
        # A list of all the word tokens in the sentence
        sbow = get_bow(sent, stopwords)

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
        deps = sorted(deps+[node], key=operator.itemgetter("address"))
        return " ".join(dep["word"] for dep in deps)
    return node['word']


def get_dependents(node, graph):
    results = []
    for item in node["deps"]:
        if len(node["deps"][item]) > 0:
            address = node["deps"][item][0]
            dep = graph.nodes[address]
            results.append(dep)
            results = results + get_dependents(dep, graph)     
    return results

def parse_question(q):
    qgraph = q['dep']
    qmain = find_main(qgraph)
    qword = qmain["word"]
    qnode = find_node(qword, qgraph)
    dependencies = get_dependents(qnode, qgraph)
    
    nsubj = None
    dobj = None
    iobj =None
    nmod = None
    loc = None
    be = None
    verb = None
    
    nsubj_address = get_address(qnode, 'nsubj')
    dobj_address = get_address(qnode, 'dobj')
    iobj_address = get_address(qnode, 'iobj')
    loc_address = get_address(qnode, 'loc')
    nmod_address = get_address(qnode, 'nmod')
    be_address = get_address(qnode, 'cop')
    verb_address = None
    
    if be_address is None:
        verb = qword

    
    for node in dependencies:
        if node['address'] == nsubj_address:
            nsubj = add_dependency(node,qgraph)
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
        
    return qnode, dependencies, nsubj, dobj, iobj, nmod, loc, be, verb
    

def parsed_question_dic(q):
    qnode, dependencies, nsubj, dobj, iobj, nmod, loc, be, verb = parse_question(q)
    dic = {}
    dic['nsubj'] = nsubj
    dic['dobj'] = dobj
    dic['iobj'] = iobj
    dic['nmod'] = nmod
    dic['loc'] = loc
    dic['be'] = be
    dic['verb'] = verb
    return dic

def reformulate_question(q):
    qnode, dependencies, nsubj, dobj, iobj, nmod, loc, be, verb = parse_question(q)
    
    if nsubj == None:
        nsubj = ''
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
    #where
    reformulatedQ = ''
    if "Where" in question:
        #a. where is nsubj.?/#b. where did nsubj do something? 
        reformulatedQ = " ".join([nsubj, verb, "somewhere"])
    elif "When" in question:
        reformulatedQ = " ".join([nsubj, verb, "sometime"])
    elif "Who" in question:
        #a. who did something?
        if verb is not '':
           reformulatedQ = " ".join(["someone", verb, dobj])
        #b. who is nsubj. about?  qword == "Who"
        else:
            reformulatedQ = " ".join([nsubj, be, nmod, "someone"])
    elif "What" in question:
        #a. what did nsubj. do? question on verb
        reformulatedQ = " ".join([nsubj, verb, "something", nmod])
        #b. direct object/ (indirect object) question on verb.
    elif "Why" in question:
        pass
        
    return reformulatedQ

def QAmatching_reformulate(question,text):
    reformulated_question = reformulate_question(question)
    sentences = nltk.sent_tokenize(text)
    closest_sentence = ''
    max_overlap = 0
    for sentence in sentences:
        overlap = len(sentence & reformulated_question)
        if overlap > max_overlap:
            max_overlap = overlap
            closest_sentence = sentence
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
    #print (closest_sentence, "distance = %.3f" % lowest_distance)
    return closest_sentence

def QAmatching_baseline(question, text):
    qbow = get_bow(get_sentences(question)[0], stopwords)
    sentences = get_sentences(text)
    best = baseline(qbow, sentences, stopwords)
    best_sentence = ' '.join(word[0] for word in best)[:-2]+'.'  
    return best_sentence
    
def QAmatching_combined(question, text):
    baseline = QAmatching_baseline(question, text)
    reformulate = QAmatching_word_embedding(question, text)
    wordemb = QAmatching_word_embedding(question, text)
    
    if reformulate == wordemb:
        return reformulate
    elif wordemb == baseline:
        return wordemb
    elif baseline == reformulate:
        return baseline
    return wordemb
    
if __name__ == '__main__':

    question_id = "fables-02-10"
    # for qid in hw6-questions.csv:
    driver = QABase()
    q = driver.get_question(question_id)
    story = driver.get_story(q["sid"])
    text = story["text"]
    question = q["text"]
    print("question:", question)
    stopwords = set(nltk.corpus.stopwords.words("english"))

    qbow = get_bow(get_sentences(question)[0], stopwords)
    sentences = get_sentences(text)
    answer = baseline(qbow, sentences, stopwords)
    print("answer:", " ".join(t[0] for t in answer))
