'''

@authors: Reid Swanson
Brian Schwarzmann, Ada Ma, and Nathaniel Suriawijaya

'''

import re, sys, nltk
from nltk.stem.wordnet import WordNetLemmatizer
from qa_engine.base import QABase
from nltk.corpus import wordnet as wn
from baseline_stub import *
from dependency_demo_stubV1 import find_answer, find_index #this line
# Our simple grammar from class (and the book)
GRAMMAR = """
            N: {<NN>|<PRP> }
            V: {<V>|(<TO> <V>)}
            ADJ: {<JJ.*>}
            NP: {(<DT>? <ADJ>* <N>)|(<DT>? <NNP>)}
            PP: {(<TO> <PRP$> <NN> <NNP> <POS> <NP>)|(<IN> <NP> <WRB> <PRP> <VBR>)|(<IN> <NP> <IN>? <NP>?)|(<TO> <NP> <IN>? <NP>?)|(<IN> <NNP> <POS> <NP>)}
                }<JJ|PRP>{
            VP: {<TO>? <V> (<NP>|<PP>)*}
            PN: {<DT>? <NNP>}

            """

LOC_PP = ["in", "on", "at", "under", "near", "by", "along", "in front of", "on top of", "inside", "outside", "up",
          "towards", "past", "over", "through", "above", "across", "against", "among", "back", "in back of",
          "at the back of", "behind", "beside", "next to", "between", "close to", "inside", "underneath"]

TIME_PP = ["at", "on", "in", "when", "last", "next", "today", "yesterday", "tomorrow", "every day", "noon", "around"]


def get_sentences(text):
    sentences = nltk.sent_tokenize(text)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    # print(sentences)
    return sentences
#
def tokenize_sentence(sent):
    sentence = nltk.word_tokenize(sent)
    sentence = nltk.pos_tag(sentence)
    return sentence

def get_sentences_without_quotes(text):
    pattern = r'("\w.*")|(\'\w.*\')'
    text = re.sub(pattern, '', text)
    sentences = nltk.sent_tokenize(text)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    #sentence = [' '.join(sent.split()[1:]) for sent in sentences]
    print("tokenized sents:\n", sentences)
    return sentences

def pp_filter(subtree):
    return subtree.label() == "PP"

def who_filter(subtree):
    return subtree.label() == "PN"

def is_location(prep):
    return prep[0] in LOC_PP

# def is_who(noun):
#     return noun[0] in WHO_NP

def is_time(prep):
    return prep[0] in TIME_PP


def find_locations(tree):
    # Starting at the root of the tree
    # Traverse each node and get the subtree underneath it
    # Filter out any subtrees who's label is not a PP
    # Then check to see if the first child (it must be a preposition) is in
    # our set of locative markers
    # If it is then add it to our list of candidate locations

    # How do we modify this to return only the NP: add [1] to subtree!
    # How can we make this function more robust?
    # Make sure the crow/subj is to the left
    locations = []
    for subtree in tree.subtrees(filter=pp_filter):
        # print(subtree)
        if is_location(subtree[0]):
            locations.append(subtree)
    # print(locations)
    return locations

def find_where(sentences):
    where = []
    chunker = nltk.RegexpParser(GRAMMAR)
    for sent in sentences:
        tree = chunker.parse(sent)
        for subtree in tree.subtrees(filter=pp_filter):
            if is_location(subtree[0]):
                where.append(subtree)
    return where

def find_where_sent(sent):
    where = []
    chunker = nltk.RegexpParser(GRAMMAR)
    tree = chunker.parse(sent)
    for subtree in tree.subtrees(filter=pp_filter):
        if is_location(subtree[0]):
            where.append(subtree)
    return where

def find_who(sentences):
    who = nltk.RegexpParser('WHO: {(<DT>? <NNP> <NN>*)|(<DT> <NNS>)}')
    candidates = []
    for sent in sentences:
        tree = who.parse(sent)
        for subtree in tree.subtrees():
            if subtree.label() == 'WHO':
                if subtree not in candidates:
                    candidates.append(subtree)
    return candidates

