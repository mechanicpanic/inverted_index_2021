import sys

def parse_query(query):
    operands = ["AND", "NOT", "OR"]
    ls = query.split(" ")
    opers = []
    terms = []
    for token in ls:
        if token not in operands:
            terms.append(token)
        else:
            opers.append(token)
    return opers, terms


def run_search():
    while True:
        query = input("Enter a boolean query:")
        if query == "0":
            sys.exit()
        else:
            opers, terms = parse_query(query)

