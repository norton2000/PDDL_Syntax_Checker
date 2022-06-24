

class ParseError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.value
        
class SynError(Exception):
    def __init__(self, text, line, word):
        self.line = line
        self.word = word
        self.text = text
    def __str__(self):
        return self.text

class SupportException(Exception):
    def __init__(self, text, line, word):
        self.line = line
        self.word = word
        self.text = text
    def __str__(self):
        return self.text


import re
def findIndexInText(word,line_file):
    dist = 0
    if word[0] == "?":
        word = word[1:]
        match2search = re.search('[?]'+word+r'[\s)]',line_file)
    else:
        match2search = re.search('^'+word+r'[\s)]',line_file)

        if not match2search:
            match2search = re.search(r'[\s(]' + word + r'[\s)]',line_file)
            dist = 1
            if not match2search:
                match2search = re.search(r'[\s(]' + word+'$',line_file)
    if match2search: return match2search.start()+4+dist
    else: return -1
