# tooling.py

from typing import List, Dict
from pydantic import BaseModel, Field


class QuizToolArgs(BaseModel):
    """
    Pydantic arguments schema for quiz tool
    """
    language: str = Field(description="Language of the quiz")
    subject: str = Field(description="Subject of the quiz")
    session_id: str = Field(description="Session ID for the quiz")
    correct_option: int = Field(description="Index of the correct option in the quiz")
    language_index: int = Field(description="Index of the selected language")
    type: str = Field('quiz', description="""Always should be equal to 'quiz' for quiz generation""")


def quiz_tool(language: str, subject: str, session_id: str, correct_option: int, language_index: int, type: str) -> str:
    response = QuizToolArgs(
        language=language,
        subject=subject,
        session_id=session_id,
        correct_option=correct_option - 1,
        language_index=language_index,
        type=type
    )
    return response.json()

class WordsToolArgs(BaseModel):
    """
    Pydantic arguments schema for words tool
    """
    topic: str = Field(description="Topic for creating words")
    session_id: str = Field(description="Session ID for the words task")
    language_index: int = Field(description="Index of the selected language")
    type: str = Field('words', description="""Always should be equal to 'words' for words generation""")

#    words: Dict[str, str] = Field(description="Dictionary of words and their translations")

def words_tool(topic: str, session_id: str, language_index: int, type: str) -> str:
    response = WordsToolArgs(
        topic=topic,
        session_id=session_id,
        language_index=language_index,
        type=type
    )
    return response.json()

class SentencesToolArgs(BaseModel):
    """
    Pydantic arguments schema for sentences tool
    """
    topic: str = Field(description="Topic for creating sentences")
    session_id: str = Field(description="Session ID for the sentences task")
    language_index: int = Field(description="Index of the selected language")
    type: str = Field('sentences', description="""Always should be equal to 'sentences' for sentences generation""")
#    words: Dict[str, str] = Field(description="Dictionary of words and their translations")

def sentences_tool(topic: str, session_id: str, language_index: int, type: str) -> str:
    response = SentencesToolArgs(
        topic=topic,
        session_id=session_id,
        language_index=language_index,
        type=type
    )
    return response.json()

class SongToolArgs(BaseModel):
    """
    Pydantic arguments schema for sentences tool
    """
    topic: str = Field(description="Words and task to creating song from")
    session_id: str = Field(description="Session ID for the sentences task")
    language_index: int = Field(description="Index of the selected language")
    type: str = Field('song', description="""Always should be equal to 'song' for song generation""")
#    words: Dict[str, str] = Field(description="Dictionary of words and their translations")

def song_tool(topic: str, session_id: str, language_index: int, type: str) -> str:
    response = SentencesToolArgs(
        topic=topic,
        session_id=session_id,
        language_index=language_index,
        type=type
    )
    return response.json()