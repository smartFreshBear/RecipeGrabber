from vectorizing import vectorizer
from stemming import stemming


class VectorizerEng(vectorizer.Vectorizer):
    TOP_WORD_NUM = 10
    EXTRA_FEATURES_NUM = 14
    NEW_LINE_TO_WORD_RATIO_IDX = TOP_WORD_NUM + 1
    QUESTION_MARKS_VALUES_IDX = NEW_LINE_TO_WORD_RATIO_IDX + 1
    EXCLAMATION_MARKS_VALUES_IDX = QUESTION_MARKS_VALUES_IDX + 1
    DOT_MARKS_VALUES_IDX = EXCLAMATION_MARKS_VALUES_IDX + 1
    COLON_MARKS_VALUES_IDX = DOT_MARKS_VALUES_IDX + 1
    SLASH_MARKS_VALUES_IDX = COLON_MARKS_VALUES_IDX + 1
    DASH_MARKS_VALUES_IDX = SLASH_MARKS_VALUES_IDX + 1
    COMMA_MARKS_VALUES_IDX = DASH_MARKS_VALUES_IDX + 1
    DIGITS_TO_WORDS_RATIO_IDX = COMMA_MARKS_VALUES_IDX + 1

    stemmer = stemming.StemmerEnglish()

    def example_to_vector(self, txt, top_instruc_dict, top_ingred_dict):
        stemmed_txt = self.stemmer.convert_all_text_to_stem_only(txt)
        single_row_table_with_stemmed_text = [['txt', 'ing', 'instr'], [stemmed_txt, '0', '0']]
        single_row_table_with_just_text = [['txt', 'ing', 'instr'], [txt, '0', '0']]

        vectorized_instruc, instruc_lbls = self.vectorize(single_row_table_with_stemmed_text, top_instruc_dict, 2)
        vectorized_ingred, ingred_lbls = self.vectorize(single_row_table_with_stemmed_text, top_ingred_dict, 1)
        self.enrich_tables_vector(single_row_table_with_just_text, vectorized_ingred, vectorized_instruc)

        return vectorized_instruc, instruc_lbls, vectorized_ingred, ingred_lbls

