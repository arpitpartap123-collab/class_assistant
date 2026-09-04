"""Step 3 of the AI workflow - extractive summarization with TF-IDF + cosine.

How the important notes are chosen:

    1. break the lecture into sentences
    2. convert every sentence into a TF-IDF vector
    3. average all the vectors, giving one 'centroid' vector for the lecture
    4. score each sentence by its cosine similarity with the centroid,
       so a sentence close to the overall topic scores high
    5. keep the best sentences and put them back into reading order
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from text_preprocessor import split_sentences, preprocess_all

DEFAULT_NOTE_COUNT = 8


def generate_notes(text, max_notes=DEFAULT_NOTE_COUNT):
    """Returns a list of (sentence, score, sentence_index)."""
    sentences = split_sentences(text)
    if len(sentences) < 2:
        return []

    cleaned = preprocess_all(sentences)

    # A sentence made only of stopwords becomes empty and must be dropped,
    # but the original position is kept so notes stay in reading order.
    keep = [i for i, c in enumerate(cleaned) if c.strip()]
    if len(keep) < 2:
        return []

    sentences = [sentences[i] for i in keep]
    cleaned = [cleaned[i] for i in keep]

    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform(cleaned)

    centroid = np.asarray(matrix.mean(axis=0))
    scores = cosine_similarity(matrix, centroid).flatten()

    count = min(max_notes, len(sentences))
    best = np.argsort(scores)[::-1][:count]
    best = sorted(int(i) for i in best)

    return [(sentences[i], float(scores[i]), i) for i in best]


if __name__ == "__main__":
    import sys
    from Pdf_Extractor import extract_text

    if len(sys.argv) < 2:
        print("usage: python notes_generator.py <file.pdf>")
    else:
        notes = generate_notes(extract_text(sys.argv[1]))
        print(f"{len(notes)} important notes\n")
        for i, (sentence, score, index) in enumerate(notes, start=1):
            print(f"{i}. [score {score:.3f}] {sentence}\n")
