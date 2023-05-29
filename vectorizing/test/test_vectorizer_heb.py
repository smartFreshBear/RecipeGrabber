import logging
from unittest import TestCase
import stemming.stemming
from vectorizing import vectorizer_heb
from main_flow import main_flow
from utils import presistor

INSTRUCTIONS_TOP_WORDS = 'inst_top_words.pkl'
INGREDIENTS_TOP_WORDS = 'ing_top_words.pkl'


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('vectorizingEngTest')
vectorizer = vectorizer_heb.VectorizerHeb()
stemmer = stemming.stemming.StemmerHebrew()
main_flow.loadCache()
top_instruc_dict = presistor.load_parameter_cache_from_disk('app/inst_top_words.pkl')
top_ingred_dict = presistor.load_parameter_cache_from_disk('app/ing_top_words.pkl')

# please make sure your working directory for each run is RecipeGrabber and not vectorizing/test


class TestVectorizerHeb(TestCase):

    def test_example_to_vector_heb1(self):
        text = "היי תכינו את הבצל ממש ממש טוב ככה יופי טוב שיצא מושלם חם חם מהתנור ואז תדחפו אותו למיקרו ותוסיפו שמן מים וחצילים"
        vectorized_instruc, instruc_lbls, vectorized_ingred, ingred_lbls = vectorizer.example_to_vector(text,
                                                                                                        top_instruc_dict,
                                                                                                        top_ingred_dict)
        vectorized_instruc = vector_tester(vectorized_instruc)
        vectorized_ingred = vector_tester(vectorized_ingred)
        assert vectorized_instruc == [0] and vectorized_ingred == [0]

    def test_example_to_vector_heb2(self):
        text = "יש לי רק דבר אחד לומר לך הוא מכל הלב"
        vectorized_instruc, instruc_lbls, vectorized_ingred, ingred_lbls = vectorizer.example_to_vector(text,
                                                                                                        top_instruc_dict,
                                                                                                        top_ingred_dict)
        vectorized_instruc = vector_tester(vectorized_instruc)
        vectorized_ingred = vector_tester(vectorized_ingred)
        assert vectorized_instruc == [7, 56, 62, 74, 86, 131, 326, 495, 1422] and vectorized_ingred == [56, 72, 222, 232, 363, 414, 771]

    def test_example_to_vector_heb3(self):
        text = " פתאום תרנגול תרתיחי מים"
        vectorized_instruc, instruc_lbls, vectorized_ingred, ingred_lbls = vectorizer.example_to_vector(text,
                                                                                                        top_instruc_dict,
                                                                                                        top_ingred_dict)
        vectorized_instruc = vector_tester(vectorized_instruc)
        vectorized_ingred = vector_tester(vectorized_ingred)
        assert vectorized_instruc == [0, 16] and vectorized_ingred == [0, 14]

    def test_example_to_vector_heb4(self):
        text = "i do wonder what would happen if everything was in english"
        vectorized_instruc, instruc_lbls, vectorized_ingred, ingred_lbls = vectorizer.example_to_vector(text,
                                                                                                        top_instruc_dict,
                                                                                                        top_ingred_dict)
        vectorized_instruc = vector_tester(vectorized_instruc)
        vectorized_ingred = vector_tester(vectorized_ingred)
        assert vectorized_instruc == [0] and vectorized_ingred == [0]

    def test_example_to_vector_heb5(self):
        text = "בוא ננסה רשימה אחרת של טופ וורדס"
        test_top_instruc_dict = {'בוא': 1, 'אחרת': 2}
        test_top_ingred_dict = {'יש': 1, 'טופ': 2, 'של': 3}
        vectorized_instruc, instruc_lbls, vectorized_ingred, ingred_lbls = vectorizer.example_to_vector(text, test_top_instruc_dict, test_top_ingred_dict)
        vectorized_instruc = vector_tester(vectorized_instruc)
        vectorized_ingred = vector_tester(vectorized_ingred)
        assert vectorized_instruc == [0,1] and vectorized_ingred == []


def vector_tester(vectorized_text):  # used to shorten the vector for testing
    vector_index = []
    for i in range(len(vectorized_text[1])):
        if vectorized_text[1][i] == 1:
            vector_index.append(i)
    return vector_index
