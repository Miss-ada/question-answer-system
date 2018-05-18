'''
Created on May 14, 2014
@author: Reid Swanson

Modified on May 21, 2015
'''

import re, sys, nltk
from nltk.stem.wordnet import WordNetLemmatizer
from qa_engine.base import QABase
from nltk.tree import Tree; from nltk.chunk import ne_chunk



# Our simple grammar from class (and the book)

GRAMMAR =   """
            N: {<NN>|<NNS>}
            V: {<V.*>}
            ADJ: {<JJ.*>}
            NP: {<DT>? <ADJ>* <N>}
            PP: {<IN> <NP> <IN>? <NP>?}
            VP: {<TO>? <V> (<NP>|<PP>)*}
            PN: {<DT>? <NNP>}
            """

# LOC_PP = ["in", "on", "at", "under", "near", "by", "along", "in front of", "on top of", "inside", "outside", "up",
#           "towards", "past", "over", "through", "above", "across", "against", "among", "back", "in back of",
#           "at the back of", "behind", "beside", "next to", "between", "close to", "inside", "underneath"]

# WHO = re.search(r'(?:\s*\b([A-Z][A-Za-z]+)\b)+')

def get_sentences(text):
    sentences = nltk.sent_tokenize(text)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    return sentences
    # print(sentences)
#
# def get_currentCandidate(sentences):
#     for word, pos in sentences:
#         if start:
#             start = False
#             continue
#
#         if pos == 'NNP':
#             currentCandidate.append(word)
#             continue
#
#         if len(currentCandidate) > 0:
#             print(' '.join(currentCandidate))
#             currentCandidate = []
#
#     if len(currentCandidate) > 0:
#         print(' '.join(currentCandidate))
# def who(sentences):
#     whos = []
#     for sent in sentences:
#         if word in sent and re.search(r'(?:\s*\b([A-Z][A-Za-z]+)\b)+', word):
#             whos.append(word)
#     return whos

def who_filter(subtree):
    return subtree.label() == "PN"

# def is_who(noun):
#     return noun[0] in whos

def find_who(tree):
    # Starting at the root of the tree
    # Traverse each node and get the subtree underneath it
    # Filter out any subtrees who's label is not a PP
    # Then check to see if the first child (it must be a preposition) is in
    # our set of locative markers
    # If it is then add it to our list of candidate locations
    
    # How do we modify this to return only the NP: add [1] to subtree!
    # How can we make this function more robust?
    # Make sure the crow/subj is to the left
    who = []
    for subtree in tree.subtrees:
        if is_who(subtree[0]):
            who.append(subtree)
    
    return who

# def find_candidates(sentences):
def find_candidates(sentences, chunker):
    candidates = []
    for sent in who_sentences:
        tree = chunker.parse(sent)
        # print(tree)
        who = find_who(tree)
        candidates.extend(who)
        
    return candidates

def find_sentences(patterns, sentences):
    # Get the raw text of each sentence to make it easier to search using regexes
    raw_sentences = [" ".join([token[0] for token in sent]) for sent in sentences]
    result = []
    for sent, raw_sent in zip(sentences, raw_sentences):
        for word in word:
            if not re.search(pattern, raw_sent):
                matches = False
            else:
                matches = True
        if matches:
            result.append(sent)

    return result

if __name__ == '__main__':
    # Our tools
    chunker = nltk.RegexpParser(GRAMMAR)
    lmtzr = WordNetLemmatizer()
    
    question_id = "fables-01-3"

    driver = QABase()
    q = driver.get_question(question_id)
    story = driver.get_story(q["sid"])
    text = story["text"]

    # Apply the standard NLP pipeline we've seen before
    sentences = get_sentences(text)
    # print(get_currentCandidate(sentences))
    # Assume we're given the keywords for now
    # What is happening
    # verb = "standing"
    # verb = "sitting"
    # Who is doing it
    # subj = "fox"
    # subj = "crow"
    # Where is it happening (what we want to know)
    # loc = None
    
    # Might be useful to stem the words in case there isn't an extact
    # string match
    # subj_stem = lmtzr.lemmatize(NP, "n")
    # verb_stem = lmtzr.lemmatize(ROOT, "v")
    
    # Find the sentences that have all of our keywords in them
    # How could we make this better?
    who_sentences = find_sentences(GRAMMAR(PN), sentences)
    
    # Extract the candidate locations from these sentences
    # who = find_candidates(sentences)
    who = find_candidates(sentences, chunker)

    # Print them out
    for w in who:
        print(w)
        print(" ".join([token[0] for token in w.leaves()]))
