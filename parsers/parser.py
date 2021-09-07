import main_flow.main_flow
from daos.key_words import key_words as keys

ACCEPTANCE_BENCHMARK_INGRID = 0.07
ACCEPTANCE_BENCHMARK_INSTRU = 0.0742


WINDOW_SIZE_INGRID = 6
WINDOW_SIZE_INSTRUCT = 8

def get_paragraph_from_indexes(first_line, last_line, lines_of_text):
    return lines_of_text[first_line:last_line]

def is_window_valid_ingred(text_window):
    return ACCEPTANCE_BENCHMARK_INGRID < main_flow.main_flow.predict_ingri_probes('\n'.join(text_window))


def is_window_valid_instr(text_window):
    return ACCEPTANCE_BENCHMARK_INSTRU < main_flow.main_flow.predict_instru_probes('\n'.join(text_window))


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

    if len(list(all_indices)) == 0:
        return [0]
    return list(all_indices)


