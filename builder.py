import argparse
import json
import pickle
import sys
import spacy
from pathlib import Path


def get_files(path):
    file_list = []
    for x in path.iterdir():
        if x.is_file():
            file_list.append(x)
    return file_list


def token_iterator(files):
    nlp = spacy.load("en_core_web_sm")
    for file in files:
        with open(file, 'r') as f:
            temp = json.load(f)
            p = Path(file)
            doc_num = p.name.split("_")[1]
            docs = list(nlp.pipe(temp['comments']))
            docs.append(nlp(temp['title']))
            for doc in docs:
                for token in doc:
                    if token.is_alpha:  # Easy way to check for URLs, numbers, etc.
                        yield doc_num, token.lemma_  # Lemmatized form: more correct from the viewpoint of natural language


def merge_dicts(dict1, dict2):
    for key, value in dict2.items():
        if key in dict1.keys():
            dict1[key] += value
        else:
            dict1[key] = value
    return dict(sorted(dict1.items()))


def spimi(files, memory=1000):
    block_dir = Path.joinpath(Path.cwd(), 'blocks')
    Path(block_dir).mkdir(exist_ok=True)
    memory_used = 0
    index = 0
    block_dict = {}
    for doc_num, token in token_iterator(files):
        memory_used += sys.getsizeof(token)
        if token not in block_dict.keys():
            block_dict[token] = {}
        if doc_num not in block_dict[token].keys():
            block_dict[token][doc_num] = 0
        block_dict[token][doc_num] += 1
        if memory_used > memory:
            with open(Path.joinpath(block_dir, str(index)), "wb") as f:
                pickle.dump(dict(sorted(block_dict.items())), f)
            index += 1
            block_dict = {}
            memory_used = 0
    return block_dir


def merge_blocks(block_dir):
    blocks = get_files(block_dir)
    f1 = blocks.pop()
    with open(f1, 'rb') as f:
        dict1 = pickle.load(f)
    while len(blocks) > 0:
        f2 = blocks.pop()
        with open(f2, 'rb') as f:
            dict2 = pickle.load(f)
            dict1 = merge_dicts(dict1, dict2)
    with open("index.pkl", "wb") as f:
        pickle.dump(dict1, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Enter the memory threshold in kilobytes')
    parser.add_argument('memory', type=int,
                        help='Memory threshold')
    dataset_path = Path.joinpath(Path.cwd(),'news_dataset')
    args = parser.parse_args()
    if dataset_path.is_dir():
        block_dir = spimi(get_files(dataset_path), args.memory)
        merge_blocks(block_dir)


