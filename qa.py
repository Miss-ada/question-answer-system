"""
@author: Brian Schwarzmann, Ada Ma, and Nathaniel Suriawijaya

"""
from qa_engine.base import QABase
from qa_engine.score_answers import main as score_answers
from baseline_stub import *
from chunk_demo import *
from dependency_demo_stubV1 import *
from nltk.stem.wordnet import WordNetLemmatizer
from nltk import RegexpParser as rp
from coreference import get_Ada_answer
stopwords = set(nltk.corpus.stopwords.words("english"))


def get_answer(question, story):
    """
    :param question: dict
    :param story: dict
    :return: str


    question is a dictionary with keys:
        dep -- A list of dependency graphs for the question sentence.
        par -- A list of constituency parses for the question sentence.
        text -- The raw text of story.
        sid --  The story id.
        difficulty -- easy, medium, or hard
        type -- whether you need to use the 'sch' or 'story' versions
                of the .
        id  --  The id of the question.


    story is a dictionary with keys:
        story_dep -- list of dependency graphs for each sentence of
                    the story version.
        sch_dep -- list of dependency graphs for each sentence of
                    the sch version.
        sch_par -- list of constituency parses for each sentence of
                    the sch version.
        story_par -- list of constituency parses for each sentence of
                    the story version.
        sch --  the raw text for the sch version.
        text -- the raw text for the story version.
        sid --  the story id


    """
    ###     Your Code Goes Here         ###
    q = question['text']
    text= ''
    if (question['type'] == 'Sch'):
        text = story['sch']
    else:
        text = story['text']
    print (text)
    #qbow = get_bow(get_sentences(q)[0])
    #sentences = get_sentences(text)
    #answer = baseline(qbow, sentences)
    
    #better_answer = QAmatching_combined(question, text)
    better_answer = get_Ada_answer(question,story)
    
    return str(better_answer)
    #if better_answer is None:
    #    best_answer = answer
    #else:
    #    best_answer = better_answer

    #return( " ".join(t[0] for t in best_answer))

    # answer = "whatever you think the answer is"

    ###     End of Your Code         ###
#get_better_answer takes in question
def get_better_answer(q,text):
    answer = None
    answers =[]
    driver = QABase()
    single = False
    
    #q = driver.get_question(question_id)
    story = driver.get_story(q["sid"])
    text = story["text"]
    question = q['text'] #this line

    # matched_sent contains the sentence containing the answer
    matched_sent = QAmatching_combined(q, text)
    tokenized_sentences = get_sentences(text)
    sentences = get_sentences_without_quotes(text)
    # sent_array = []
    # for sentence in sentences:
    #     sent_array.append(sentence.strip(''))
    #print("SENTENCE ARRAY:\n", sent_array)
    # if the matched_sent is '', as in QAmatching_combined(q, text)
    
    if(matched_sent != ''):
        index = find_index(matched_sent, text)
        single = True
    else:
        matched_sent = text
    
    #chunker = nltk.RegexpParser(GRAMMAR)
    
    
    state_question = reformulate_question(q)
    #parsed_dic = parsed_question_dic(q)
    if 'story' and 'about' in state_question:
        special_cases(q,text)
    if 'somewhere' in state_question:
        if len(answers) == 0:
            if single == True:
                tokenized_matched_sent = tokenize_sentence(matched_sent)
                #print("tokenized_matched_sent:", tokenized_matched_sent)
                answer_tree = find_where_sent(tokenized_matched_sent)
                for whe in answer_tree:
                    answers.append(" ".join([token[0] for token in whe.leaves()]))
            else:
                answer_tree = find_where(tokenized_sentences)
                for whe in answer_tree:
                    answers.append(" ".join([token[0] for token in whe.leaves()]))
        else:
            answers.append(matched_sent)
        """
        if (story["sch_dep"] != '' and index):
            qgraph = q["dep"]
            sgraph = story["sch_dep"][index]
            answers.append(find_where_answer(qgraph,sgraph))
        
        """
    if 'sometime' in state_question:
        answers.append(matched_sent)
        
    if 'someone' in state_question:
        #chunk_demo for an alternate answer
        if len(answers) == 0:
            if single == True:
                tokenized_matched_sent = tokenize_sentence(matched_sent)
                #print("tokenized_matched_sent:", tokenized_matched_sent)
                answer_tree = find_who_sent(tokenized_matched_sent)
                for whe in answer_tree:
                    answers.append(" ".join([token[0] for token in whe.leaves()]))
            else:
                answer_tree = find_who(tokenized_sentences)
                for whe in answer_tree:
                    answers.append(" ".join([token[0] for token in whe.leaves()]))
            #dobj = None
        else:
            answers.append(matched_sent)
        """
        if (story["sch_dep"] != ''):
            qgraph = q["dep"]
            sgraph = story["sch_dep"][index]
            answers.append(find_where_answer(qgraph,sgraph))
        """
#    if 'somewhat' in state_question:
#        if 'direct_object' in state_question:
#            answers.append(matched_sent)
#        if 'indirect_object' in state_question:
#            answers.append(matched_sent)
#        if 'verb' in state_question:
#            answers.append(matched_sent)
#        else:
#            answers.append(matched_sent)
    if 'somewhy' in state_question:
        answers.append(matched_sent)
    if 'something' in state_question: #this line
        if state_question.startswith("something"):
            dir_obj = find_dobj(q, matched_sent, text, story)
            answers.append(dir_obj)
        elif "do" in question and ("did" in question or "does" in question ):
            if single == True:
                action = find_verb_sent(matched_sent)
                answers.append(action)
            else:
                action = find_verb(sentences)
                answers.append(action)
        else:
            ind_obj= find_iobj(q, matched_sent, text, story)
            answers.append(ind_obj)
    if len(answers) == 0:
        answers.append(matched_sent)
    print("answers object:", answers)
    # joining 'answers' into a single string 'answer' with a ' '
    # answers holds all possible answers, not just the one
    answer = ' '.join(answers)
    return answer

def special_cases(question, text):
    #special case for 'who is this about?' : 'story' *\b* 'about'
    sentences = get_sentences(text)
    answer = []
    for sent in sentences:
        for word, pos in sent:
            if pos == 'NNP' and word not in answer:
                answer.append(word)            
    return answer

#############################################################
###     Dont change the code below here
#############################################################

class QAEngine(QABase):
    @staticmethod
    def answer_question(question, story):
        answer = get_answer(question, story)
        return answer


def run_qa():
    QA = QAEngine()
    QA.run()
    QA.save_answers()

def main():
    run_qa()
    # You can uncomment this next line to evaluate your
    # answers, or you can run score_answers.py
    score_answers()

if __name__ == "__main__":
    main()


    # question = {'text': 'Where was the crow sitting?', 'type': 'story'}
    # story = {'text' : "A Crow was sitting on a branch of a tree with a piece of cheese in her beak when a Fox observed her and set his wits to work to discover some way of getting the cheese. Coming and standing under the tree he looked up and said, What a noble bird I see above me! Her beauty is without equal, the hue of her plumage exquisite. If only her voice is as sweet as her looks are fair, she ought without doubt to be Queen of the Birds.The Crow was hugely flattered by this, and just to show the Fox that she could sing she gave a loud caw. Down came the cheese, of course, and the Fox, snatching it up, said, You have a voice, madam, I see: what you want is wits.", 'sch': ''}
    # #print(nltk.sent_tokenize(story["text"]))
    # print(get_answer(question,story))