def find_who_sent(sent):
    who = nltk.RegexpParser('WHO: {(<DT>? <NNP> <NN>*)|(<DT> <NNS>)}')
    candidates = []
    tree = who.parse(sent)
    for subtree in tree.subtrees():
        if subtree.label() == 'WHO':
            if subtree not in candidates:
                candidates.append(subtree)
    return candidates


# def find_subj(sentences):
#     candidates = []
#     for sent in sentences:
#         for word, pos in sent:
#             if pos == 'NNP' and word not in candidates:
#                 candidates.append(word)
#     return candidates

def find_verb(sentences):
    # print(sentences)
    candidates = []
    for sent in sentences:
        for word, pos in sent:
            if pos in ('VB', 'VBD') and word not in candidates:
                candidates.append(word)
    # print(candidates)
    return candidates
#
# def find_who(tree):
#     candidates = []
#     for subtree in tree.subtrees(filter=who_filter):
#         # print(subtree)
#         if is_who(subtree[0]):
#             candidates.append(subtree)
#     return candidates

def find_dobj(q, sentence_with_answer, text, story):
    qgraph =  q["dep"]
    s_index = find_index(sentence_with_answer, text)
    sgraph = None
    if text == story['sch']:
        sgraph = story["sch_dep"][s_index]
    else:
        sgraph = story["story_dep"][s_index]
    try:  
        answer = find_answer(qgraph, sgraph, "dobj") #this line
    except TypeError:
        answer = sentence_with_answer
    return answer
    
def find_iobj(q, sentence_with_answer, text, story):
    qgraph =  q["dep"]
    s_index = find_index(sentence_with_answer, text)
    sgraph = None
    if text == story['sch']:
        sgraph = story["sch_dep"][s_index]
    else:
        sgraph = story["story_dep"][s_index]
        
    #s_dic = parsed_question_dic(sgraph) 
    try:  
        answer = find_answer(qgraph, sgraph, "nsubjpass") #this line
    except TypeError:
        answer = sentence_with_answer
    return answer

def find_time(tree):
    time = []
    for subtree in tree.subtrees(filter=time_filter):
        # print(subtree)
        if is_time(subtree[0]):
            time.append(subtree)
    # print(time)
    return time

#
# def find_reason(tree):
#     candidates = []
#     for sent in sentences:
#         for word, pos in sent:
#             if word in ('because', 'for'):
#                 return text(['because':]|['for':])
#                 # candidates.append(word)
#     return candidates


def find_candidates(sentences, chunker):
    candidates = []
    for sent in crow_sentences:
        tree = chunker.parse(sent)
        # print(tree)
        locations = find_locations(tree)
        candidates.extend(locations)
    # print(crow_sentences)
    # print(candidates)
    return candidates


def find_sentences(patterns, sentences):
    # Get the raw text of each sentence to make it easier to search using regexes
    raw_sentences = [" ".join([token[0] for token in sent]) for sent in sentences]
    # print(raw_sentences)
    result = []
    for sent, raw_sent in zip(sentences, raw_sentences):
        for pattern in patterns:
            if not re.search(pattern, raw_sent):
                matches = False
            else:
                matches = True
        if matches:
            result.append(sent)

    return result

