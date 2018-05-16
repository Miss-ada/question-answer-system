
from qa_engine.base import QABase
from qa_engine.score_answers import main as score_answers
from baseline_stub import *
from dependency_demo_stub import *

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
    if (question['type'] == 'sch'):
        text = story['sch']
    else
        text = story['text']

    qbow = get_bow(get_sentences(q)[0], stopwords)
    sentences = get_sentences(text)
    answer = baseline(qbow, sentences, stopwords)
    return( " ".join(t[0] for t in answer))

    # answer = "whatever you think the answer is"

    ###     End of Your Code         ###



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