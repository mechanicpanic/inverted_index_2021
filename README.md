# inverted index with boolean querying
Assignment for the IR class.
[Dataset download link.](https://drive.google.com/file/d/1fj8WNOfGsievss_Gd8UrM29aVI30Kpw-/view?usp=sharing)
Unzip the `news_dataset` folder and place it into the working directory (the repo root folder).

## Usage
It is recommended to create a `conda` or `venv` environment, as PRAW and Spacy have a lot of dependencies.

`git clone https://github.com/mechanicpanic/inverted_index_2021`
`cd inverted_index_2021`
`pip install -r requirements.txt`

### Scrape dataset fresh:
`python reddit_scraper.py CLIENT_ID CLIENT_SECRET_ID APP_NAME PASSWORD USERNAME`

### Build index:
`python builder.py MEMORY_LIMIT(Kb) STEMMING_METHOD`

`STEMMING_METHOD` refers to whether the data will be indexed as stems obtained with Porter Stemmer or as lemmas obtained by Spacy.
The options are `nltk` and `spacy` respectively.

### Run search:
`python searcher.py USED_STEMMING_METHOD`
The used stemming method has to match the one you used for building the index. So if you obtained the `nltk_index.pkl` file, you would need to run this with as `python searcher.py nltk`.

