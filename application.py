import os
import streamlit as st
from dotenv import load_dotenv

from src.utils.helpers import QuizManager, rerun
from src.generator.question_generator import QuestionGenerator

load_dotenv()


# -------------------- Custom CSS --------------------
def load_css():
    st.markdown(
        """
        <style>
        .main-title {
            font-size: 42px;
            font-weight: 700;
            text-align: center;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #6c757d;
            margin-bottom: 40px;
        }
        .card {
            background-color: #ffffff;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.06);
            margin-bottom: 25px;
        }
        .score-card {
            background: linear-gradient(135deg, #6f42c1, #4dabf7);
            color: white;
            padding: 25px;
            border-radius: 14px;
            text-align: center;
            margin-bottom: 30px;
        }
        .divider {
            margin: 30px 0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def main():
    st.set_page_config(
        page_title="Learning Companion AI NEW",
        page_icon="🎓",
        layout="wide"
    )

    load_css()

    # -------------------- Session State Init --------------------
    if "quiz_manager" not in st.session_state:
        st.session_state.quiz_manager = QuizManager()

    if "quiz_generated" not in st.session_state:
        st.session_state.quiz_generated = False

    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False

    if "rerun_trigger" not in st.session_state:
        st.session_state.rerun_trigger = False

    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}

    # -------------------- Header --------------------
    st.markdown('<div class="main-title">🎓 Learning Companion</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">AI-powered quizzes that adapt to your learning</div>',
        unsafe_allow_html=True
    )

    # -------------------- Sidebar --------------------
    st.sidebar.title("⚙️ Quiz Control Panel")

    question_type = st.sidebar.selectbox(
        "Question Format",
        ["Multiple Choice", "Fill in the Blank"],
        index=0
    )

    topic = st.sidebar.text_input(
        "Quiz Topic",
        placeholder="Indian History, Geography"
    )

    difficulty = st.sidebar.selectbox(
        "Difficulty",
        ["Easy", "Medium", "Hard"],
        index=1
    ).lower()

    num_questions = st.sidebar.slider(
        "Number of Questions",
        min_value=1,
        max_value=10,
        value=5
    )

    st.sidebar.markdown("---")

    if st.sidebar.button("🚀 Generate Quiz", use_container_width=True):
        st.session_state.quiz_submitted = False
        st.session_state.quiz_generated = False
        st.session_state.user_answers = {}

        generator = QuestionGenerator()

        success = st.session_state.quiz_manager.generate_questions(
            generator=generator,
            topic=topic,
            question_type=question_type,
            difficulty=difficulty,
            num_questions=num_questions
        )

        st.session_state.quiz_generated = success
        rerun()

    # -------------------- Quiz Section --------------------
    if st.session_state.quiz_generated and st.session_state.quiz_manager.questions:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.header("📝 Your Quiz")

            if not st.session_state.quiz_submitted:
                st.session_state.quiz_manager.attempt_quiz()

                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

                if st.button("✅ Submit Quiz", use_container_width=True):
                    st.session_state.quiz_manager.evaluate_quiz()
                    st.session_state.quiz_submitted = True
                    rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    # -------------------- Results Section --------------------
    if st.session_state.quiz_submitted:
        results_df = st.session_state.quiz_manager.generate_result_dataframe()

        if not results_df.empty:
            correct_count = int(results_df["is_correct"].sum())
            total_questions = len(results_df)
            score_percentage = (correct_count / total_questions) * 100

            st.markdown(
                f"""
                <div class="score-card">
                    <h2>🎯 Your Score</h2>
                    <h1>{score_percentage:.2f}%</h1>
                    <p>{correct_count} out of {total_questions} correct</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            for _, result in results_df.iterrows():
                with st.container():
                    st.markdown('<div class="card">', unsafe_allow_html=True)

                    q_no = result["question_number"]

                    if result["is_correct"]:
                        st.success(f"Question {q_no}")
                    else:
                        st.error(f"Question {q_no}")

                    st.write(result["question"])

                    if not result["is_correct"]:
                        st.write(f"Your answer: **{result['user_answer']}**")
                        st.write(f"Correct answer: **{result['correct_answer']}**")

                    st.markdown('</div>', unsafe_allow_html=True)

            # -------------------- Save Results --------------------
            if st.button("💾 Save Results", use_container_width=True):
                saved_file = st.session_state.quiz_manager.save_to_csv()

                if saved_file:
                    with open(saved_file, "rb") as f:
                        st.download_button(
                            label="⬇️ Download CSV",
                            data=f.read(),
                            file_name=os.path.basename(saved_file),
                            mime="text/csv"
                        )
                else:
                    st.warning("No results available to save")


if __name__ == "__main__":
    main()
