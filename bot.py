from typing import NoReturn
import praw
import time
import json
import re

def has_comment(submission : praw.reddit.Submission) -> bool :

    # expand comments only if necessary. Each expansion costs one additional request
    try:
        if isinstance(submission.comments.list()[-1], praw.models.reddit.more.MoreComments):
            submission.comments.replace_more(limit=0)
    except IndexError:
        return False

    for comment in submission.comments.list():
        if comment.author == reddit.user.me():
            return True
    else: return False

def needs_comment(submission : praw.reddit.Submission) -> bool : 

    # non-extensive list of string patterns, which have a high probability 
    # of appearing in (python) code blocks, but not in plain english text
    codewords = ['def ', 'self\.', 'np\.', 'tf\.',  
                 'plt\.', 'pd\.', '__', '\(\)', '==']
    regex_pattern = re.compile('(' + '|'.join(codewords) + ')')

    lacks_formatting = re.search(re.compile('<code>.*?'), submission.selftext_html) is None
    needs_formatting = re.search(regex_pattern, submission.selftext) is not None
    not_already_commented = not has_comment(submission)

    return lacks_formatting and needs_formatting and not_already_commented

def reply() -> str : 

    return '\
It looks like your post contains code blocks that are not properly formatted using markdown. \n\n\
By adding four spaces to the beginning of every line you can convert plain text to a code block: \n\n\
\
    This is normal text\n\n\
        def my_code_goes_here():\n\
            a, b = 0, 1\n\
            while True:\n\
                yield a\n\
                a, b = b, a + b\n\n\
    Normal text resumes\n\n\
\
You can write inline code by adding backticks (\`) before and after your code: `` `example()` ``.\n\n\
Please help others help you by providing a well readable example of your problem. Thank you!\n\n\
\
---\n\n\
*^(I am a bot, and this action was performed automatically. Please)* \
[^(*contact my creator*)](https://reddit.com/message/compose/?to=u/Quizznor) \
*^(if you want to raise an issue.)* [^(Here is my source code)](https://www.github.com/Quizznor/FormattingAssistant)'

def main() -> NoReturn :

    with open('secrets.json', 'r') as fp:
        data = fp.read()

    global reddit
    reddit = praw.Reddit(
        **json.loads(data)    
    )

    sub = reddit.subreddit('learnpython')
    for submission in sub.stream.submissions():
        if time.time() - submission.created_utc > 24 * 3600: continue
        if needs_comment(submission):
            submission.reply(reply())

if __name__ == '__main__':
    main()