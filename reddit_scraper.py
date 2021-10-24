import json

import praw
import argparse
from pathlib import Path


def create_dataset_dir():
    cwd = Path.cwd()
    dir = Path.joinpath(cwd, "news_dataset")
    Path(dir).mkdir(exist_ok=True)
    return dir


def scrape_dataset(my_client_id, my_client_secret, my_user_agent, password, user):
    reddit = praw.Reddit(client_id=my_client_id, client_secret=my_client_secret, user_agent=my_user_agent,
                         password=password, user=user)
    top_posts = reddit.subreddit('news').top(limit=1000)
    dir = create_dataset_dir()
    doc_num = 0
    for post in top_posts:
        fname = Path.joinpath(dir, "news_" + str(doc_num) + ".json")
        submission = reddit.submission(id=post.id)
        submission.comments.replace_more(limit=0)

        comments = [str(comment.author) + ": " + comment.body for comment in submission.comments.list()]
        temp_dict = {'title': post.title, 'comments': comments}
        with open(fname, "w") as f:
            json.dump(temp_dict, f)
        doc_num += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='This script needs Reddit account and app credentials to parse the r/news subreddit.')
    parser.add_argument('client_id', type=str,
                        help='14-digit Reddit App Client ID')
    parser.add_argument('client_secret', type=str, help='21-digit Reddit App Client Secret ID')
    parser.add_argument('agent', type=str, help='App name')
    parser.add_argument('password', type=str, help='Reddit account password')
    parser.add_argument('user', type=str, help='Reddit account username')

    args = parser.parse_args()
    scrape_dataset(args.client_id, args.client_secret, args.agent, args.password, args.user)
