import main_flow.main_flow

ACCEPTANCE_BENCHMARK = 0.2

WINDOW_SIZE_INGRID = 10
WINDOW_SIZE_INSTRUCT = 12



# proceed_text only roots

def get_key_words_ingred():
    with open('../parsers/resource/key_words_ingri.txt') as f:
        return [line.replace('\n', "") for line in f.readlines()]


def get_key_words_instr():
    with open('../parsers/resource/key_words_instruc.txt') as f:
        return [line.replace('\n', "") for line in f.readlines()]


key_words_ingred = get_key_words_ingred()
key_words_instr = get_key_words_instr()


def get_paragraph_from_indexes(first_line, last_line, lines_of_text):
    return lines_of_text[first_line:last_line]
    # need to check


def is_window_valid_ingred(text_window):
    return ACCEPTANCE_BENCHMARK < main_flow.main_flow.predict_ingri_probes('\n'.join(text_window))


def is_window_valid_instr(text_window):
    return ACCEPTANCE_BENCHMARK < main_flow.main_flow.predict_instru_probes('\n'.join(text_window))


def find_last_index_if_ingred(line_num, lines_of_text):
    line = line_num
    text_window = get_paragraph_from_indexes(line, line + WINDOW_SIZE_INGRID, lines_of_text)
    while is_window_valid_ingred(text_window):
        line += 1
        text_window = get_paragraph_from_indexes(line, line + WINDOW_SIZE_INGRID, lines_of_text)
    return line + 1


def find_last_index_if_instruc(line_num, lines_of_text):
    line = line_num
    text_window = get_paragraph_from_indexes(line, line + WINDOW_SIZE_INSTRUCT, lines_of_text)
    while is_window_valid_instr(text_window):
        line += 1
        text_window = get_paragraph_from_indexes(line, line + WINDOW_SIZE_INSTRUCT, lines_of_text)
    return line + 1


def find_line_with_key_word(lines_of_text, ingredients):
    all_indices = []
    if ingredients:
        key_words = key_words_ingred
    else:
        key_words = key_words_instr
    for i in range(0, len(lines_of_text)):
        line = lines_of_text[i]
        line_contains_key_words = any(key in line for key in key_words)
        if line_contains_key_words:
            all_indices.append(i)
    return list(all_indices)


