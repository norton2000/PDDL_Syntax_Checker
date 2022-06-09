

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
