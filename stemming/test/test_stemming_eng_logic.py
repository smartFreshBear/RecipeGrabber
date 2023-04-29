import logging
from unittest import TestCase

from stemming import stemming

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('stemmingTest')
stemmer_heb = stemming.StemmerHebrew()
stemmer_eng = stemming.StemmerEnglish()


class TestStemmingLogic(TestCase):

    def test_prepare_stem_mapping_eng(self):
        text_input_to_test = [
            'ran**',
            'running!',
            'run/',
            'run',
            '@@#@#run#$$%;',
            'runs',
            'cook',
            'cooking',
            'idkwhatisthis'
        ]
        result = stemmer_eng.prepare_stem_mapping(text_input_to_test)
        assert ['ran', 'run', 'run', 'run', 'run', 'run', 'cook', 'cook', 'idkwhatisthi'] == result

    def test_prepare_stem_mapping(self):
        stemmer_heb.load_from_word_to_stem()
        text_input_to_test = [
            'בדיקה',
            'בדקנו!',
            'בודק/',
            'בודקים',
            '@@#@#בדוק#$$%;',
            'בדיקות',
            'בודק',
        ]
        result = stemmer_heb.prepare_stem_mapping(text_input_to_test)
        assert ['בְּדִיקָה', 'בָּדַק', 'בָּדַק', 'בָּדַק.'] == result    # some words are lef tout cause of cache(?)

    def test_prepare_stem_mapping_eng2(self):
        text_input_to_test = [
            'oil',
            'oiled!',
            'oiling^^^^',
            '-----oil!@!',
            '%''oils%'
        ]
        result = stemmer_eng.prepare_stem_mapping(text_input_to_test)
        assert ['oil', 'oil', 'oil', 'oil', 'oil'] == result

    def test_prepare_stem_mapping_eng3(self):
        text_input_to_test = [
            'omg',
            'frying_',
            'fried!@#$%^^&*&',
            'friesss',
            'friday'
        ]
        result = stemmer_eng.prepare_stem_mapping(text_input_to_test)
        assert ['omg', 'frying_', 'fri', 'friesss', 'friday'] == result

    def test_prepare_stem_mapping_eng4(self):
        text_input_to_test = [
            'עבריתית',
            '123435',
            'is this stemmed?',
            '!@#$%^&*()?>',
            'CAPITALS'
        ]
        result = stemmer_eng.prepare_stem_mapping(text_input_to_test)
        assert ['עבריתית', '123435', 'is', 'thi', 'stem', 'capit'] == result

