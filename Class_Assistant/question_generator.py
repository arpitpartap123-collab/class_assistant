"""Step 4 of the AI workflow - build the questionnaire from the lecture text.

Three kinds of question are produced:

    MCQ         an important keyword is removed from a sentence and the student
                has to choose it back. The three wrong options are keywords that
                behave like the answer, found with cosine similarity between the
                TF-IDF column vectors of the terms.

    TrueFalse   a real sentence is shown unchanged (True) or with its keyword
                swapped for a similar keyword (False).

    ShortAnswer the student explains a keyword in their own words. The sentence
                that best defines that keyword is stored as the reference answer
                and quiz_evaluator.py grades against it with cosine similarity.
"""

import re
import random

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from text_preprocessor import split_sentences, preprocess_all

DEFAULT_MCQ = 5
DEFAULT_TRUE_FALSE = 3
DEFAULT_SHORT_ANSWER = 2

BLANK = "________"

# A very long "sentence" is usually a heading that got joined to the paragraph
# after it, which makes an ugly question.
MAX_SENTENCE_WORDS = 45

# Very short keywords ("inverse", "set") make poor short answer questions.
MIN_KEYWORD_LENGTH = 4


# --------------------------------------------------------------- internals ---
def _build_model(text):
    """Returns (sentences, vectorizer, matrix) or None when there is too little text."""
    sentences = split_sentences(text)
    if len(sentences) < 3:
        return None

    cleaned = preprocess_all(sentences)
    keep = [i for i, c in enumerate(cleaned) if c.strip()]
    if len(keep) < 3:
        return None

    sentences = [sentences[i] for i in keep]
    cleaned = [cleaned[i] for i in keep]

    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform(cleaned)
    return sentences, vectorizer, matrix


def _keywords(vectorizer, matrix, top_n=30):
    """The terms with the highest total TF-IDF weight in the whole lecture."""
    terms = vectorizer.get_feature_names_out()
    weights = np.asarray(matrix.sum(axis=0)).flatten()
    order = np.argsort(weights)[::-1][:top_n]
    return [str(terms[i]) for i in order]


def _best_sentence_for(vectorizer, matrix, term):
    """Index of the sentence where this term carries the most weight."""
    terms = vectorizer.get_feature_names_out()
    found = np.where(terms == term)[0]
    if len(found) == 0:
        return None

    column = matrix[:, found[0]].toarray().flatten()
    if column.max() <= 0:
        return None
    return int(column.argmax())


def _similar_terms(vectorizer, matrix, term, count, avoid_sentence=""):
    """Terms used in the same kind of context as `term`.

    Each term is a column of the TF-IDF matrix, so transposing gives one vector
    per term. Terms with a high cosine similarity appear in the same sentences,
    which makes them believable wrong options.
    """
    terms = list(vectorizer.get_feature_names_out())
    if term not in terms:
        return []

    index = terms.index(term)
    term_vectors = matrix.T.tocsr()
    similarity = cosine_similarity(term_vectors[index], term_vectors).flatten()

    lowered = avoid_sentence.lower()
    picked = []
    for i in np.argsort(similarity)[::-1]:
        candidate = str(terms[i])
        if candidate == term:
            continue
        # a word already visible in the sentence would give the answer away
        if candidate in lowered:
            continue
        picked.append(candidate)
        if len(picked) >= count:
            break
    return picked


def _find_word(sentence, keyword):
    """Locates the keyword inside the original sentence, allowing word endings."""
    return re.search(rf"\b{re.escape(keyword)}\w*\b", sentence, re.IGNORECASE)


def _blank_question(sentence):
    return f"Fill in the blank:  {sentence}"


# ------------------------------------------------------------------- MCQ ----
def generate_mcq(sentences, vectorizer, matrix, keywords, count, used_keywords):
    questions = []
    used_sentences = set()

    for keyword in keywords:
        if len(questions) >= count:
            break
        if keyword in used_keywords:
            continue

        index = _best_sentence_for(vectorizer, matrix, keyword)
        if index is None or index in used_sentences:
            continue

        sentence = sentences[index]
        if len(sentence.split()) > MAX_SENTENCE_WORDS:
            continue

        match = _find_word(sentence, keyword)
        if match is None:
            continue

        answer = match.group(0)
        blanked = sentence[:match.start()] + BLANK + sentence[match.end():]

        distractors = _similar_terms(vectorizer, matrix, keyword, 3, sentence)
        distractors = [d for d in distractors if d.lower() != answer.lower()]
        if len(distractors) < 3:
            continue

        options = [answer] + distractors[:3]
        random.shuffle(options)

        questions.append({
            "question_type": "MCQ",
            "question_text": _blank_question(blanked),
            "option_a": options[0],
            "option_b": options[1],
            "option_c": options[2],
            "option_d": options[3],
            "correct_answer": "ABCD"[options.index(answer)],
            "marks": 1,
        })
        used_sentences.add(index)
        used_keywords.add(keyword)

    return questions


