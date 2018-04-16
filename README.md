### Using the best-selling fiction titles on audible.com, I built a fuzzy search app that allows users to find what we want even when we mess up with the keywords. And I built an emoji-tagger that provides a quick visual idea of people's opinion on the book.

### "Find the butterfly book, or something like that!"

When we search for something, we use keywords. However, we can mess up with the keywords. Say, if we type in "Butterfly" as the keywords when the book is actually called "Dragonfly in amber". 

In this case, what we actually mean is **"find the butterfly book, or something like that"**. In other words, we want to be allowed some fuzziness in searching. 

I am building a fuzzy search app to deal with this "or something like that" problem. The current app can return results base on the similarity of meanings the search keywords. The model behind the app utilizes techniques in natural language processing (NLP) and the [google **word2vec** word-embedding model](https://code.google.com/archive/p/word2vec/). 



With the word-embedding model, we can search by the meaning of the words, rather than depend strictly matching of keywords. 

Currently, the app is based on titles of the 500 best-selling Fiction books listed on [audible.com](https://www.audible.com/). User can type find **[A Clockwork Orange](https://www.audible.com/pd/Classics/A-Clockwork-Orange-Audiobook/B002V1OHIW)** by typing in **"tangerine"** as the keyword. (**This task is [currently not easy on audible.com](https://www.audible.com/search/ref=a_hp_tseft?advsearchKeywords=tangerine&filterby=field-keywords)**.)

(Please check out ["How it works"](/how_it_works) for more technical details of the model.)


### "So, what do you think about it?"

After finding a book, the next thing we usually do is browsing through online reviews. We want to get an idea of what people think about this book. Emojis provide a quick visualization of how people feel about something.

I constructed a Recurrent Neural Network (RNN) model to predict emojis for sentences from a book reviews. Using the **word2vec** embedding, this task is possible (60% accuracy) with 1,000s of labeled training examples. 

With emoji tagger, we can get a quick  visual idea on how other people think about a book.

#### Emoji-sentence pair where predictions are "correct":
##### 😀 - 'plenty of laugh out loud moments'
##### 🤔 - 'this story has been so inspirational to me, and makes you think deeply about current issues'
##### 😥 - 'I wasn't sure what to expect but it left me in tears'
##### 😱 - 'the horror does not disappoint in any of these regards'
##### 😒 - 'i found this book pretty blah'
##### 👍 -'it is an absolute classic for many good reasons'
##### 'no emoji'- 'there are a lot of pros and cons to this book' 

(Please check out ["How it works"](/how_it_works) for more technical details of the model.)