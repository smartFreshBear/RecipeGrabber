import copy
import logging
import re
import threading
import time
from json import JSONDecodeError
from pathlib import Path

import numpy as np
import pickle as pickle
import requests
import requests_cache
from tensorflow import keras

import data_loader
import utils
from training import training_test_cv_divider
from utils import presistor

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')
logger = logging.getLogger('main_flow')

CYCLE_TIME_TO_SAVE_CACHE = 60 * 60

# Cache file names:
INSTRUCTIONS_MODEL = 'inst_params'
INSTRUCTIONS_TOP_WORDS = 'inst_top_words.pkl'

INGREDIENTS_MODEL = 'ing_params'
INGREDIENTS_TOP_WORDS = 'ing_top_words.pkl'

HEBREW_NLP_END_POINT = 'https://hebrew-nlp.co.il/service/morphology/normalize'

requests_cache.install_cache(cache_name='hebrew_roots', backend='sqlite', expire_after=60 * 60 * 24 * 100)


def loadCache():
    global top_instru_dict
    global top_ingri_dict
    global model_instruction
    global model_ingredients

    top_instru_dict = presistor.load_parameter_cache_from_disk(INSTRUCTIONS_TOP_WORDS)
    top_ingri_dict = presistor.load_parameter_cache_from_disk(INGREDIENTS_TOP_WORDS)
    load_from_word_to_steam()

    file_instru = f'{INSTRUCTIONS_MODEL}'
    file_ingri = f'{INGREDIENTS_MODEL}'

    if not (Path(file_instru).is_dir() and Path(file_ingri).is_dir()):
        return None

    logging.info('loading cache')
    model_instruction = keras.models.load_model(file_instru)
    model_ingredients = keras.models.load_model(file_ingri)

    return model_instruction and model_ingredients and top_instru_dict and top_ingri_dict


def load_from_word_to_steam():
    try:
        with open('data.pkl', 'rb') as handle:
            global from_word_to_steam_cache
            from_word_to_steam_cache = pickle.load(handle)
    except Exception:
        logging.error('load_cache error')
        from_word_to_steam_cache = {}


def periodically_save_cache():
    while True:
        # Wait for new data to accumulate
        time.sleep(CYCLE_TIME_TO_SAVE_CACHE)

        # Save to disk
        with open('data.pkl', 'wb') as handle:
            pickle.dump(from_word_to_steam_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)


TOP_WORD_NUM = 1500
EXTRA_FEATURES_NUM = 14

NEW_LINE_TO_WORD_RATIO_IDX = TOP_WORD_NUM + 1
QUESTION_MARKS_VALUES_IDX = NEW_LINE_TO_WORD_RATIO_IDX + 1
EXCLAMATION_MARKS_VALUES_IDX = QUESTION_MARKS_VALUES_IDX + 1
DOT_MARKS_VALUES_IDX = EXCLAMATION_MARKS_VALUES_IDX + 1
COMMA_MARKS_VALUES_IDX = DOT_MARKS_VALUES_IDX + 1
SLASH_MARKS_VALUES_IDX = COMMA_MARKS_VALUES_IDX + 1
DASH_MARKS_VALUES_IDX = SLASH_MARKS_VALUES_IDX + 1
PSIKIM_MARKS_VALUES_IDX = DASH_MARKS_VALUES_IDX + 1
DIGITS_TO_WORDS_RATIO_IDX = PSIKIM_MARKS_VALUES_IDX + 1

FROM_NAME_TO_LABELS = {}


def steamimfy(table):
    steamed_table = copy.deepcopy(table)
    only_text_respective = [row[0] for row in steamed_table]
    prepare_stem_mapping(only_text_respective)

    for row_i in range(len(steamed_table)):
        steamed_table[row_i][0] = convert_all_text_to_stem_only(only_text_respective[row_i])
    return steamed_table


def convert_all_text_to_stem_only(text):
    return [''.join(from_word_to_steam_cache.get(word, '')) for word in text.split()]


