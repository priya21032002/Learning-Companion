from langchain_core.output_parsers import PydanticOutputParser

from src.models.question_schemas import MCQQuestion, FillBlankQuestion
from src.prompts.templates import mcq_prompt_template, fill_blank_prompt_template
from src.llm.groq_client import get_groq_llm
from src.config.settings import settings
from src.common.logger import get_logger
from src.common.custom_exception import CustomException


class QuestionGenerator:
    def __init__(self):
        self.llm = get_groq_llm()
        self.logger = get_logger(self.__class__.__name__)

    def _retry_and_parse(self, prompt_template, parser, topic, difficulty):
        """
        Handles prompt formatting, LLM invocation, parsing, and retries.
        """
        for attempt in range(settings.MAX_RETRIES):
            try:
                self.logger.info(
                    f"Generating question | topic={topic}, difficulty={difficulty}, attempt={attempt + 1}"
                )

                # Proper PromptTemplate formatting (LangChain-native)
                formatted_prompt = prompt_template.format_prompt(
                    topic=topic,
                    difficulty=difficulty,
                    format_instructions=parser.get_format_instructions(),
                )

                response = self.llm.invoke(formatted_prompt)

                # Parse strictly using PydanticOutputParser
                parsed_output = parser.parse(response.content)

                self.logger.info("Question generated and parsed successfully")
                return parsed_output

            except Exception as e:
                self.logger.error(f"Generation attempt failed: {str(e)}")

                if attempt == settings.MAX_RETRIES - 1:
                    raise CustomException(
                        f"Generation failed after {settings.MAX_RETRIES} attempts",
                        e,
                    )

    def generate_mcq(self, topic: str, difficulty: str = "medium") -> MCQQuestion:
        """
        Generates a validated MCQ question.
        """
        try:
            parser = PydanticOutputParser(pydantic_object=MCQQuestion)

            question = self._retry_and_parse(
                mcq_prompt_template, parser, topic, difficulty
            )

            # Extra safety validation
            if len(question.options) != 4:
                raise ValueError("MCQ must contain exactly 4 options")

            if question.correct_answer not in question.options:
                raise ValueError("Correct answer must be one of the options")

            self.logger.info("Validated MCQ question successfully")
            return question

        except Exception as e:
            self.logger.error(f"MCQ generation failed: {str(e)}")
            raise CustomException("MCQ generation failed", e)

    def generate_fill_blank(
        self, topic: str, difficulty: str = "medium"
    ) -> FillBlankQuestion:
        """
        Generates a validated fill-in-the-blank question.
        """
        try:
            parser = PydanticOutputParser(pydantic_object=FillBlankQuestion)

            question = self._retry_and_parse(
                fill_blank_prompt_template, parser, topic, difficulty
            )

            # Extra safety validation
            if "___" not in question.question:
                raise ValueError("Fill-in-the-blank question must contain '___'")

            self.logger.info("Validated fill-in-the-blank question successfully")
            return question

        except Exception as e:
            self.logger.error(f"Fill-in-the-blank generation failed: {str(e)}")
            raise CustomException("Fill-in-the-blank generation failed", e)
