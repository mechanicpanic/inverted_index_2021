# inverted index with boolean querying
Assignment for the IR class.

[Dataset download link.](https://drive.google.com/file/d/1fj8WNOfGsievss_Gd8UrM29aVI30Kpw-/view?usp=sharing)

Unzip the `news_dataset` folder and place it into the working directory (the repo root folder). As indicated by the name, the dataset contains about 700 post titles and top-level comments from the r/news subreddit.

## Usage
It is recommended to create a `conda` or `venv` environment, as PRAW and Spacy have a lot of dependencies.

``` 
git clone https://github.com/mechanicpanic/inverted_index_2021
cd inverted_index_2021
pip install -r requirements.txt 
```


### Scrape dataset fresh: (SKIP this step if you downloaded the .zip!)
```
python reddit_scraper.py CLIENT_ID CLIENT_SECRET_ID APP_NAME PASSWORD USERNAME
```

### Build index:
There are two choices, NLTK is x2 faster.
1. Build index using a token stemmer from NLTK:
```
python builder.py MEMORY_LIMIT(Kb) nltk
```

2. Build index using a token lemmatizer from spaCy:

```
python -m spacy download en_core_web_sm
python builder.py MEMORY_LIMIT(Kb) spacy
```

### Run search:
```
python searcher.py USED_STEMMING_METHOD
```

The used stemming method has to match the one you used for building the index. So if you obtained the `nltk_index.pkl` file, you would need to run this with as `python searcher.py nltk`.