def prepare_stem_mapping(text_to_steam_list):
    cleaned_texted = [clean_text(text) for text in text_to_steam_list]
    words = [word for words_of_row in cleaned_texted for word in words_of_row]
    attention_seekers = list(filter(lambda word: word not in from_word_to_steam_cache, words))

    try:
        if attention_seekers:

            request = {
                'token': 'vhZZt9hGGX20aUW',
                'type': 'SEARCH',
                'text': ' ## '.join(attention_seekers)
            }

            response = requests.post(HEBREW_NLP_END_POINT, json=request)
            json_response = response.json()
            flatten_lst_of_words = [item for sublist in json_response for item in sublist]
            answer_from_api = ''.join(flatten_lst_of_words).split('##')
            for i in range(len(attention_seekers)):
                from_word_to_steam_cache[attention_seekers[i]] = answer_from_api[i]

    except JSONDecodeError as jsonExc:
        logging.info("had a problem parsing this row {} \n more info: {}".format(row, jsonExc))


def clean_text(text):
    purified_text = re.sub(r'[^\w\s]', '', text)
    return purified_text.split()


def get_already_cached_words(attention_seekers, words):
    cached_words = [item for item in words if item not in attention_seekers]
    cached_words = list(map(lambda w: from_word_to_steam_cache[w], cached_words))
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

    global top_instru_dict
    top_instru_dict = {key: instru_dict[key] for key in top_instru}

    top_ingri = list(sort_dic_by_size(ingri_dict))[: top_num]

    global top_ingri_dict
    top_ingri_dict = {key: ingri_dict[key] for key in top_ingri}

    return top_instru_dict, top_ingri_dict


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


def vectorized(steamed_table, top_words, index_of_mark):
    lst_of_top = list(top_words.keys())

    vectorized_table = steamed_table
    training_set_size = len(vectorized_table)
    training_examples_matrix = np.zeros((training_set_size, TOP_WORD_NUM + EXTRA_FEATURES_NUM))
    labels = np.zeros((training_set_size, 1))

    for i in range(1, training_set_size):
        row = vectorized_table[i]
        if len(row) == 3:
            txt = row[0]
            numed_txt = []
            for word in txt:
                if word in lst_of_top:
                    numed_txt.append(lst_of_top.index(word))
            labels[i] = steamed_table[i][index_of_mark]
            training_examples_matrix[i][numed_txt] = 1

    return training_examples_matrix, labels


def enrich_count_char_for_index(vectorized_instr, table, index, char):
    for i in range(len(table)):
        row = table[i]
        vectorized_instr[i][index] = (row[0].count(char) / int(row[3]))


def enrich_ratio_word_to_numbers(vectorized_instr, table):
    for i in range(len(table)):
        row = table[i]
        amount_of_words = int(row[3])
        numbers = re.findall(r'\d+', row[0])
        vectorized_instr[i][DIGITS_TO_WORDS_RATIO_IDX] = count_amount_of_n_digits(numbers, 1) / amount_of_words
        vectorized_instr[i][DIGITS_TO_WORDS_RATIO_IDX + 1] = count_amount_of_n_digits(numbers, 2) / amount_of_words
        vectorized_instr[i][DIGITS_TO_WORDS_RATIO_IDX + 2] = count_amount_of_n_digits(numbers, 3) / amount_of_words
        vectorized_instr[i][DIGITS_TO_WORDS_RATIO_IDX + 3] = count_amount_of_n_digits(numbers, 4) / amount_of_words
        vectorized_instr[i][DIGITS_TO_WORDS_RATIO_IDX + 4] = count_amount_of_n_digits(numbers, 5) / amount_of_words


def count_amount_of_n_digits(numbers, digit_count):
    return len(list((filter((lambda n: len(n) == digit_count), numbers))))


