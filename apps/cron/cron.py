import os
import random
from datetime import datetime
from dotenv import load_dotenv

from django.db.models.manager import BaseManager

from apps.authentication.models import User
from apps.language_practice.models import UserVocabulary, Language
from apps.llm.utils import practice

load_dotenv()

WORDS_TO_SEND: int = int(os.getenv("WORDS_TO_SEND", 5))
QTD_EXTRA_WORDS: int = int(os.getenv("QTD_EXTRA_WORDS", 4))

def generate_email_content():
    try:
        users: BaseManager[User] = User.objects.filter(is_active=True, keep_sending_taks=True)
        languages: BaseManager[Language] = Language.objects.filter(enable=True)

        for user in users:
            user_vocabulary: BaseManager[UserVocabulary] = UserVocabulary.objects.filter(user=user, enable=True)

            for language in languages:
                user_vocabulary_language = user_vocabulary.filter(vocabulary__language=language)

                if user_vocabulary_language.exists():
                    vocab_for_practice: list[UserVocabulary] = []
                    practiced_vocab: list[str] = []
                    for uv in user_vocabulary:
                        if uv.ready_for_practice:
                            vocab_for_practice.append(uv)
                        else:
                            practiced_vocab.append(uv.vocabulary.word_vocab)

                    chosen_vocab: list[UserVocabulary] = sorted(vocab_for_practice, key=lambda x: x.practice_count, reverse=True)[:min(WORDS_TO_SEND, len(vocab_for_practice))]
                    extra_words: list[str] = random.sample(practiced_vocab, min(QTD_EXTRA_WORDS, len(practiced_vocab)))

                    words: list[str] = [vocab.vocabulary.word_vocab for vocab in chosen_vocab]

                    practice(words=words, language=language, user=user, extra_words=extra_words)

                    for user_vocab in chosen_vocab:
                        user_vocab.practice_count += 1
                        user_vocab.last_practiced = datetime.now()
                    
                    UserVocabulary.objects.bulk_update(objs=chosen_vocab, fields=["practice_count", "last_practiced"])
    except Exception as e:
        raise e
