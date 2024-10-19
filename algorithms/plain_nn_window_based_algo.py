from algorithms.recipe_extarctor_algorithm import ExtractorAlgorithm
import parsers.parser

INGREDIENTS = 'ingredients'
INSTRUCTIONS = 'instructions'


class PlainNNWindowBasedAlgo(ExtractorAlgorithm):
    def extract(self, all_text) -> (str, str):

        lines_of_text = list(filter(None, all_text.split('\n')))

        all_relevant_ingred_indies = self.get_lines_of_text(lines_of_text, True)

        ingred_paragraph = self.extract_paragraph_from_one_of_the_indices(all_relevant_ingred_indies,
                                                                          lines_of_text, INGREDIENTS)
        ingred_paragraph = ingred_paragraph if len(ingred_paragraph) > 1 \
            else self.extract_paragraph_from_one_of_the_indices(range(0, len(lines_of_text) - 1), lines_of_text,
                                                                INGREDIENTS)

        all_relevant_instruction_indies = self.get_lines_of_text(lines_of_text, False)

        instr_paragraph = self.extract_paragraph_from_one_of_the_indices(all_relevant_instruction_indies,
                                                                         lines_of_text, INSTRUCTIONS)
        instr_paragraph = instr_paragraph if len(instr_paragraph) > 1 \
            else self.extract_paragraph_from_one_of_the_indices(range(0, len(lines_of_text) - 1), lines_of_text,
                                                                INSTRUCTIONS)
        return ingred_paragraph, instr_paragraph

    def extract_paragraph_from_one_of_the_indices(self, all_relevant_indices, lines_of_text, type):
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

    def get_lines_of_text(self, lines_of_text, is_ingredients):
        return parsers.parser.find_line_with_key_word(lines_of_text, is_ingredients)
