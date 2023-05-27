from vectorizing import vectorizer
from stemming import stemming


class VectorizerHeb(vectorizer.Vectorizer):

    stemmer = stemming.StemmerHebrew()

    def __init__(self):
        pass

    def example_to_vector(self, txt, top_instruc_dict, top_ingred_dict):
        stemmed_text = self.stemmer.convert_all_text_to_stem_only(txt)
        single_row_table_with_stemmed_text = [['txt', 'ing', 'instr'], [stemmed_text, '0', '0']]
        single_row_table_with_just_text = [['txt', 'ing', 'instr'], [txt, '0', '0']]

        vectorized_instruc, instruc_lbls = self.vectorize(single_row_table_with_stemmed_text, top_instruc_dict, 2)
        vectorized_ingred, ingred_lbls = self.vectorize(single_row_table_with_stemmed_text, top_ingred_dict, 1)
        self.enrich_tables_vector(single_row_table_with_just_text, vectorized_ingred, vectorized_instruc)

        return vectorized_instruc, instruc_lbls, vectorized_ingred, ingred_lbls








