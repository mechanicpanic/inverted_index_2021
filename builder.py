import argparse
import json
import pickle
import sys
import spacy
from nltk.stem import PorterStemmer
from nltk.tokenize import TweetTokenizer
from pathlib import Path


def get_files(path):
    file_list = []
    for x in path.iterdir():
        if x.is_file():
            file_list.append(x)
    return file_list


def token_iterator_nltk(files):
    tokenizer = TweetTokenizer()
    stemmer = PorterStemmer()
    for file in files:
        with open(file, 'r') as f:
            temp = json.load(f)
            p = Path(file)
            doc_num = p.stem.split('_')[1]
            big_str = " ".join(temp['comments'])
            words = tokenizer.tokenize(big_str)
            words = [stemmer.stem(word.lower()) for word in words if word.isalpha()]
            for word in words:
                yield doc_num, word


def token_iterator_spacy(files):
    nlp = spacy.load("en_core_web_sm", exclude=["ner"])
    nlp.disable_pipe("parser")
    nlp.enable_pipe("senter")
    for file in files:
        with open(file, 'r') as f:
            temp = json.load(f)
            p = Path(file)
            doc_num = p.name.split("_")[1].split(".")[0]
            docs = list(nlp.pipe(temp['comments']))
            for doc in docs:
                for token in doc:
                    if token.is_alpha:  # Easy way to check for URLs, numbers, etc.
                        yield doc_num, token.lemma_  # Lemmatized form: more correct from the viewpoint of natural
                        # language


def select_iterator(iterator_name, files):
    if iterator_name == "nltk":
        return token_iterator_nltk(files)
    elif iterator_name == "spacy":
        return token_iterator_spacy(files)


def spimi(files, iterator_name, memory=1000):
    blocks = Path.joinpath(Path.cwd(), 'blocks')
    Path(blocks).mkdir(exist_ok=True)
    memory_used = 0
    index = 0
    block_dict = {}

    for doc_num, token in select_iterator(iterator_name, files):
        memory_used += sys.getsizeof(token)
        if token not in block_dict.keys():
            block_dict[token] = {}
        if doc_num not in block_dict[token].keys():
            block_dict[token][doc_num] = 0
        block_dict[token][doc_num] += 1
        if memory_used > memory:
            with open(Path.joinpath(blocks, str(index)), "wb") as f:
                pickle.dump(dict(sorted(block_dict.items())), f)
            index += 1
            block_dict = {}
            memory_used = 0
    if len(block_dict) > 0:
        with open(Path.joinpath(blocks, str(index)), "wb") as f:
            pickle.dump(dict(sorted(block_dict.items())), f)
    return blocks


def merge_dicts(dict1, dict2):
    for key, value in dict2.items():
        if key in dict1.keys():
            dict1[key] += value
        else:
            dict1[key] = value
    return dict(sorted(dict1.items()))


def merge_blocks(block_dir, lib):
    blocks = get_files(block_dir)
    f1 = blocks.pop()
    with open(f1, 'rb') as f:
        dict1 = pickle.load(f)
    while len(blocks) > 0:
        f2 = blocks.pop()
        with open(f2, 'rb') as f:
            dict2 = pickle.load(f)
        for key in dict2.keys():
            if key in dict1.keys():
                dict1[key] = merge_dicts(dict1[key], dict2[key])
            else:
                dict1[key] = dict2[key]
    with open(lib + "_index.pkl", "wb") as f:
        pickle.dump(dict1, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Enter the memory threshold in kilobytes')
    parser.add_argument('memory', type=int,
                        help='Memory threshold')
    parser.add_argument('lib', type=str,
                        help='Whether the text will be lemmatized with spacy (slower) or stemmed with nltk (faster)')
    dataset_path = Path.joinpath(Path.cwd(), 'news_dataset')
    args = parser.parse_args()
    if dataset_path.is_dir():
        block_dir = spimi(get_files(dataset_path), args.lib, args.memory * 1024)
        merge_blocks(block_dir,args.lib)
