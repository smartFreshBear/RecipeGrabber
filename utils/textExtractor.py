# import asyncio
# from pyppeteer import launch

import urllib.request
import time


import urllib.request
from bs4 import BeautifulSoup

SEPERATOR_TOLORANCE = 4

I = 4


def get_text_from_url(url , retries = 20):
    try:
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers = {'User-Agent': user_agent, }
        request = urllib.request.Request(url, None, headers)

        html = urllib.request.urlopen(request).read()
        # ttt = html2text.html2text(html)
        soup = BeautifulSoup(html)

        # kill all script and style elements
        for script in soup(["script", "style"]):
         script.extract()    # rip it out

        # get text
        paragraphs_raw = soup.get_text('\n\n\n').split('\n\n\n')

        result_paragraph = []
        next_para_to_add = ''
        separator_tolerance = SEPERATOR_TOLORANCE
        for text in paragraphs_raw:

            lines = (line.strip() for line in text.splitlines())
            # break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # drop blank lines
            text_result = '\n'.join(chunk for chunk in chunks if chunk)
            if text_result != '':
                next_para_to_add += '\n' + text_result
            else:
                separator_tolerance = separator_tolerance - 1

            if text_result == '' and separator_tolerance == 0:
                if next_para_to_add != '':
                    result_paragraph.append(next_para_to_add)
                next_para_to_add = ''
                separator_tolerance = SEPERATOR_TOLORANCE

        return result_paragraph
    except Exception as exc:
        if retries > 0:
            print("an exception occurred while trying to access url {} trying again \n more details: {}"
                  .format(url, exc))
            time.sleep(1)
            return get_text_from_url(url, --retries)
        else:
            raise