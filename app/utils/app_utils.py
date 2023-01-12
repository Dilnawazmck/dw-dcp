# Standard Library imports
import re
from typing import List

import gensim.downloader as gensim_api

# Third-Party imports
import nltk
import numpy as np
import spacy
import transformers
from googletrans import Translator
from hashids import Hashids

# Local Source Tree imports
from app.core.config import HASH_MIN_LENGTH, HASH_SALT

_hash = Hashids(salt=HASH_SALT, min_length=HASH_MIN_LENGTH)
GENSIM_NLP = gensim_api.load("glove-wiki-gigaword-300")
SPACY_NLP = spacy.load("en_core_web_lg")


def utils_preprocess_text(text, flg_stemm=False, flg_lemm=True, lst_stopwords=None):
    """
    Preprocess a string.
    :parameter
        :param text: string - name of column containing text
        :param lst_stopwords: list - list of stopwords to remove
        :param flg_stemm: bool - whether stemming is to be applied
        :param flg_lemm: bool - whether lemmitisation is to be applied
    :return
        cleaned text
    """

    if lst_stopwords is None:
        lst_stopwords = nltk.corpus.stopwords.words("english")

    ## clean (convert to lowercase and remove punctuations and characters and then strip)
    text = re.sub(r"[^\w\s]", "", str(text).lower().strip())

    ## Tokenize (convert from string to list)
    lst_text = text.split()
    ## remove Stopwords
    if lst_stopwords is not None:
        lst_text = [word for word in lst_text if word not in lst_stopwords]

    ## Stemming (remove -ing, -ly, ...)
    if flg_stemm:
        ps = nltk.stem.porter.PorterStemmer()
        lst_text = [ps.stem(word) for word in lst_text]

    ## Lemmatisation (convert the word into root word)
    if flg_lemm:
        lem = nltk.stem.wordnet.WordNetLemmatizer()
        lst_text = [lem.lemmatize(word) for word in lst_text]

    ## back to string from list
    text = " ".join(lst_text)
    return text


def get_similar_words(lst_words, top):
    similar_words_list: list = lst_words.copy()
    result = set()
    try:
        for tupla in GENSIM_NLP.most_similar(lst_words, topn=top):
            similar_words_list.append(tupla[0])
    except KeyError:
        return []
    doc = SPACY_NLP(" ".join(similar_words_list))

    for d in doc:
        if d.lemma_.lower() in lst_words:
            continue
        result.add(d.lemma_.lower())
    return list(result)[:5]


def bert_embedding(txt):
    tokenizer = transformers.BertTokenizer.from_pretrained(
        "bert-base-uncased", do_lower_case=True
    )
    nlp = transformers.TFBertModel.from_pretrained("bert-base-uncased")
    idx = tokenizer.encode(txt)
    idx = np.array(idx)[None, :]
    embedding = nlp(idx)
    X = np.array(embedding[0][0][1:-1])
    return X


def translate(text: str, **kwargs):
    translator = Translator()
    translated = translator.translate(text, **kwargs)
    return translated.text, translated.src, translated.dest


def hash_response(data, columns: List):
    for col in columns:
        setattr(data, col, _hash.encode(getattr(data, col)))
