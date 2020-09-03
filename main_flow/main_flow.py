import data_loader

import requests
import requests_cache


import copy
import utils

import numpy as np

requests_cache.install_cache(cache_name='hebrew_roots', backend='sqlite')


TOP_WORD_NUM = 150
EXTRA_FEATURES_NUM = 7
NEW_LINE_TO_WORD_RATIO_IDX = TOP_WORD_NUM + 1
DIGITS_TO_WORDS_RATIO_IDX = NEW_LINE_TO_WORD_RATIO_IDX + 1


def steamimfy(table):
    steamedTable = copy.deepcopy(table)

    for row in steamedTable:
        row[0] = row[0].replace('\n', ' ').replace('\r', ' ')

        request = {
            'token': 'vhZZt9hGGX20aUW',
            'type': 'SEARCH',
            'text': row[0]
        }

        response = requests.post('https://hebrew-nlp.co.il/service/Morphology/Normalize', json=request).json()
        flatten_lst_of_words = [item for sublist in response for item in sublist]
        row[0] = flatten_lst_of_words
    return steamedTable


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


def enrich_new_lines_words_ratio(vectorized_instr, table):

    for i in range(len(table)):
        row = table[i]
        vectorized_instr[i][NEW_LINE_TO_WORD_RATIO_IDX] = (row[0].count('\n')/len(row[0]))


def enrich_ratio_word_to_numbers(vectorized_instr, table):
    for i in range(len(table)):
        row = table[i]
        amount_of_words = len(row[0].split())
        numbers = [str(s) for s in row[0].split() if s.isdigit()]
        vectorized_instr[i][DIGITS_TO_WORDS_RATIO_IDX] = count_amount_of_n_digits(numbers, 1)/amount_of_words
        vectorized_instr[i][DIGITS_TO_WORDS_RATIO_IDX + 1] = count_amount_of_n_digits(numbers, 2)/amount_of_words
        vectorized_instr[i][DIGITS_TO_WORDS_RATIO_IDX + 2] = count_amount_of_n_digits(numbers, 3)/amount_of_words
        vectorized_instr[i][DIGITS_TO_WORDS_RATIO_IDX + 3] = count_amount_of_n_digits(numbers, 4)/amount_of_words
        vectorized_instr[i][DIGITS_TO_WORDS_RATIO_IDX + 4] = count_amount_of_n_digits(numbers, 5)/amount_of_words




def count_amount_of_n_digits(numbers, digit_count):
    return len(list((filter((lambda n: len(n) > digit_count), numbers))))


def load_data():
    table = data_loader.training_extractor.load_all_training_examples(False)
    steamed_dict = steamimfy(table)
    top_instruction_words, top_ingridiates_words = top_words(steamed_dict, TOP_WORD_NUM)
    vectorized_instr, instruction_lbls = vectorized(steamed_dict, top_instruction_words, 2)
    vectorized_ingrid, ingrid_lbls = vectorized(steamed_dict, top_ingridiates_words, 1)

    enrich_new_lines_words_ratio(vectorized_ingrid, table)
    enrich_ratio_word_to_numbers(vectorized_ingrid, table)

    enrich_new_lines_words_ratio(vectorized_instr, table)
    enrich_ratio_word_to_numbers(vectorized_instr, table)
    return vectorized_instr, instruction_lbls, vectorized_ingrid, ingrid_lbls

def example_to_vector(txt):

    single_row_table_with_text = [['txt', 'ing', 'instr'], [txt, '0', '0']]
    steamed = steamimfy(single_row_table_with_text)
    vectorized_instr, instruction_lbls = vectorized(steamed, top_instru_dict, 2)
    vectorized_ingrid, ingrid_lbls = vectorized(steamed, top_ingri_dict, 1)
    enrich_new_lines_words_ratio(vectorized_ingrid, single_row_table_with_text)
    enrich_ratio_word_to_numbers(vectorized_ingrid, single_row_table_with_text)

    enrich_new_lines_words_ratio(vectorized_instr, single_row_table_with_text)
    enrich_ratio_word_to_numbers(vectorized_instr, single_row_table_with_text)

    return vectorized_instr, instruction_lbls, vectorized_ingrid, ingrid_lbls




def divided_training_test(examples_matrix, lbls, train_prec):
    size_of_matrix = len(examples_matrix)
    size_of_training = int(size_of_matrix * train_prec)

    training = examples_matrix[0:size_of_training, :]
    training_lbls = lbls[0:size_of_training]

    test = examples_matrix[size_of_training + 1: size_of_matrix, :]
    test_lbls = lbls[size_of_training + 1: size_of_matrix]
    return training, training_lbls , test, test_lbls


def main():
    vectorized_instr, instru_lbls, vectorized_ingrid, ingrid_lbls = load_data()

    train_x_orig, train_y, test_x_orig, test_y = divided_training_test(vectorized_instr, instru_lbls, 0.8)

    layers_dims = [TOP_WORD_NUM + EXTRA_FEATURES_NUM, 24, 12, 1]  # layer model

    parameters_instructions = utils.L_layer_network.L_layer_model(vectorized_instr.T, instru_lbls.T, layers_dims,
                                                                  learning_rate=0.12,
                                                                  num_iterations=6600,
                                                                  print_cost=True)

    parameters_ingri = utils.L_layer_network.L_layer_model(vectorized_ingrid.T, ingrid_lbls.T, layers_dims,
                                                                  learning_rate=0.12,
                                                                  num_iterations=7000,
                                                                  print_cost=True)

    results_training_set_instru = utils.core_methods.predict(vectorized_instr.T, instru_lbls,
                                                      parameters=parameters_instructions)

    results_training_set_ingri = utils.core_methods.predict(vectorized_ingrid.T, ingrid_lbls,
                                                      parameters=parameters_ingri)
    my_file_handle = open("D:\\ML\\RecipeGrabber\\data_loader\\resources\example.txt", encoding='utf-8')
    text = my_file_handle.read()
    a, b, c, d = example_to_vector(text)

    predictions = utils.core_methods.predict(c.T, np.ones((2, 1)),
                               parameters=parameters_ingri)

    print('the text: {} \n is predicted to be ingri = {}'.format(text, predictions[0][1]))





    # results_test_set = utils.core_methods.predict(test_x_orig.T, test_y, parameters=parameters_instructions)









if __name__ == '__main__':
    main()
