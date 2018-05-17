#!/usr/bin/env python
'''
Created on May 14, 2014
@author: reid

Modified on May 21, 2015
'''

import sys, nltk, operator, collections
from qa_engine.base import QABase
from dependency_demo_stub import *

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
        return node['deps'][rel]
    return None

def add_dependency(node, qgraph):
    if len(node['deps']) > 0:
        deps = get_dependents(node, qgraph)
        deps = sorted(deps+[node], key=operator.itemgetter("address"))
        return " ".join(dep["word"] for dep in deps)
    return node['word']

def reformulate_question(q):
    question = q["text"]
    qgraph = q['dep']
    qmain = find_main(qgraph)
    qword = qmain["word"]
    qnode = find_node(qword, qgraph)
    
    nsubj_address = get_address(qnode, 'nsubj')
    dobj_address = get_address(qnode, 'dobj')
    nmod_address = get_address(qnode, 'nmod')
    be_address = get_address(qnode, 'cop')
    
    nsubj = ''
    dobj = ''
    nmod = ''
    be = ''
    
    dependencies = get_dependents(qnode, qgraph)
    #where
    reformulatedQ = ''
    if "Where" in question:
        #a. where is nsubj.?/#b. where did nsubj do something? 
        for node in dependencies:
            if node['address'] == nsubj_address:
                nsubj = add_dependency(node,qgraph)
        reformulatedQ = " ".join([nsubj, qword, "somewhere"])
    elif "When" in question:
        for node in dependencies:
            if node['address'] == nsubj_address:
                nsubj = add_dependency(node, qgraph)
        reformulatedQ = " ".join([nsubj, qword, "sometime"])
    elif "Who" in question:
        #a. who did something?
        if qword != "Who":
            for node in dependencies:
                if node['address'] == dobj_address:
                    dobj = node['word']
            reformulatedQ = " ".join(["someone", qword, dobj])
        #b. who is nsubj. about?  qword == "Who"
        else:
            for node in dependencies:
                if node['address'] == nsubj_address:
                    nsubj = node['word']
                elif node['address'] == be_address:
                    be = node['word']
                elif node['address'] == nmod_address:
                    nmod = node['word']
            reformulatedQ = " ".join([nsubj, be, nmod, "someone"])
    elif "What" in question:
        #a. what did nsubj. do?
        for node in dependencies:
            if node['address'] == nsubj_address:
                nsubj = add_dependency(node,qgraph)
        reformulatedQ = " ".join([nsubj, qword, "something"])
        
    return reformulatedQ

def QAmatching_reformulate(question,text):
    reformulated_question = reformulate_question(question)
    for sentence in text:
        #highest level: strict matching
        #secondary level: most words overlap
        pass
        

def QAmatching_word_embedding(question, text):
    pass
    
if __name__ == '__main__':

    question_id = "blogs-01-4"
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
