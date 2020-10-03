from json import JSONDecodeError

import data_loader

import requests
import requests_cache

import sched, time
import pickle
import threading

import copy
import utils

import numpy as np

HEBREW_NLP_END_POINT = 'https://hebrew-nlp.co.il/service/Morphology/Normalize'

requests_cache.install_cache(cache_name='hebrew_roots', backend='sqlite', expire_after=60 * 60 * 24 * 100)

scheduler = sched.scheduler(time.time, time.sleep)


def load_cache_from_disk():
    try:
        with open('data.pkl', 'rb') as handle:
            global from_word_to_steam_cache
            from_word_to_steam_cache = pickle.load(handle)
    except EOFError:
        from_word_to_steam_cache = {}


def start_periodic():
    scheduler.enter(60, 1, periodically_save_cache, (scheduler,))
    scheduler.run()


def periodically_save_cache(sc):
    with open('data.pkl', 'wb') as handle:
        pickle.dump(from_word_to_steam_cache, handle, protocol=pickle.HIGHEST_PROTOCOL)
    scheduler.enter(60, 1, periodically_save_cache, (sc,))


TOP_WORD_NUM = 170
EXTRA_FEATURES_NUM = 9
NEW_LINE_TO_WORD_RATIO_IDX = TOP_WORD_NUM + 1
QUESTION_MARKS_VALUES_IDX = NEW_LINE_TO_WORD_RATIO_IDX + 1
EXCLAMATION_MARKS_VALUES_IDX = QUESTION_MARKS_VALUES_IDX + 1
DIGITS_TO_WORDS_RATIO_IDX = EXCLAMATION_MARKS_VALUES_IDX + 1


# TODO add new feature numer of words divided by something


def steamimfy(table):
    steamedTable = copy.deepcopy(table)

    for row in steamedTable:
        steam_list_of_words_with_cache(row)
    return steamedTable


def steam_list_of_words_with_cache(row):
    words = row[0].replace('\n', ' ').replace('\r', ' ').replace(',', ' '). \
        replace('.', ' ').replace(':', ' ').replace('!', ' ').replace('?', ' ').split(' ')
    words = [word for word in words if word != '']
    attention_seekers = list(filter(lambda word: word not in from_word_to_steam_cache, words))
    cached_words = get_already_cached_words(attention_seekers, words)
    answer_from_api = []
    try:
        if attention_seekers != []:

            request = {
                'token': 'vhZZt9hGGX20aUW',
                'type': 'SEARCH',
                'text': ' ## '.join(attention_seekers)
            }

            response = requests.post(HEBREW_NLP_END_POINT, json=request).json()
            flatten_lst_of_words = [item for sublist in response for item in sublist]
            answer_from_api = ''.join(flatten_lst_of_words).split('##')
            for i in range(len(attention_seekers)):
                from_word_to_steam_cache[attention_seekers[i]] = answer_from_api[i]

        row[0] = answer_from_api.extend(cached_words)
        row[0] = answer_from_api
    except JSONDecodeError as jsonExc:
        print("had a problem parsing this row {} \n more info: {}".format(row, jsonExc))


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
        numbers = [str(s) for s in row[0].split() if s.isdigit()]
        vectorized_instr[i][DIGITS_TO_WORDS_RATIO_IDX] = count_amount_of_n_digits(numbers, 1) / amount_of_words
        vectorized_instr[i][DIGITS_TO_WORDS_RATIO_IDX + 1] = count_amount_of_n_digits(numbers, 2) / amount_of_words
        vectorized_instr[i][DIGITS_TO_WORDS_RATIO_IDX + 2] = count_amount_of_n_digits(numbers, 3) / amount_of_words
        vectorized_instr[i][DIGITS_TO_WORDS_RATIO_IDX + 3] = count_amount_of_n_digits(numbers, 4) / amount_of_words
        vectorized_instr[i][DIGITS_TO_WORDS_RATIO_IDX + 4] = count_amount_of_n_digits(numbers, 5) / amount_of_words


def count_amount_of_n_digits(numbers, digit_count):
    return len(list((filter((lambda n: len(n) > digit_count), numbers))))


def load_data():
    table = data_loader.training_extractor.load_all_training_examples(False)
    steamed_dict = steamimfy(table)
    top_instruction_words, top_ingridiates_words = top_words(steamed_dict, TOP_WORD_NUM)
    vectorized_instr, instruction_lbls = vectorized(steamed_dict, top_instruction_words, 2)
    vectorized_ingrid, ingrid_lbls = vectorized(steamed_dict, top_ingridiates_words, 1)

    enrich_tables_vector(table, vectorized_ingrid, vectorized_instr)

    return vectorized_instr, instruction_lbls, vectorized_ingrid, ingrid_lbls