def load_data():
    table = data_loader.training_extractor.load_all_training_examples(False)
    steamed_dict = steamimfy(table)
    top_instruction_words, top_ingredients_words = top_words(steamed_dict, TOP_WORD_NUM)

    # Save dictionaries to disk for caching
    presistor.presist_parameters_to_disk(top_instruction_words, INSTRUCTIONS_TOP_WORDS)
    presistor.presist_parameters_to_disk(top_ingredients_words, INGREDIENTS_TOP_WORDS)

    vectorized_instr, instruction_lbls = vectorized(steamed_dict, top_instruction_words, 2)
    vectorized_ingrid, ingrid_lbls = vectorized(steamed_dict, top_ingredients_words, 1)

    enrich_tables_vector(table, vectorized_ingrid, vectorized_instr)

    FROM_NAME_TO_LABELS[INSTRUCTIONS_MODEL] = [vectorized_instr, instruction_lbls]
    FROM_NAME_TO_LABELS[INGREDIENTS_MODEL] = [vectorized_ingrid, ingrid_lbls]


def example_to_vector(txt):
    steamed_text = convert_all_text_to_stem_only(txt)
    single_row_table_with__stemed_text = [['txt', 'ing', 'instr'], [steamed_text, '0', '0']]
    single_row_table_with_just_text = [['txt', 'ing', 'instr'], [txt, '0', '0']]

    vectorized_instr, instruction_lbls = vectorized(single_row_table_with__stemed_text, top_instru_dict, 2)
    vectorized_ingrid, ingrid_lbls = vectorized(single_row_table_with__stemed_text, top_ingri_dict, 1)
    enrich_tables_vector(single_row_table_with_just_text, vectorized_ingrid, vectorized_instr)

    return vectorized_instr, instruction_lbls, vectorized_ingrid, ingrid_lbls


def calculate_amount_of_words(table):
    for row in table:
        row.append(len(row[0].split(' ')))


def enrich_tables_vector(table, vectorized_ingrid, vectorized_instr):
    calculate_amount_of_words(table)
    enrich_vectors(table, vectorized_ingrid)
    enrich_vectors(table, vectorized_instr)


def enrich_vectors(table, vecotrized):
    enrich_count_char_for_index(vecotrized, table, NEW_LINE_TO_WORD_RATIO_IDX, '\n')
    enrich_count_char_for_index(vecotrized, table, EXCLAMATION_MARKS_VALUES_IDX, '!')
    enrich_count_char_for_index(vecotrized, table, QUESTION_MARKS_VALUES_IDX, '?')
    enrich_count_char_for_index(vecotrized, table, DOT_MARKS_VALUES_IDX, '.')
    enrich_count_char_for_index(vecotrized, table, COMMA_MARKS_VALUES_IDX, ':')
    enrich_count_char_for_index(vecotrized, table, SLASH_MARKS_VALUES_IDX, '/')
    enrich_count_char_for_index(vecotrized, table, DASH_MARKS_VALUES_IDX, '-')
    enrich_count_char_for_index(vecotrized, table, PSIKIM_MARKS_VALUES_IDX, ',')
    enrich_ratio_word_to_numbers(vecotrized, table)


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
    model.add(keras.layers.Dense(TOP_WORD_NUM + EXTRA_FEATURES_NUM, activation="relu"))
    model.add(keras.layers.Dense(8, activation="relu"))
    model.add(keras.layers.Dense(2, activation="relu"))
    model.add(keras.layers.Dense(1, activation="sigmoid"))
    model.compile(
        loss='binary_crossentropy',
        optimizer="sgd",
        metrics=["accuracy"])
    return model


def predict_ingri_probes(text):
    _, _, vectorized_ingrid, ingrid_lbls = example_to_vector(text)
    return predict_vector_with_model(model_ingredients, vectorized_ingrid)


def predict_instru_probes(text):
    vectorized_instr, instruction_lbls, _, _ = example_to_vector(text)
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
    global parameters_instr
    global parameters_ingred
    global top_instru_dict
    global top_ingri_dict
    global model_instruction
    global model_ingredients

    if not loadCache():
        load_data()
        model_instruction = train(name_group=INSTRUCTIONS_MODEL,
                                  test_error_tolerance=0.037)
        model_ingredients = train(name_group=INGREDIENTS_MODEL,
                                  test_error_tolerance=0.01)

    caching_thread = threading.Thread(target=periodically_save_cache)
    caching_thread.start()


if __name__ == '__main__':
    main()
