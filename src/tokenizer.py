from .utility import *

#Function that take the input and return a list of a tuple of all the word with the correspective line.
def tokenize(input):
    for count_line, line in enumerate(input):
        line = line.split(";", 1)[0]  # Strip comments.

        try:
            line.encode("ascii")
        except UnicodeEncodeError:
            raise ParseError("Non-ASCII character outside comment: %s" %
                             line[0:-1])
        line = line.replace("(", " ( ").replace(")", " ) ").replace("?", " ?")
        for token in line.split():
            yield (token.lower(), count_line)

#Function that ricursive check each word. Each parenthesis will become a sublist
def parse_list_aux(tokenstream):
    # Leading "(" has already been swallowed.
    while True:
        try:
            (token, n_line) = next(tokenstream)
        except StopIteration:
            raise ParseError("Missing ')', check all parenthesis")
        if token == ")":
            return
        elif token == "(":
            yield list(parse_list_aux(tokenstream))
        else:
            yield (token,n_line)
