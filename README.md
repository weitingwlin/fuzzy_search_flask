### "Find the butterfly book, or something like that!"

When we "search" for something from a database, we type a few words that we think are the "keywords". However, more often when what we type in keywords, what we actually mean is **"show me this butterfly book, or something like that"**. In this case, most of current web application may not give you the book that you actually want.

I am building a "fuzzy search" app that can return results base on the similarity of meanings the search keywords. This is possible using the [**word2vec** (word to vector) model pre-trained with google news](https://code.google.com/archive/p/word2vec/), and natural language processing (NLP) skills.

###--->[check out the app](/app)

Currently, the app is based on titles of the 500 best-selling Fiction books listed on [audible.com](https://www.audible.com/). User can type find **[A Clockwork Orange](https://www.audible.com/pd/Classics/A-Clockwork-Orange-Audiobook/B002V1OHIW)** by typing in **"tangerine"** as the keyword. 

**This task is [currently not easy on audible.com](https://www.audible.com/search/ref=a_hp_tseft?advsearchKeywords=tangerine&filterby=field-keywords)**.




