#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 25 12:01:56 2018
@author: wenjia.ma
"""


from neuralcoref import Coref
import spacy
import en_core_web_sm
from baseline_stub import *
from chunk_demo import *


def find_index(sentence_with_answer, text): #this line method
    sentences = [sentence.strip(' ')for sentence in nltk.sent_tokenize(text)]
    index = sentences.index(sentence_with_answer.strip())
    return index


def transform_text_by_coreference(sentence_with_answer, text):
    nlp = en_core_web_sm.load()
    coref = Coref(nlp)
    clusters = coref.one_shot_coref(utterances=sentence_with_answer, context=text)
    resolved_utterance_text = coref.get_resolved_utterances()
    print(resolved_utterance_text[0])
    return resolved_utterance_text[0]

def find_answer(qgraph, sgraph, rel): #this line method
    qmain = find_main(qgraph)
    qword = qmain["word"]
    snode = find_node(qword, sgraph)

    for node in sgraph.nodes.values():
        # print("node[head]=", node["head"])
        if node.get('head', None) == snode["address"]:
            #print(node["word"], node["rel"])

            if node['rel'] == rel: #node['rel'] =="nmod"
                deps = get_dependents(node, sgraph)
                deps = sorted(deps+[node], key=operator.itemgetter("address"))
                
                return " ".join(dep["word"] for dep in deps)
    
def find_Ada_time(q, sentence_with_answer, text, story):
    qgraph =  q["dep"]
    sgraph = find_sgraph(sentence_with_answer,text, story)
    if sgraph is not None:
        dic = parsed_question_dic(sgraph) 
        try:  
            answer = dic['nmod:tmod']
        except TypeError:
            answer = sentence_with_answer
        return answer
    return sentence_with_answer

def find_Ada_loc(q, sentence_with_answer, text, story):
    qgraph =  q["dep"]
    sgraph = find_sgraph(sentence_with_answer,text, story)
    if sgraph is not None:
        dic = parsed_question_dic(sgraph) 
        try:  
            answer = dic['nmod']
        except TypeError:
            answer = sentence_with_answer
        return answer
    return sentence_with_answer

def find_Ada_who_subj(q, sentence_with_answer, text, story):
    qgraph =  q["dep"]
    sgraph = find_sgraph(sentence_with_answer,text, story)
    if sgraph is not None:
        dic = parsed_question_dic(sgraph) 
        try:  
            if dic['dobj'] is None and dic['nsubj'] is not None:
                answer = dic['nsubj']
            else:
                answer = dic['nsubj'] + ' '+ dic['dobj']
        except TypeError:
            answer = sentence_with_answer
        return answer
    return sentence_with_answer

def find_Ada_verb(q, sentence_with_answer, text, story):
    qgraph =  q["dep"]
    sgraph = find_sgraph(sentence_with_answer,text, story)
    if sgraph is not None:
        dic = parsed_question_dic(sgraph) 
        try:  
            answer = dic['nsubj'] + ' ' + dic['verb'] + ' '+ dic['dobj']
        except TypeError:
            answer = sentence_with_answer
        return answer
    return sentence_with_answer

def find_dobj(q, sentence_with_answer, text, story):
    qgraph =  q["dep"]
    sgraph = find_sgraph(sentence_with_answer,text, story)
    if sgraph is not None:
        try:  
            answer = find_answer(qgraph, sgraph, "dobj") 
            if answer is None:
                answer = find_answer(qgraph, sgraph, "nsubjpass")
        except TypeError:
            answer = sentence_with_answer
        return answer
    return sentence_with_answer   

def find_iobj(q, sentence_with_answer, text, story):
    qgraph =  q["dep"]
    sgraph = find_sgraph(sentence_with_answer,text, story)
    if sgraph is not None:
    #s_dic = parsed_question_dic(sgraph) 
        try:  
            answer = find_answer(qgraph, sgraph, "nsubjpass") #this line
        except TypeError:
            answer = sentence_with_answer
        return answer
    return sentence_with_answer

def find_reason(q, sentence_with_answer, text, story):
    qgraph =  q["dep"]
    sgraph = find_sgraph(sentence_with_answer,text, story)
    if sgraph is not None:
        s_dic = parsed_question_dic(sgraph) 
        try:  
            answer = s_dic['advcl'] #this line
        except TypeError:
            answer = sentence_with_answer
        return answer
    return sentence_with_answer

def find_sgraph(sentence_with_answer,text, story):
    s_index = find_index(sentence_with_answer, text)
    sgraph = None
    if text == story['sch']and len(story["sch_dep"])>s_index:
        sgraph = story["sch_dep"][s_index]
    elif len(story["story_dep"]) > s_index:
        sgraph = story["story_dep"][s_index]
    return sgraph
    
def get_Ada_answer(q,story):
    
    answer = None
    text= ''
    if (q['type'] == 'Sch'):
        text = story['sch']
    else:
        text = story['text']

    # matched_sent contains the sentence containing the answer
    matched_sent = QAmatching_combined(q, text)
    if(matched_sent != ''):
        index = find_index(matched_sent, text)
    else:
        matched_sent = text
    #chunker = nltk.RegexpParser(GRAMMAR)
    
    question = q['text']
    state_question = reformulate_question(q)
    if 'somewhere' in state_question:
        answer = find_Ada_loc(q, matched_sent, text, story)
    elif 'sometime' in state_question:
        answer = find_Ada_time(q, matched_sent, text, story)
    elif 'someone' in state_question:
        if state_question.startswith('someone'):
            answer = find_Ada_who_subj(q, matched_sent, text, story)
            #answer = transform_text_by_coreference(answer, text)
        else:  
            answer = special_cases(q['text'], text)
    elif 'something' in state_question: #something was burned. 
        if state_question.startswith("something"):
            answer = find_dobj(q, matched_sent, text, story)
        elif "do" in question and ("did" in question or "does" in question):#fox did something 
            answer = find_Ada_verb(q, matched_sent, text, story)
        else: ##what was fired at dobj          
            answer = find_iobj(q, matched_sent, text, story)
    elif 'somewhy' in state_question:
        #answer = find_reason(q, matched_sent, text, story)
         answer = matched_sent
    elif question.startswith("Did") or question.startswith("Has") or question.startswith("Have")or question.startswith("Had"):
        answer = find_yes_no(q, matched_sent, text, story)

    if answer == None or len(answer) == 0:
        answer = matched_sent
    elif answer in {'he', 'He', 'she', 'She', 'him', 'Him', 'her', 'Her', 'it', 'It', 'them', 'Them', 'they', 'They', 'we', 'We'}:
        answer = transform_text_by_coreference(answer, text)
    return str(answer)

def find_yes_no(q, matched_sent, text, story):
    #trans_text = transform_text_by_coreference(text, text)
    qgraph =  q["dep"]
    sgraph = find_sgraph(matched_sent,text, story)
    if sgraph is not None:
        s_dic = parsed_question_dic(sgraph) 
        if s_dic['neg'] is not None or "never" in matched_sent:
            return "No"
    return "Yes"

# def special_cases(question, text):
#     #special case for 'who is this about?' : 'story' *\b* 'about'
#     sentences = get_sentences(text)
#     answer = []
#     for sent in sentences:
#         for word, pos in sent:
#             if pos == 'NNP' and word not in answer:
#                 answer.append(word)            
#     return " ".join(answer)

def special_cases(question, text):
    #special case for 'who is this about?' : 'story' *\b* 'about'
    sentences = get_sentences(text)
    answers = []
    dic = {}
    for sent in sentences:
        for word, pos in sent:
#            if pos == 'NNP' and word not in answer:
#                answer.append(word)
#            else:
            if pos == 'NN' or pos == 'NNP':
                if word in dic.keys():
                        dic[word] += 1
                else:
                    dic[word] = 1
    for key in dic.keys():
        if dic[key] > 2:
            if (key.startswith('a') or key.startswith('A') or key.startswith('e') or key.startswith('E')):
                answer = "an "+ key
            else:
                answer = "a " + key
            answers.append(answer)
    if len(answers) > 1:
        return " and ".join(answers)
    return ' '.join(answers)

def change_passive_to_active_voice(text):
    pass