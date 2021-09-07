import re


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


class RemoveHeadlines(TextPrettifier):
    def process(text):
        url_regex = ''
        fixed_doc = []
        for row in text:
            fixed_doc.append(re.sub(url_regex, '', row))
        return fixed_doc



def process(txt):
    all_prettifies = [UnwantedPatternRemover]

    processed_text = txt

    for prettifer in all_prettifies:
        processed_text = prettifer.process(processed_text)
    return processed_text
