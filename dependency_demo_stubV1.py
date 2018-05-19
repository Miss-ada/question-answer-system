#!/usr/bin/env python

import re, sys, nltk, operator
from nltk.stem.wordnet import WordNetLemmatizer

from qa_engine.base import QABase
    
def find_main(graph):
    for node in graph.nodes.values():
        if node['rel'] == 'root':
            return node
    return None

def find_node(word, graph):
    for node in graph.nodes.values():
        if node["word"] == word:
            return node
    return None
    
def get_dependents(node, graph):
    results = []
    for item in node["deps"]:
        address = node["deps"][item][0]
        dep = graph.nodes[address]
        results.append(dep)
        results = results + get_dependents(dep, graph)
        
    return results


def find_where_answer(qgraph, sgraph):
    qmain = find_main(qgraph)
    qword = qmain["word"]
    # print(qword)
    snode = find_node(qword, sgraph)
    for node in sgraph.nodes.values():
        # print("node[head]=", node["head"])
        if node.get('head', None) == snode["address"]:
            # print(node["word"], node["rel"])
            if node['rel'] == "nmod":
                deps = get_dependents(node, sgraph)
                deps = sorted(deps+[node], key=operator.itemgetter("address"))
                return " ".join(dep["word"] for dep in deps)

def find_subj_answer(qgrpah, sgraph):
    qmain = find_main(qgraph)
    qword = qmain["word"]
    snode = find_node(qword, sgraph)
    for node in sgraph.nodes.values():
        # print("node[head]=", node["head"])
        if node.get('head', None) == snode["address"]:
            # print(node["word"], node["rel"])
            if node['rel'] == "nsubj":
                deps = get_dependents(node, sgraph)
                deps = sorted(deps+[node], key=operator.itemgetter("address"))
                return " ".join(dep["word"] for dep in deps)

def find_dobj_answer(qgrpah, sgraph):
    qmain = find_main(qgraph)
    qword = qmain["word"]
    snode = find_node(qword, sgraph)
    # print(qmain)
    for node in sgraph.nodes.values():
        # print("node[head]=", node["head"])
        if node.get('head', None) == snode["address"]:
            # print(node["word"], node["rel"])
            if node['rel'] == "dobj":
                deps = get_dependents(node, sgraph)
                deps = sorted(deps+[node], key=operator.itemgetter("address"))
                return " ".join(dep["word"] for dep in deps)

if __name__ == '__main__':
    driver = QABase()

    # Get the first question and its story
    # q = driver.get_question("blogs-01-13")  ### This is for dobj ####
    q = driver.get_question("fables-01-1")
    # q = driver.get_question("fables-02-1")
    # q = driver.get_question("blogs-01-3")
    ############### mc500 will not work with this parser###############

    story = driver.get_story(q["sid"])

    # get the dependency graph of the first question
    qgraph = q["dep"]
    # print("qgraph:", qgraph)

    # The answer is in the second sentence
    # You would have to figure this out like in the chunking demo
    # sgraph = story["sch_dep"][8]  ####   THIS IS FOR dobj  ####
    # sgraph = story["story_par"][6]
    sgraph = story["sch_dep"][1]

# TODO: send in the correct sentence!!!!!
    
    lmtzr = WordNetLemmatizer()
    for node in sgraph.nodes.values():
        tag = node["tag"]
        word = node["word"]
        if word is not None:
            if tag.startswith("V"):
                print(lmtzr.lemmatize(word, 'v'))
            else:
                print(lmtzr.lemmatize(word, 'n'))
    # print()

    answer = find_where_answer(qgraph, sgraph)
    print("answer:", answer)
    subject = find_subj_answer(qgraph, sgraph)
    print("subject:", subject)
    # happen = find_root(sgraph)
    # print("happen:", happen)
    direct_object = find_dobj_answer(qgraph, sgraph)
    print("direct object:", direct_object)
