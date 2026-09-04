import os

from connection import connect
from Pdf_Extractor import extract_text
from notes_generator import generate_notes
from question_generator import generate_questions


PDF_DIR = "lecturePdf"
MIN_WORDS = 50


def process_lecture(lecture_id, note_count=8,
                    mcq_count=5,
                    true_false_count=3,
                    short_answer_count=2):

    conn = connect()
    cr = conn.cursor()

    q = '''
    select pdf_file
    from Lectures
    where id = %s
    '''

    cr.execute(q, (lecture_id,))

    row = cr.fetchone()

    if row is None:
        conn.close()
        raise Exception("Lecture not found")

    pdf_file = row[0]

    pdf_path = os.path.join(
        PDF_DIR,
        pdf_file
    )

    if not os.path.exists(pdf_path):
        conn.close()
        raise Exception("PDF file not found")

    text = extract_text(pdf_path)

    if len(text.split()) < MIN_WORDS:
        conn.close()
        raise Exception(
            "PDF does not contain enough readable text"
        )

    # Save extracted text
    q = '''
    update Lectures
    set extracted_text = %s
    where id = %s
    '''

    cr.execute(
        q,
        (text, lecture_id)
    )

    # Delete old notes
    q = '''
    delete from Notes
    where lecture_id = %s
    '''

    cr.execute(
        q,
        (lecture_id,)
    )

    # Generate Important Notes
    notes = generate_notes(
        text,
        note_count
    )

    # Insert Notes
    q = '''
    insert into Notes
    (lecture_id, note_text, rank_score, sentence_index)
    values (%s, %s, %s, %s)
    '''

    for note in notes:

        cr.execute(
            q,
            (
                lecture_id,
                note[0],
                note[1],
                note[2]
            )
        )

    # Delete old questions
    q = '''
    delete from Questions
    where lecture_id = %s
    '''

    cr.execute(
        q,
        (lecture_id,)
    )

    # Generate Questions
    questions = generate_questions(
        text,
        mcq_count,
        true_false_count,
        short_answer_count
    )

    # Insert Questions
    q = '''
    insert into Questions
    (lecture_id, question_type, question_text,
     option_a, option_b, option_c, option_d,
     correct_answer)
    values (%s, %s, %s, %s, %s, %s, %s, %s)
    '''

    for question in questions:

        cr.execute(
            q,
            (
                lecture_id,
                question["question_type"],
                question["question_text"],
                question["option_a"],
                question["option_b"],
                question["option_c"],
                question["option_d"],
                question["correct_answer"]
            )
        )

    conn.commit()
    conn.close()

    return len(notes), len(questions)