import argparse
import pickle
import sys
from builder import get_files
from nltk.stem import PorterStemmer
import spacy
from pathlib import Path
import pprint
from render import print_file


def get_doc_ids(file_path):
    ls = get_files(file_path)
    return [name.stem.split("_")[1] for name in ls]


def get_postings_by_term(term, index):
    return index[term]


def get_not(postings, doc_ids):
    return {doc_id: 0 for doc_id in doc_ids if doc_id not in postings.keys()}


def get_and(postings1, postings2):
    result = {}
    # print(postings1)
    # print(postings2)
    i, j = 0, 0
    while i < len(postings1.keys()) and j < len(postings2.keys()):
        if list(postings1)[i] < list(postings2)[j]:
            i += 1
        elif list(postings1)[i] > list(postings2)[j]:
            j += 1
        else:
            result[list(postings1)[i]] = postings1[list(postings1)[i]] + postings2[list(postings2)[j]]
            i += 1
            j += 1
    return result


def get_or(postings1, postings2):
    result = dict(postings1)
    result.update(postings2)
    return result


def get_representation_nltk(query, stemmer, index, doc_ids):
    operands = ["AND", "NOT", "OR"]
    ls = query.split(" ")
    res = {}
    tokens = []
    for i, token in enumerate(ls):
        if token not in operands and token is not None:
            tokens.append(token)
            res[i] = get_postings_by_term(stemmer.stem(ls[i]), index)
        elif token == 'NOT':
            res[i] = get_not(get_postings_by_term(stemmer.stem(ls[i + 1]), index), doc_ids)
            tokens.append(ls[i+1])
            ls[i] = None
        elif token == 'AND' or token == 'OR':
            res[i] = token
    return res, tokens


def get_representation_spacy(query, nlp, index, doc_ids):
    operands = ["AND", "NOT", "OR"]
    ls = query.split(" ")
    res = {}
    tokens = []
    for i, token in enumerate(ls):
        if token not in operands and token is not None:
            tokens.append(token)
            res[i] = get_postings_by_term(nlp(ls[i]).lemma_, index)
        elif token == 'NOT':
            tokens.append(ls[i + 1])
            res[i] = get_not(get_postings_by_term(nlp(ls[i + 1]).lemma_, index), doc_ids)
            ls[i] = None
        else:
            res[i] = token
    return res, tokens


def run_query(representation):
    temp = [k for k in representation.keys() if representation[k] in ['AND', 'OR']]
    for key in temp:
        if representation[key] == 'AND':
            temp = get_and(representation[key - 1], representation[key + 1])
            representation.pop(key - 1)
            representation.pop(key)
            representation[key + 1] = temp
        elif representation[key] == 'OR':
            temp = get_or(representation[key - 1], representation[key + 1])
            representation.pop(key - 1)
            representation.pop(key)
            representation[key + 1] = temp
    return representation[list(representation.keys())[0]]


def run_search(index_path, file_path):
    pp = pprint.PrettyPrinter(indent=4)
    stemmer = PorterStemmer()
    nlp = spacy.load('en_core_web_sm', exclude=['ner'])
    nlp.disable_pipe("parser")
    nlp.enable_pipe("senter")
    doc_ids = get_doc_ids(file_path)
    with open(index_path, 'rb') as f:
        index = pickle.load(f)
    while True:
        query = input("Enter a boolean query, 0 to exit:")
        if query == "0":
            sys.exit()
        else:
            if 'nltk' in index_path.stem:
                r, tokens = get_representation_nltk(query, stemmer, index, doc_ids)
            elif 'spacy' in index_path.stem:
                r, tokens = get_representation_spacy(query, nlp, index, doc_ids)
            else:
                print("No valid file found")
                sys.exit()
            res = run_query(r)
            print("Doc_ID results:")
            pp.pprint(res)
            print("The query matched documents with the following titles:")
            for key in res.keys():
                print_file(key)


if __name__ == "__main__":
    file_path = Path.joinpath(Path.cwd(), "news_dataset")
    parser = argparse.ArgumentParser()
    parser.add_argument('lib', type=str,
                        help='Use index built with nltk or spacy')
    args = parser.parse_args()
    index_path = Path.joinpath(Path.cwd(), args.lib + "_index.pkl")
    run_search(index_path, file_path)
