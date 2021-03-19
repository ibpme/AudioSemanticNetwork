import re
import nltk
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from time import perf_counter

stopwords = set(nltk.corpus.stopwords.words("indonesian"))
stop_factory = StopWordRemoverFactory()
stopwords.update(stop_factory.get_stop_words())

# Use NLTK for Word Distribution and Most Common Words


def text_clean(text, case_folding=True, bad_symbols=True, bad_brackets=True, remove_stopwords=True):
    print("Cleaning Text...")
    # lowercase text
    if case_folding:
        text = text.lower()

    if bad_brackets:
        # replace REPLACE_BY_SPACE_RE symbols by space in text
        BRACKETS_RE = re.compile('[/(){}\[\]\|@,;]')
        text = re.sub(BRACKETS_RE, " ", text)

    if bad_symbols:
        BAD_SYMBOLS_RE = re.compile('[^0-9a-z #+_-]')
        # delete symbols which are in BAD_SYMBOLS_RE from text
        text = re.sub(BAD_SYMBOLS_RE, "", text)

    # delete stopwords from text
    if remove_stopwords:
        text_list = text.split()
        text_list_copy = text_list.copy()
        for word in text_list_copy:
            if word in stopwords:
                text_list.remove(word)
        text = " ".join(text_list)

    return text


def text_stem(text):
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    print("Stemming Text...")
    t1_start = perf_counter()
    stemmed_text = stemmer.stem(text)
    t1_stop = perf_counter()
    print("Stemming done in {} seconds".format(t1_stop-t1_start))

    return stemmed_text


with open("file.txt", "r") as file:
    text = file.read()

cleaned_text = text_clean(text)
stemmed_text = text_clean(text_stem(cleaned_text))
print(stemmed_text)
word_tokens = nltk.tokenize.word_tokenize(stemmed_text)
print(word_tokens)
word_count = nltk.FreqDist(word_tokens)
print("Most common words :", word_count.most_common())
