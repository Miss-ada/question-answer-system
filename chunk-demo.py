'''
Created on May 14, 2014
@author: Reid Swanson

Modified on May 21, 2015
'''

import re, sys, nltk
from nltk.stem.wordnet import WordNetLemmatizer
from qa_engine.base import QABase
from nltk.corpus import wordnet as wn
from baseline_stub import *

# Our simple grammar from class (and the book)
GRAMMAR = """
            N: {<NN>|<PRP> }
            V: {<V>|(<TO> <V>)}
            ADJ: {<JJ.*>}
            NP: {<DT>? <ADJ>* <N>}
            PP: {(<IN> <NP> <IN>? <NP>?)|(<TO> <NP> <IN>? <NP>?)|(<IN> <NNP> <POS> <NP>)|(<TO> <PRP$> <NN> <NNP> <POS> <NP>)|(<IN> <NP> <WRB> <PRP> <VBR>)}
            VP: {<TO>? <V> (<NP>|<PP>)*}

            """
# {<TO> <PRP$> <NN> <NNP> <POS> <NN>}
# PP: {(<IN> <NP> <IN>? <NP>?)|(<TO> <NP> <IN>? <NP>?)|(<IN> <NNP> <POS> <NN>)}
# PP: { < TO > < PRP$ > ? < NN >? < NNP > < POS > < NN >}

LOC_PP = ["in", "on", "at", "under", "near", "by", "along", "in front of", "on top of", "inside", "outside", "up",
          "towards", "past", "over", "through", "above", "across", "against", "among", "back", "in back of",
          "at the back of", "behind", "beside", "next to", "between", "close to", "inside", "underneath"]

TIME_PP = ["at", "on", "in", "when", "last", "next", "today", "yesterday", "tomorrow"]


def get_sentences(text):
    sentences = nltk.sent_tokenize(text)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    # print(sentences)
    return sentences
#
# def get_sentences_without_quotes(text):
#     test_NQ = re.sub(r'(?!(([^"]*[^"]*$),', '', text)
#     test_NQ = nltk.sent_tokenize(text)
#     test_NQ = [nltk.word_tokenize(sent) for sent in sentences]
#
def pp_filter(subtree):
    return subtree.label() == "PP"


def is_location(prep):
    return prep[0] in LOC_PP


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

# TODO: eliminate words in quotes!

def find_subj(sentences):
    # print(sentences)
    currentCandidate = []
    for sent in sentences:
        for word, pos in sent:
            if pos == 'NNP' and word not in currentCandidate:
                currentCandidate.append(word)
    who = set(currentCandidate)
    return who

def find_obj(tree):
    pass


def find_time(tree):
    pass


def find_reason(tree):
    pass


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


if __name__ == '__main__':
    # Our tools
    chunker = nltk.RegexpParser(GRAMMAR)
    lmtzr = WordNetLemmatizer()

    question_id = "blogs-01-3"
    # question_id = "mc500.train.0.12"
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

    sentences = get_sentences(text)

    # print(sentences)
    # Assume we're given the keywords for now

    state_question = baseline_stub.reformulate_question(q)
        if 'somewhere' in state_question:
            loc =
            verb =
            nsubj =
            dobj =
            iobj =
        if 'sometime' in state_question:
            time = None
        if 'someone' in state_question:
            if state_question.startwith('someone'):
                subj = None
            else:
                dobj = None
        if 'direct_object' in state_question:
            dobj = None
        if 'indirect_object' in state_question:
            iobj = None
        if 'verb' in state_question:
            verb = None


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

    crow_sentences = find_sentences([subj, verb], sentences)

    # crow_sentences = find_sentences([subj_stem, verb_stem], sentences)

    # Extract the candidate locations from these sentences
    locations = find_candidates(crow_sentences, chunker)

    # Print them out

    for loc in locations:
        print(loc)
        print(" ".join([token[0] for token in loc.leaves()]))

    # for who in find_subj(sentences):
    #     print(who)



# TODO:  (WHERE QUESTIONS)  IF we know the verb, use verb_stem in crow_sentences. IF we only know the subject, use subj in crow_sentences.
# First try with the verb then try just the subject.

# TODO: (WHO QUESTIONS) Print who, if not don't.