def example_to_vector(txt):
    single_row_table_with_text = [['txt', 'ing', 'instr'], [txt, '0', '0']]
    steamed = steamimfy(single_row_table_with_text)
    vectorized_instr, instruction_lbls = vectorized(steamed, top_instru_dict, 2)
    vectorized_ingrid, ingrid_lbls = vectorized(steamed, top_ingri_dict, 1)
    enrich_tables_vector(single_row_table_with_text, vectorized_ingrid, vectorized_instr)

    return vectorized_instr, instruction_lbls, vectorized_ingrid, ingrid_lbls


def calculate_amount_of_words(table):
    for row in table:
        row.append(len(row[0].split(' ')))


def enrich_tables_vector(table, vectorized_ingrid, vectorized_instr):
    #TODO： COUNT AMOUNT OF COMMAS
    #TODO： COUNT PSIKIM
    #TODO  COUNT DOTS
    #TODO COUNT  /
    calculate_amount_of_words(table)
    enrich_count_char_for_index(vectorized_ingrid, table, NEW_LINE_TO_WORD_RATIO_IDX, '\n')
    enrich_count_char_for_index(vectorized_ingrid, table, EXCLAMATION_MARKS_VALUES_IDX, '!')
    enrich_count_char_for_index(vectorized_ingrid, table, QUESTION_MARKS_VALUES_IDX, '?')
    enrich_ratio_word_to_numbers(vectorized_ingrid, table)
    enrich_count_char_for_index(vectorized_instr, table, NEW_LINE_TO_WORD_RATIO_IDX, '\n')
    enrich_count_char_for_index(vectorized_instr, table, EXCLAMATION_MARKS_VALUES_IDX, '!')
    enrich_count_char_for_index(vectorized_instr, table, QUESTION_MARKS_VALUES_IDX, '?')
    enrich_ratio_word_to_numbers(vectorized_instr, table)


def divided_training_test(examples_matrix, lbls, train_prec):
    size_of_matrix = len(examples_matrix)
    size_of_training = int(size_of_matrix * train_prec)

    training = examples_matrix[0:size_of_training, :]
    training_lbls = lbls[0:size_of_training]

    test = examples_matrix[size_of_training + 1: size_of_matrix, :]
    test_lbls = lbls[size_of_training + 1: size_of_matrix]
    return training, training_lbls, test, test_lbls


def train():
    vectorized_instr, instru_lbls, vectorized_ingrid, ingrid_lbls = load_data()

    # train_x_orig, train_y, test_x_orig, test_y = divided_training_test(vectorized_instr, instru_lbls, 0.8)

    layers_dims = [TOP_WORD_NUM + EXTRA_FEATURES_NUM, 24, 12, 1]  # layer model

    global parameters_instructions
    global parameters_ingri


    rs1,rs2 = 0.70 , 0.70
    while rs1 < 0.99 or rs2 < 0.99:
        parameters_instructions = utils.L_layer_network.L_layer_model(vectorized_instr.T, instru_lbls.T, layers_dims,
                                                                  learning_rate=0.09,
                                                                  num_iterations=5000,
                                                                  print_cost=True)

        parameters_ingri = utils.L_layer_network.L_layer_model(vectorized_ingrid.T, ingrid_lbls.T, layers_dims,
                                                           learning_rate=0.12,
                                                           num_iterations=7000,
                                                           print_cost=True)

        rs1,rs2 = print_accuracy(ingrid_lbls, instru_lbls, parameters_ingri, parameters_instructions, vectorized_ingrid,
                   vectorized_instr)


def predict_ingri(text):
    a, b, c, d = example_to_vector(text)

    predictions = utils.core_methods.predict(c.T,
                                             parameters=parameters_ingri)

    predicted = predictions[0][1]

    return predicted


def predict_instru(text):
    a, b, c, d = example_to_vector(text)

    predictions = utils.core_methods.predict(c.T,
                                             parameters=parameters_instructions)
    predicted = predictions[0][1]

    return predicted


def print_accuracy(ingrid_lbls, instru_lbls, parameters_ingri, parameters_instructions, vectorized_ingrid,
                   vectorized_instr ):
    results_training_set_instru = utils.core_methods.predict(vectorized_instr.T,
                                                             parameters=parameters_instructions)
    results_training_set_ingri = utils.core_methods.predict(vectorized_ingrid.T,
                                                            parameters=parameters_ingri)

    accuracy_instu = np.sum((results_training_set_instru == instru_lbls.T)) / vectorized_instr.T.shape[1]
    print("Accuracy instru: " + str(accuracy_instu))
    accuracy_ingri = np.sum((results_training_set_ingri == ingrid_lbls.T)) / vectorized_ingrid.T.shape[1]
    print("Accuracy ingri: " + str(accuracy_ingri))

    return accuracy_instu, accuracy_ingri


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def main():
    load_cache_from_disk()
    train()
    run_threaded(start_periodic)


if __name__ == '__main__':
    main()
