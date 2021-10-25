import json
from pathlib import Path


def print_file(doc_num):
    p = Path.joinpath(Path.cwd(), "news_dataset")
    file = Path.joinpath(p, "news_" + doc_num + ".json")
    with open(file, 'r') as f:
        temp = json.load(f)

    print(temp['title'])
