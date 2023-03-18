import logging
from unittest import TestCase

from apputils.text_prettifer import RemoveInstructions, INSTRUCTIONS, OnlyHebrewAlphanumeric

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger('prettiferTest')


class TestPrettifyLogic(TestCase):

    def test_remove_instructions_prettifer_sanity(self):
        text_input_to_test = [
            'מרכיבים:',
            'חתול ג׳ודוקא',
            'ג׳אז הארנב משנות ה-90',
            'הוראות הכנה',
            'שים את הכל בדלי פולחן',
            'קוד קידה',
        ]
        result = RemoveInstructions.process(text_input_to_test, INSTRUCTIONS)
        assert ['מרכיבים:', 'חתול ג׳ודוקא', 'ג׳אז הארנב משנות ה-90'] == result

    def test_remove_instructions_prettifer_only_last_suspicion_index(self):
        text_input_to_test = [
            'מרכיבים:',
            'חתול ג׳ודוקא',
            'ג׳אז הארנב משנות ה-90',
            'איך להכין',
            'הוראות הכנה',
            'שים את הכל בדלי פולחן',
            'קוד קידה',
        ]
        result = RemoveInstructions.process(text_input_to_test, INSTRUCTIONS)
        assert ['מרכיבים:', 'חתול ג׳ודוקא', 'ג׳אז הארנב משנות ה-90', 'איך להכין'] == result

    def test_only_hebrew_alphanumeric(self):
        text_input_to_test = [
            'מרכיבים:',
            'חתול ג׳ודוקא',
            'ג׳אז הארנב מש$@#נות ה-90%',
            'איך להכין',
            '<><><><1#@$$הוראות הכנה',
            'שים את הכל בדלי@$#@ פולחן',
            'קוד~~~~~~~~ קידה',
        ]

        result = OnlyHebrewAlphanumeric.process(text_input_to_test, INSTRUCTIONS)
        logger.info(f'after processing text array is: {result}')
        assert ['מרכיבים', 'חתול גודוקא',
                'גאז הארנב משנות ה90%', 'אי להכין',
                '1הוראות הכנה', 'שים את הכל בדלי פולחן',
                'קוד קידה'] == result
