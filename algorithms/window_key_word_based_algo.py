import parsers.parser

INGREDIENTS = 'ingredients'
INSTRUCTIONS = 'instructions'



def extract(ingredients, instructions, all_text):
    ingred_paragraph = ''
    instr_paragraph = ''
    lines_of_text = list(filter(None, all_text.split('\n')))

    if ingredients:
        all_relevant_ingred_indies = get_lines_of_text(lines_of_text, True)

        ingred_paragraph = extract_paragraph_from_one_of_the_indices(all_relevant_ingred_indies,
                                                                     lines_of_text, INGREDIENTS)
        ingred_paragraph = ingred_paragraph if len(ingred_paragraph) > 1\
            else extract_paragraph_from_one_of_the_indices(range(0, len(lines_of_text) - 1), lines_of_text,
                                                           INGREDIENTS)

    if instructions:
        all_relevant_instruction_indies = get_lines_of_text(lines_of_text, False)

        instr_paragraph = extract_paragraph_from_one_of_the_indices(all_relevant_instruction_indies,
                                                                     lines_of_text, INSTRUCTIONS)
        instr_paragraph = instr_paragraph if len(instr_paragraph) > 1\
            else extract_paragraph_from_one_of_the_indices(range(0, len(lines_of_text) - 1), lines_of_text,
                                                           INSTRUCTIONS)
    return ingred_paragraph, instr_paragraph


def extract_paragraph_from_one_of_the_indices(all_relevant_indices, lines_of_text, type):
    best_score_so_far = 0
    best_paragraph = ''

    for i in range(0, len(all_relevant_indices)):
        first_line = all_relevant_indices[i]
        last_line = parsers.parser.find_last_index(first_line, lines_of_text, type)
        paragraph = parsers.parser.get_paragraph_from_indexes(first_line, last_line,
                                                              lines_of_text)
        new_score = parsers.parser.get_score_for_text_window_of_type(paragraph, type)

        if new_score > best_score_so_far:
            best_score_so_far = new_score
            best_paragraph = paragraph

    return best_paragraph

# def extract_paragraph_from_one_of_the_indices(all_relevant_indices, lines_of_text, type):
#     best_number_of_paragraph = 0
#     paragraph = ''
#     for i in range(0, len(all_relevant_indices)):
#         first_line = all_relevant_indices[i]
#         last_line = parsers.parser.find_last_index(first_line, lines_of_text, type)
#         new_size_of_text = last_line - first_line
#         if new_size_of_text > best_number_of_paragraph:
#             first_line = first_line
#             last_line = last_line
#             best_number_of_paragraph = new_size_of_text
#             paragraph = parsers.parser.get_paragraph_from_indexes(first_line, last_line,
#                                                                   lines_of_text)
#     return paragraph


def get_lines_of_text(lines_of_text, is_ingredients):
    return parsers.parser.find_line_with_key_word(lines_of_text, is_ingredients)

