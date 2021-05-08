import main_flow.main_flow
from utils import textExtractor
ACCEPTANCE_THRESHOLD = 0.3

WINDOW_SIZE_PARAGRAPH = 20



# proceed_text only roots

def get_key_words_ingred():
    with open('../parsers/resource/key_words_ingri.txt', encoding="utf8") as f:
        return [line.replace('\n', "") for line in f.readlines()]


def get_key_words_instr():
    with open('../parsers/resource/key_words_instruc.txt', encoding="utf8") as f:
        return [line.replace('\n', "") for line in f.readlines()]


key_words_ingred = get_key_words_ingred()
key_words_instr = get_key_words_instr()


def get_paragraph_from_indexes(first_line, last_line, lines_of_text):
    return lines_of_text[first_line:last_line]


def is_window_valid_ingred(text_window):
    return ACCEPTANCE_THRESHOLD < main_flow.main_flow.predict_ingri_probes('\n'.join(text_window))


def is_window_valid_instr(text_window):
    return ACCEPTANCE_THRESHOLD < main_flow.main_flow.predict_instru_probes('\n'.join(text_window))


def find_last_index_if_ingred(line_num, lines_of_text):
    line = line_num
    text_window = get_paragraph_from_indexes(line, line + WINDOW_SIZE_PARAGRAPH, lines_of_text)
    while is_window_valid_ingred(text_window):
        line += 1
        text_window = get_paragraph_from_indexes(line, line + WINDOW_SIZE_PARAGRAPH, lines_of_text)
    return line + 1


def find_last_index_if_instruc(line_num, lines_of_text):
    line = line_num
    text_window = get_paragraph_from_indexes(line, line + WINDOW_SIZE_PARAGRAPH, lines_of_text)
    while is_window_valid_instr(text_window):
        line += 1
        text_window = get_paragraph_from_indexes(line, line + WINDOW_SIZE_PARAGRAPH, lines_of_text)
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


def find_first_and_last_line_index_paragraph(is_ingred, all_start_indexes_suspects, lines_of_text):
    max_num_of_lines = 0
    for i in range(0, len(all_start_indexes_suspects)):
        first_line = all_start_indexes_suspects[i]
        if is_ingred:
            last_line = find_last_index_if_ingred(first_line, lines_of_text)
        else:
            last_line = find_last_index_if_instruc(first_line, lines_of_text)
        new_size_of_paragraph = last_line - first_line
        if new_size_of_paragraph > max_num_of_lines:
            best_first_line = first_line
            best_last_line = last_line
            max_num_of_lines = new_size_of_paragraph
    return best_first_line, best_last_line


def find_none_recipie_indices(first_line_ingred_index, last_line_ingred_index, first_line_instr_index, last_line_instr_index):
    return min(first_line_ingred_index, first_line_instr_index), max(last_line_ingred_index, last_line_instr_index)


def divide_none_recipe_to_paragraphs(start_of_actual_recipe_index, end_of_actual_recipe_index, lines_of_text):
    threshold_to_skip_from_recipe = int(WINDOW_SIZE_PARAGRAPH / 2)
    none_recipe_paragraphs = []
    for i in range(0, start_of_actual_recipe_index - WINDOW_SIZE_PARAGRAPH, WINDOW_SIZE_PARAGRAPH):
        none_recipe_paragraphs.append(get_paragraph_from_indexes(i, i + WINDOW_SIZE_PARAGRAPH, lines_of_text))

    for i in range(end_of_actual_recipe_index + threshold_to_skip_from_recipe, len(lines_of_text) - WINDOW_SIZE_PARAGRAPH, WINDOW_SIZE_PARAGRAPH):
        none_recipe_paragraphs.append(get_paragraph_from_indexes(i, i + WINDOW_SIZE_PARAGRAPH, lines_of_text))

    return none_recipe_paragraphs

def classify_text_to_paragraphs_from_url(url):
    all_text = textExtractor.get_all_text_from_url(url=url)
    lines_of_text = list(filter(None, all_text.split('\n')))

    all_relevant_ingred_indies = find_line_with_key_word(lines_of_text, True)
    all_relevant_instr_indies = find_line_with_key_word(lines_of_text, False)

    is_ingred = True
    first_line_ingred_index, last_line_ingred_index = find_first_and_last_line_index_paragraph(is_ingred,
                                                                                                              all_relevant_ingred_indies,
                                                                                                              lines_of_text)
    is_ingred = False
    first_line_instr_index, last_line_instr_index = find_first_and_last_line_index_paragraph(is_ingred,
                                                                                                            all_relevant_instr_indies,
                                                                                                            lines_of_text)

    ingred_paragraph = get_paragraph_from_indexes(first_line_ingred_index, last_line_ingred_index,
                                                                 lines_of_text)
    instr_paragraph = get_paragraph_from_indexes(first_line_instr_index, last_line_instr_index,
                                                                lines_of_text)

    start_of_actual_recipe_index, end_of_actual_recipe_index = find_none_recipie_indices(
        first_line_ingred_index, last_line_ingred_index, first_line_instr_index, last_line_instr_index)

    none_recipe_paragraphs = divide_none_recipe_to_paragraphs(start_of_actual_recipe_index,
                                                                             end_of_actual_recipe_index, lines_of_text)

    return {'ingredients': ingred_paragraph, 'instructions': instr_paragraph,
            'none_recipe_paragraphs': none_recipe_paragraphs}
