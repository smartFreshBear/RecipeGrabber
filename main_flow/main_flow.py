from vectorizing import vectorizer_heb
import logging
import threading

from pathlib import Path


import requests_cache
from tensorflow import keras
import data_loader
from training import training_test_cv_divider
from utils import presistor
from stemming import stemming

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')
logger = logging.getLogger('main_flow')
stemmer = stemming.StemmerHebrew()
vectorizer = vectorizer_heb.VectorizerHeb()


# Cache file names:
INSTRUCTIONS_MODEL = 'inst_params'
INSTRUCTIONS_TOP_WORDS = 'inst_top_words.pkl'

INGREDIENTS_MODEL = 'ing_params'
INGREDIENTS_TOP_WORDS = 'ing_top_words.pkl'

HEBREW_NLP_END_POINT = 'https://hebrew-nlp.co.il/service/morphology/normalize'

requests_cache.install_cache(cache_name='hebrew_roots', backend='sqlite', expire_after=60 * 60 * 24 * 100)


# This method tries to load data from the cache (like pre-trained models and top dictionaries).
# If it doesn't find this data in the cache, it returns NONE, that means needs to be reloaded.
def loadCache():
    global top_instruc_dict
    global top_ingred_dict
    global model_instruction
    global model_ingredients

    top_instruc_dict = presistor.load_parameter_cache_from_disk(INSTRUCTIONS_TOP_WORDS)
    top_ingred_dict = presistor.load_parameter_cache_from_disk(INGREDIENTS_TOP_WORDS)

    global from_word_to_stem_cache
    from_word_to_stem_cache = stemmer.load_from_word_to_stem()

    file_instru = f'{INSTRUCTIONS_MODEL}'
    file_ingri = f'{INGREDIENTS_MODEL}'

    if not (Path(file_instru).is_dir() and Path(file_ingri).is_dir()):
        return None

    logging.info('loading cache')
    model_instruction = keras.models.load_model(file_instru)
    model_ingredients = keras.models.load_model(file_ingri)

    return model_instruction and model_ingredients and top_instruc_dict and top_ingred_dict






FROM_NAME_TO_LABELS = {}


def get_already_cached_words(attention_seekers, words):
    cached_words = [item for item in words if item not in attention_seekers]
    cached_words = list(map(lambda w: from_word_to_stem_cache[w], cached_words))
    return cached_words


def top_words(tables, top_num):
    instru_dict = {}
    ingri_dict = {}
    for row in tables:
        if len(row) == 3:
            if row[1] == '1':
                count_word_in_row(ingri_dict, row)

            if row[2] == '1':
                count_word_in_row(instru_dict, row)

    top_instru = list(sort_dic_by_size(instru_dict))[: top_num]

    global top_instruc_dict
    top_instruc_dict = {key: instru_dict[key] for key in top_instru}

    top_ingri = list(sort_dic_by_size(ingri_dict))[: top_num]

    global top_ingred_dict
    top_ingred_dict = {key: ingri_dict[key] for key in top_ingri}

    return top_instruc_dict, top_ingred_dict


# ;)
def sort_dic_by_size(x):
    return {k: v for k, v in sorted(x.items(), key=lambda item: item[1], reverse=True)}


def count_word_in_row(dict_ingri, row):
    flatten_lst_of_words = row[0]
    for word in flatten_lst_of_words:
        incr(dict_ingri, word)


def incr(dic, word):
    if not word in dic:
        dic[word] = 0
    dic[word] += 1


def load_data():
    table = data_loader.training_extractor.load_all_training_examples(False)
    stemmed_dict = stemmer.stemmify(table)
    top_instruction_words, top_ingredients_words = top_words(stemmed_dict, vectorizer.TOP_WORD_NUM)

    # Save dictionaries to disk for caching
    presistor.presist_parameters_to_disk(top_instruction_words, INSTRUCTIONS_TOP_WORDS)
    presistor.presist_parameters_to_disk(top_ingredients_words, INGREDIENTS_TOP_WORDS)

    vectorized_instr, instruction_lbls = vectorizer.vectorize(stemmed_dict, top_instruction_words, 2)
    vectorized_ingrid, ingrid_lbls = vectorizer.vectorize(stemmed_dict, top_ingredients_words, 1)

    vectorizer.enrich_tables_vector(table, vectorized_ingrid, vectorized_instr)

    FROM_NAME_TO_LABELS[INSTRUCTIONS_MODEL] = [vectorized_instr, instruction_lbls]
    FROM_NAME_TO_LABELS[INGREDIENTS_MODEL] = [vectorized_ingrid, ingrid_lbls]


def train(name_group, test_error_tolerance):
    test_error = 10

    model = create_model()

    while test_error_tolerance < test_error:
        training_ex, training_labels, validation_ex, validation_labels, test_ex, test_labels = \
            training_test_cv_divider.divided_training_test(FROM_NAME_TO_LABELS[name_group][0],
                                                           FROM_NAME_TO_LABELS[name_group][1], 0.8)

        model.fit(training_ex, training_labels, epochs=30,
                  validation_data=(validation_ex, validation_labels))

        test_error, _ = model.evaluate(test_ex, test_labels)

    model.save(f'{name_group}')

    return model


def create_model():
    model = keras.models.Sequential()
    model.add(keras.layers.Dense(vectorizer.TOP_WORD_NUM + vectorizer.EXTRA_FEATURES_NUM, activation="relu"))
    model.add(keras.layers.Dense(8, activation="relu"))
    model.add(keras.layers.Dense(2, activation="relu"))
    model.add(keras.layers.Dense(1, activation="sigmoid"))
    model.compile(
        loss='binary_crossentropy',
        optimizer="sgd",
        metrics=["accuracy"])
    return model


def predict_ingred_probes(text):
    _, _, vectorized_ingred, ingred_lbls = vectorizer.example_to_vector(text, top_instruc_dict, top_ingred_dict)
    return predict_vector_with_model(model_ingredients, vectorized_ingred)


def predict_instruc_probes(text):
    vectorized_instr, instruction_lbls, _, _ = vectorizer.example_to_vector(text, top_instruc_dict, top_ingred_dict)
    return predict_vector_with_model(model_instruction, vectorized_instr)


def predict_vector_with_model(model, vector):
    try:
        ans = model(vector)
        ans = ans[1][0]
    except Exception as e:
        logger.error(f'error has occurred during prediction, {e}')
        raise e

    return ans


def main():
    global FROM_NAME_TO_LABELS
    global parameters_instruc
    global parameters_ingred
    global top_instruc_dict
    global top_ingred_dict
    global model_instruction
    global model_ingredients

    if not loadCache():
        load_data()
        model_instruction = train(name_group=INSTRUCTIONS_MODEL,
                                  test_error_tolerance=0.037)
        model_ingredients = train(name_group=INGREDIENTS_MODEL,
                                  test_error_tolerance=0.01)

    caching_thread = threading.Thread(target=stemmer.periodically_save_cache)
    caching_thread.start()


if __name__ == '__main__':
    main()