def get_better_answer(q):
    crow_sentences = find_sentences([subj, verb], sentences)
    chunker = nltk.RegexpParser(GRAMMAR)
    locations = find_candidates(crow_sentences, chunker)
    answer = None
    driver = QABase()
    q = driver.get_question(question_id)
    story = driver.get_story(q["sid"])
    text = story["text"]
    sentences = get_sentences(text)
    state_question = baseline_stub.reformulate_question(q)
    parsed_dic = parsed_question_dic(q)
    if 'somewhere' in state_question:
        subj = parsed_dic["nsubj"]
        verb = parsed_dic["verb"]
        # loc = None
        answer = find_locations(tree)
    if 'sometime' in state_question:
        subj = parsed_dic["nsubj"]
        verb = parsed_dic["verb"]
    if 'someone' in state_question:
        if state_question.startwith('someone'):
            answer = find_subj(sentences)
        # else:
        #     dobj = None
    if 'somewhat' in state_question:
        if 'direct_object' in state_question:
            subj = parsed_dic["nsubj"]
            verb = parsed_dic["verb"]
        if 'indirect_object' in state_question:
            subj = parsed_dic["nsubj"]
            verb = parsed_dic["verb"]
        if 'verb' in state_question:
            subj = parsed_dic["nsubj"]

    if 'somewhy' in state_question:
        subj = parsed_dic["nsubj"]
        verb = parsed_dic["verb"]
    return answer

if __name__ == '__main__':

    # # Our tools
    chunker = nltk.RegexpParser(GRAMMAR)
    # lmtzr = WordNetLemmatizer()

    question_id = "blogs-01-3"
    # question_id = "fables-02-1"
    # question_id = "mc500.train.0.12"
    # question_id = "fables-02-3"
    # question_id = "blogs-01-5"
    # question_id = "fables-02-1"
    # question_id = "fables-01-3"

    driver = QABase()
    q = driver.get_question(question_id)
    story = driver.get_story(q["sid"])
    # sentences = story["story_par"]
    text = story["text"]
    # print(text)
    # Apply the standard NLP pipeline we've seen before

    # sentences = get_sentences(text)
    sentences = get_sentences_without_quotes(text)
    # print(sentences)
    # answer = find_subj(sentences)
    where = find_where(sentences)
    for whe in where:
        print(" ".join([token[0] for token in whe.leaves()]))

    #
    # candidates = find_who(sentences)
    # # print(candidates)
    # for cand in candidates:
    #     print(" ".join([token[0] for token in cand.leaves()]))

    #
    # verb = 'was'
    # verb_stem = lmtzr.lemmatize(verb, "v")
    # crow_sentences = find_sentences(verb, sentences)
    # time = find_candidates(crow_sentences, chunker)
    #
    # pos_time = find_time(sentences)
    # for pt in pos_time:
    #     print(" ".join([token[0] for token in pt.leaves()]))


    # print(sentences)
    # Assume we're given the keywords for now
    #
    # better_answer = get_better_answer(q)
    # print(better_answer)


    # What is happening
    # verb = "standing"
    # verb = "called"
    # verb = "feeding"
    # verb = "happen"

    # Who is doing it
    # subj = "fox"
    # subj = "she"
    # subj = "protest"
    # subj = "bull"
    # Where is it happening (what we want to know)
    # loc = None

    # Might be useful to stem the words in case there isn't an extact
    # string match

    # subj_stem = lmtzr.lemmatize(subj, "n")
    # verb_stem = lmtzr.lemmatize(verb, "v")

    # subj_syn = wn.synsets(subj_stem)
    # verb_syn = wn.synsets(verb_stem)

    # Find the sentences that have all of our keywords in them
    # How could we make this better?
    # crow_sentences = find_sentences([subj_syn, verb_syn], sentences)

    # crow_sentences = find_sentences(subj, sentences)

    # crow_sentences = find_sentences([subj, verb], sentences)

    # crow_sentences = find_sentences([subj_stem, verb_stem], sentences)

    # Extract the candidate locations from these sentences
    # locations = find_candidates(crow_sentences, chunker)

    # Print them out
    #
    # for loc in locations:
    #     print(loc)
    #     print(" ".join([token[0] for token in loc.leaves()]))




# TODO:  (WHERE QUESTIONS)  IF we know the verb, use verb_stem in crow_sentences. IF we only know the subject, use subj in crow_sentences.
# First try with the verb then try just the subject.

# TODO: (WHO QUESTIONS) Print who, if not don't.
