import re
from daos.key_words import key_words

class TextPrettifier:
    def process(ingred_paragraph):
        pass


class UnwantedPatternRemover(TextPrettifier):
    def process(text):
        url_regex = r'([\w]+(\/.*?\.[\w:]+))|([\w+]+\:\/\/)?([\w\d-]+\.)*[\w-]+[\.\:]\w+([\/\?\=\&\#.]?[-\w\+\,\%\=\'\"\:\/]+)*\/?'
        fixed_doc = []
        for row in text:
            fixed_doc.append(re.sub(url_regex, '', row))
        return fixed_doc


#play and check
class RemoveHeadlines(TextPrettifier):
    def process(text):
        if len(text) > 0:
            big_regex = re.compile('|'.join(map(re.escape, key_words.get_ingredients_key_words())))
            result = [big_regex.sub("", text[0])]
            result.append(text[1 :])
            return result

        return text


def process(txt):
    all_prettifies = [UnwantedPatternRemover, RemoveHeadlines]

    processed_text = txt

    for prettifer in all_prettifies:
        processed_text = prettifer.process(processed_text)
    return processed_text
