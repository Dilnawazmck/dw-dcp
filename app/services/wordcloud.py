# Standard Library imports
import re
from collections import defaultdict

# Third-Party imports

# Local Source Tree imports


def get_words_with_frequency_from_document(doc: str, stopwords_dict: dict, nlp) -> dict:
    """Ignores all the stopwords, applies lemmatization and then returns the tokens with frequency.

    Args:
        doc (str): Text for which the token are to be generated with frequency.
        stopwords_dict (dict): Stopwords dict for the language
        nlp: Spacy instance

    Returns:
        dict: Dict containing tokens as keys and their frequency as value

    Raises:
        N/A

    Examples:
        >>> get_words_with_frequency_from_document("This is a Sample document for token. Check Tokens       ")
        {'sample': 1, 'document': 1, 'token': 2, 'check': 1}
    """

    token_dict: dict = defaultdict(int)

    # Remove anything that is not a word
    document: str = re.sub("[^a-zA-Z]", " ", doc)

    # Remove all the tabs and new lines
    document: str = " ".join(document.split())

    doc = nlp(document)

    for d in doc:
        if stopwords_dict[d.lemma_.lower()] or not d.lemma_.strip():
            continue
        token_dict[d.lemma_.lower()] += 1

    return token_dict