# ------------------------------------------------------------ True / False ---
def generate_true_false(sentences, vectorizer, matrix, keywords, count, used_keywords):
    questions = []
    used_sentences = set()
    make_true = True

    for keyword in keywords:
        if len(questions) >= count:
            break
        if keyword in used_keywords:
            continue

        index = _best_sentence_for(vectorizer, matrix, keyword)
        if index is None or index in used_sentences:
            continue

        sentence = sentences[index]
        if len(sentence.split()) > MAX_SENTENCE_WORDS:
            continue

        if make_true:
            questions.append({
                "question_type": "TrueFalse",
                "question_text": sentence,
                "option_a": None, "option_b": None,
                "option_c": None, "option_d": None,
                "correct_answer": "True",
                "marks": 1,
            })
            used_sentences.add(index)
            used_keywords.add(keyword)
            make_true = False
            continue

        # Build a false version by swapping the keyword for a similar term.
        match = _find_word(sentence, keyword)
        if match is None:
            continue

        replacements = _similar_terms(vectorizer, matrix, keyword, 1, sentence)
        if not replacements:
            continue

        corrupted = sentence[:match.start()] + replacements[0] + sentence[match.end():]
        if corrupted == sentence:
            continue

        questions.append({
            "question_type": "TrueFalse",
            "question_text": corrupted,
            "option_a": None, "option_b": None,
            "option_c": None, "option_d": None,
            "correct_answer": "False",
            "marks": 1,
        })
        used_sentences.add(index)
        used_keywords.add(keyword)
        make_true = True

    return questions


# ---------------------------------------------------------- Short Answer ----
def _defines_term(sentence, keyword):
    """True when the sentence begins with the keyword, as a definition does:
    'Training is the process of ...' defines 'training'."""
    return re.match(rf"\b{re.escape(keyword)}\w*\b", sentence, re.IGNORECASE) is not None


def generate_short_answer(sentences, vectorizer, matrix, keywords, count, used_keywords):
    questions = []
    used_sentences = set()

    # First pass takes only terms the lecture actually defines, which gives
    # questions like "Explain the term 'training'". The second pass relaxes the
    # rule, but only if the first pass could not make enough questions.
    for definitions_only in (True, False):
        for keyword in keywords:
            if len(questions) >= count:
                break
            if keyword in used_keywords or len(keyword) < MIN_KEYWORD_LENGTH:
                continue

            index = _best_sentence_for(vectorizer, matrix, keyword)
            if index is None or index in used_sentences:
                continue

            reference = sentences[index]
            length = len(reference.split())
            if length < 6 or length > MAX_SENTENCE_WORDS:
                continue

            if definitions_only and not _defines_term(reference, keyword):
                continue

            questions.append({
                "question_type": "ShortAnswer",
                "question_text": f"Explain the term '{keyword}' in your own words.",
                "option_a": None, "option_b": None,
                "option_c": None, "option_d": None,
                "correct_answer": reference,     # graded by cosine similarity
                "marks": 2,
            })
            used_sentences.add(index)
            used_keywords.add(keyword)

        if len(questions) >= count:
            break

    return questions


# ------------------------------------------------------------------ main ----
def generate_questions(text, mcq_count=DEFAULT_MCQ,
                       true_false_count=DEFAULT_TRUE_FALSE,
                       short_answer_count=DEFAULT_SHORT_ANSWER):
    """Returns a list of question dictionaries ready to insert into the DB."""
    model = _build_model(text)
    if model is None:
        return []

    sentences, vectorizer, matrix = model
    keywords = _keywords(vectorizer, matrix)
    if not keywords:
        return []

    # Shared between the three generators so that no keyword is asked twice.
    used_keywords = set()

    questions = []
    questions += generate_mcq(sentences, vectorizer, matrix, keywords,
                              mcq_count, used_keywords)
    questions += generate_true_false(sentences, vectorizer, matrix, keywords,
                                     true_false_count, used_keywords)
    questions += generate_short_answer(sentences, vectorizer, matrix, keywords,
                                       short_answer_count, used_keywords)
    return questions


if __name__ == "__main__":
    import sys
    from Pdf_Extractor import extract_text

    if len(sys.argv) < 2:
        print("usage: python question_generator.py <file.pdf>")
    else:
        for i, q in enumerate(generate_questions(extract_text(sys.argv[1])), start=1):
            print(f"{i}. [{q['question_type']}] {q['question_text']}")
            if q["question_type"] == "MCQ":
                print(f"   A) {q['option_a']}    B) {q['option_b']}")
                print(f"   C) {q['option_c']}    D) {q['option_d']}")
            print(f"   answer: {q['correct_answer']}\n")
