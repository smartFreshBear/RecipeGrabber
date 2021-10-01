import parsers.parser

INGREDIENTS = 'ingredients'
INSTRUCTIONS = 'instructions'



def extract(ingredients, instructions, all_text):
    ingred_paragraph = ''
    instr_paragraph = ''
    lines_of_text = list(filter(None, all_text.split('\n')))

    if ingredients:
        all_relevant_ingred_indies = get_lines_of_text(lines_of_text, True)

        ingred_paragraph = extract_paragraph_from_one_of_the_indices(all_relevant_ingred_indies, ingred_paragraph,
                                                                     lines_of_text, INGREDIENTS)
        ingred_paragraph = ingred_paragraph if len(ingred_paragraph) > 1\
            else extract_paragraph_from_one_of_the_indices(range(0, len(lines_of_text) - 1), ingred_paragraph, lines_of_text,
                                                           INGREDIENTS)

    if instructions:
        all_relevant_instruction_indies = get_lines_of_text(lines_of_text, False)

        instr_paragraph = extract_paragraph_from_one_of_the_indices(all_relevant_instruction_indies, instr_paragraph,
                                                                     lines_of_text, INSTRUCTIONS)
        instr_paragraph = instr_paragraph if len(instr_paragraph) > 1\
            else extract_paragraph_from_one_of_the_indices(range(0, len(lines_of_text) - 1), instr_paragraph, lines_of_text,
                                                           INSTRUCTIONS)
    # if instructions:
    #     # find instr paragraph with max number of lines
    #     all_relevant_instr_indies = get_lines_of_text(lines_of_text, False)
    #     max_num_of_lines_instr = 0
    #
    #     for i in range(0, len(all_relevant_instr_indies)):
    #         first_line = all_relevant_instr_indies[i]
    #         last_line = parsers.parser.find_last_index_if_instruc(first_line, lines_of_text)
    #         new_size_of_text = last_line - first_line
    #         if new_size_of_text > max_num_of_lines_instr:
    #             first_line_instr = first_line
    #             last_line_instr = last_line
    #             max_num_of_lines_instr = new_size_of_text
    #             instr_paragraph = parsers.parser.get_paragraph_from_indexes(first_line_instr, last_line_instr,
    #                                                                         lines_of_text)
    return ingred_paragraph, instr_paragraph


def extract_paragraph_from_one_of_the_indices(all_relevant_indices, paragraph, lines_of_text, type):
    max_num_of_lines_ingred = 0
    # find ingred paragraph with max number of lines
    for i in range(0, len(all_relevant_indices)):
        first_line = all_relevant_indices[i]
        last_line = parsers.parser.find_last_index(first_line, lines_of_text, type)
        new_size_of_text = last_line - first_line
        if new_size_of_text > max_num_of_lines_ingred:
            first_line_ingred = first_line
            last_line_ingred = last_line
            max_num_of_lines_ingred = new_size_of_text
            paragraph = parsers.parser.get_paragraph_from_indexes(first_line_ingred, last_line_ingred,
                                                                  lines_of_text)
    return paragraph


def get_lines_of_text(lines_of_text, is_ingredients):
    return parsers.parser.find_line_with_key_word(lines_of_text, is_ingredients)

