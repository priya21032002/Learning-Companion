import os
import streamlit as st
import pandas as pd
from src.generator.question_generator import QuestionGenerator


def rerun():
    st.session_state['rerun_trigger'] = not st.session_state.get('rerun_trigger', False)


class QuizManager:
    def __init__(self):
        self.questions = []
        self.results = []

    def generate_questions(
        self,
        generator: QuestionGenerator,
        topic: str,
        question_type: str,
        difficulty: str,
        num_questions: int
    ):
        self.questions = []
        self.results = []
        st.session_state.user_answers = {}

        try:
            for _ in range(num_questions):
                if question_type == "Multiple Choice":
                    q = generator.generate_mcq(topic, difficulty.lower())
                    self.questions.append({
                        "type": "MCQ",
                        "question": q.question,
                        "options": q.options,
                        "correct_answer": q.correct_answer
                    })
                else:
                    q = generator.generate_fill_blank(topic, difficulty.lower())
                    self.questions.append({
                        "type": "Fill in the blank",
                        "question": q.question,
                        "correct_answer": q.answer
                    })

        except Exception as e:
            st.error(f"Error generating questions: {e}")
            return False

        return True

    def attempt_quiz(self):
        for i, q in enumerate(self.questions, start=1):
            st.markdown(f"**Question {i}:** {q['question']}")

            if q["type"] == "MCQ":
                answer = st.radio(
                    "Select an answer",
                    q["options"],
                    key=f"mcq_{i}"
                )
                st.session_state.user_answers[i] = answer

            else:
                answer = st.text_input(
                    "Your answer",
                    key=f"fill_blank_{i}"
                )
                st.session_state.user_answers[i] = answer

            st.markdown("---")

    def evaluate_quiz(self):
        self.results = []

        for i, q in enumerate(self.questions, start=1):
            user_answer = st.session_state.user_answers.get(i, "").strip()
            correct_answer = q["correct_answer"].strip()

            is_correct = (
                user_answer.lower() == correct_answer.lower()
            )

            self.results.append({
                "question_number": i,
                "question": q["question"],
                "question_type": q["type"],
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct
            })

    def generate_result_dataframe(self):
        if not self.results:
            return pd.DataFrame()
        return pd.DataFrame(self.results)

    def save_to_csv(self, filename_prefix="quiz_results"):
        if not self.results:
            st.warning("No results to save")
            return None

        df = self.generate_result_dataframe()

        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.csv"

        os.makedirs("results", exist_ok=True)
        path = os.path.join("results", filename)

        df.to_csv(path, index=False)
        return path
