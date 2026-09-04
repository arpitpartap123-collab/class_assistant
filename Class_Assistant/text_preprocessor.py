import re
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS


def split_sentences(text):
    sentences = re.split(
        r'(?<=[.!?])\s+',
        text
    )

    sentences = [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]

    return sentences


def preprocess_all(sentences):
    result = []

    for sentence in sentences:

        sentence = sentence.lower()

        sentence = re.sub(
            r'[^a-zA-Z0-9\s]',
            '',
            sentence
        )

        words = sentence.split()

        words = [
            word
            for word in words
            if word not in ENGLISH_STOP_WORDS
        ]

        result.append(
            " ".join(words)
        )

    return result