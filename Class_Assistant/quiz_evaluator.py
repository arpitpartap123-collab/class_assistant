"""Step 5 of the AI workflow - grade a submitted quiz.

MCQ and True/False are a straight comparison. A short answer cannot be compared
letter by letter, so it is graded with cosine similarity: the student answer and
the reference sentence are both turned into TF-IDF vectors and the angle between
them decides whether the answer is close enough.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from text_preprocessor import preprocess_all

# A short answer is accepted at or above this similarity.
SHORT_ANSWER_THRESHOLD = 0.30


def compare_texts(first, second):
    """Cosine similarity between two pieces of text, from 0.0 to 1.0."""
    first_tokens = preprocess_all(first or "")
    second_tokens = preprocess_all(second or "")

    # Ensure preprocessed tokens are joined back into text strings for TfidfVectorizer
    first_clean = " ".join(first_tokens) if isinstance(first_tokens, list) else str(first_tokens)
    second_clean = " ".join(second_tokens) if isinstance(second_tokens, list) else str(second_tokens)

    if not first_clean.strip() or not second_clean.strip():
        return 0.0

    try:
        matrix = TfidfVectorizer().fit_transform([first_clean, second_clean])
    except ValueError:
        # happens when both texts share no usable words at all
        return 0.0

    return float(cosine_similarity(matrix[0], matrix[1])[0][0])


def evaluate_answer(question_type, correct_answer, student_answer):
    """Returns (is_correct, similarity_score).

    similarity_score is None for MCQ and True/False, because those are not
    graded by similarity.
    """
    student_answer = (student_answer or "").strip()

    if question_type == "ShortAnswer":
        if not student_answer:
            return False, 0.0
        similarity = compare_texts(correct_answer, student_answer)
        return similarity >= SHORT_ANSWER_THRESHOLD, similarity

    if not student_answer:
        return False, None

    return student_answer.strip().lower() == str(correct_answer).strip().lower(), None


if __name__ == "__main__":
    reference = ("Cosine similarity measures the angle between two vectors and "
                 "returns a value between zero and one.")

    tests = [
        "It measures the angle between two vectors and gives a value from zero to one.",
        "It is the angle between vectors.",
        "The capital city of France is Paris.",
        "",
    ]

    print("MCQ        'B' vs 'B' ->", evaluate_answer("MCQ", "B", "B"))
    print("MCQ        'B' vs 'C' ->", evaluate_answer("MCQ", "B", "C"))
    print("TrueFalse  True/true  ->", evaluate_answer("TrueFalse", "True", "true"))
    print()

    for answer in tests:
        correct, score = evaluate_answer("ShortAnswer", reference, answer)
        print(f"[{'PASS' if correct else 'FAIL'}] similarity {score:.3f} <- {answer!r}")