
from qa_engine.base import QABase
from qa_engine.score_answers import main as score_answers
from baseline_stub import *
from dependency_demo_stub import *
from chunk_demo import *
from dependency_demo_stubV1 import *
from nltk.stem.wordnet import WordNetLemmatizer

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
    better_answer = QAmatching_combined(question, text)
    
    return better_answer
    #if better_answer is None:
    #    best_answer = answer
    #else:
    #    best_answer = better_answer

    #return( " ".join(t[0] for t in best_answer))

    # answer = "whatever you think the answer is"

    ###     End of Your Code         ###
#get_better_answer takes in question
def get_better_answer(q):


    chunker = nltk.RegexpParser(GRAMMAR)
    locations = find_answer(crow_sentences, chunker)
    answer = None
    answers =[]
    driver = QABase()
    
    q = driver.get_question(question_id)
    story = driver.get_story(q["sid"])
    text = story["text"]
    question = q['text']
    #unparsed_sent contains the sentence containing the answer
    unparsed_sent = QAmatching_combined(question, text)
    #sentences = sentence.strip('')for sentence in text.split('\n')
    index = find_index(unparsed_sent, text)
    
    lmtzr = WordNetLemmatizer()
    subj_stem = lmtzr.lemmatize(subj, "n")
    verb_stem = lmtzr.lemmatize(verb, "v")
    crow_sentences = find_sentences([subj_stem, verb_stem], sentences)
    #crow_sentences = find_sentences([subj, verb], sentences)
    
    state_question = baseline_stub.reformulate_question(q)
    parsed_dic = parsed_question_dic(q)
    if 'story' and 'about' in state_question:
        special_cases(q)
    if 'somewhere' in state_question:
        answers.append(find_where_answer(q["dep"],story["sch_dep"][index]))
        if len(answers) == 0:
            #if verb exits, then we perform find_locations from that verb
            if (verb_stem):
                find_locations(tree)# needs to be changed
            elif(subj_stem):
                find_locations(tree)
        else:
            answers.append(unparsed_sent)
        # loc = None        
    if 'sometime' in state_question:
        answers.append(unparsed_sent)
        
    if 'someone' in state_question:
        if state_question.startwith('someone'):
            answers.append(find_subj_answer(q["dep"],story["sch_dep"][index]))
        #chunk_demo for an alternate answer
        else:
            answers.append(unparsed_sent)
            dobj = None
    if 'something' in state_question:
        if state_question.startswith("something"):
            answer = find_dobj(q, unparsed_sent, text, story)
            answers.append(answer)
        elif "do" in question and ("did" in question or "does" in question ):
            answer= find_verb(sentences)
            answer.append(answer)
        else:
            answer= find_iobj(q, sentence_with_answer, text, story)
            answer.append(answer)
    if 'somewhy' in state_question:
        subj = parsed_dic["nsubj"]
        verb = parsed_dic["verb"]
        answers.append(subj)
        answers.append(verb)
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