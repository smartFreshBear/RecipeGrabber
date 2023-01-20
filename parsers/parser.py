import main_flow.main_flow
from daos.key_words import key_words as keys

ACCEPTANCE_BENCHMARK_INGRID = 0.3
ACCEPTANCE_BENCHMARK_INSTRU = 0.4

WINDOW_SIZE_INGRID = 8
WINDOW_SIZE_INSTRUCT = 8

INSTRUCTIONS = 'instructions'
INGREDIENTS = 'ingredients'

FROM_TYPE_TO_DEFS = {
    INSTRUCTIONS: {
        'ACCEPTANCE_BENCHMARK': ACCEPTANCE_BENCHMARK_INSTRU,
        'WINDOW_SIZE': WINDOW_SIZE_INSTRUCT,
        'CLASSIFIER': main_flow.main_flow.predict_instru_probes
    },
    INGREDIENTS: {
        'ACCEPTANCE_BENCHMARK': ACCEPTANCE_BENCHMARK_INGRID,
        'WINDOW_SIZE': WINDOW_SIZE_INGRID,
        'CLASSIFIER': main_flow.main_flow.predict_ingri_probes
    }
}


def get_paragraph_from_indexes(first_line, last_line, lines_of_text):
    return lines_of_text[first_line:last_line]


def is_window_valid_ingred(text_window):
    return ACCEPTANCE_BENCHMARK_INGRID < main_flow.main_flow.predict_ingri_probes('\n'.join(text_window))


def is_window_valid_instr(text_window):
    return ACCEPTANCE_BENCHMARK_INSTRU < main_flow.main_flow.predict_instru_probes('\n'.join(text_window))


def is_window_valid(text_window, type):
    configs_for_type = FROM_TYPE_TO_DEFS[type]
    score_of_paragraph = get_score_for_text_window_of_type(text_window, type)
    return configs_for_type['ACCEPTANCE_BENCHMARK'] < score_of_paragraph


def get_score_for_text_window_of_type(text_window, type):
    configs_for_type = FROM_TYPE_TO_DEFS[type]
    score_of_paragraph = configs_for_type['CLASSIFIER']('\n'.join(text_window))
    return score_of_paragraph


def find_last_index_if_ingred(line_num, lines_of_text):
    line = line_num
    text_window = get_paragraph_from_indexes(line, line + WINDOW_SIZE_INGRID, lines_of_text)
    if not is_window_valid_ingred(text_window):
        return line
    while is_window_valid_ingred(text_window):
        line += 1
        text_window = get_paragraph_from_indexes(line, line + WINDOW_SIZE_INGRID, lines_of_text)
    return line + WINDOW_SIZE_INGRID - 1


def find_last_index_if_instruc(line_num, lines_of_text):
    line = line_num
    text_window = get_paragraph_from_indexes(line, line + WINDOW_SIZE_INSTRUCT, lines_of_text)
    while is_window_valid_instr(text_window):
        line += 1
        text_window = get_paragraph_from_indexes(line, line + WINDOW_SIZE_INSTRUCT, lines_of_text)
    return line + WINDOW_SIZE_INSTRUCT - 1


def find_last_index(line_num, lines_of_text, type):
    line = line_num
    text_window = get_paragraph_from_indexes(line, line + FROM_TYPE_TO_DEFS[type]['WINDOW_SIZE'], lines_of_text)
    window_is_valid = is_window_valid(text_window, type)
    if not window_is_valid:
        return line
    while window_is_valid:
        line += 1
        text_window = get_paragraph_from_indexes(line, line + FROM_TYPE_TO_DEFS[type]['WINDOW_SIZE'], lines_of_text)
        window_is_valid = is_window_valid(text_window, type)

    return line + FROM_TYPE_TO_DEFS[type]['WINDOW_SIZE'] - 1


def find_line_with_key_word(lines_of_text, ingredients):
    all_indices = []
    if ingredients:
        key_words = keys.get_ingredients_key_words()
    else:
        key_words = keys.get_instructions_key_words()

    for i in range(0, len(lines_of_text)):
        line = lines_of_text[i]
        line_contains_key_words = any(key in line for key in key_words)
        if line_contains_key_words:
            all_indices.append(i)

    return list(all_indices)
