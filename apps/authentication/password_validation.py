import re
import string

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import MinimumLengthValidator

"""
This module defines a set of password validators for Django authentication.

These validators enforce specific password requirements, including:
- Minimum length of 8 characters.
- At least 1 digit (0-9).
- At least 1 letter.
- At least 1 special character from the set ()[]{}|`~!@#$%^&*_-+=;:'",<>./?
- No sequences of 3 or more digits (e.g., '123' or '456').
- No sequences of 3 or more letters (e.g., 'abc' or 'xyz').

To use these validators, you can add them to the `AUTH_PASSWORD_VALIDATORS` setting
in your Django project's settings.py file.

"""


class NumberValidator(object):
    def validate(self, password, user=None):
        if not re.findall('\d', password):
            raise ValidationError(
                _("The password must contain at least 1 digit, 0-9."),
                code='password_no_number',
            )

    def get_help_text(self):
        return _("Your password must contain at least 1 digit, 0-9.")


class LetterValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[a-zA-z]', password):
            raise ValidationError(
                _("The password must contain at least 1 letter."),
                code='password_no_letter',
            )

    def get_help_text(self):
        return _("Your password must contain at least 1.")


class SymbolValidator(object):
    def validate(self, password, user=None):
        if not re.findall(
            r'[{}]'.format(re.escape(string.punctuation)), password
        ):
            raise ValidationError(
                _(
                    "The password must contain at least 1 special character: "
                    + "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?"
                ),
                code='password_no_symbol',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 special character: "
            + "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?"
        )


class NumberSequenceValidator(object):
    """
    Validate whether the password is not contain number sequence such as '456'.
    """

    sequence = '0123456789'
    reversed_sequence = sequence[::-1]

    def __init__(self, sequence_length=3):
        self.sequence_length = sequence_length

    def _get_sequence_pieces(self, sequence):
        origin_sequence = sequence[:]
        sequence = (origin_sequence[num : num + self.sequence_length] for num, i in enumerate(sequence))
        return filter(lambda x: len(x) == self.sequence_length, sequence)

    def _get_validation_regex(self):
        pieces = self._get_sequence_pieces(self.sequence)
        reversed_pieces = self._get_sequence_pieces(self.reversed_sequence)
        simple_pieces = (x * self.sequence_length for x in self.sequence)
        pieces = tuple(pieces) + tuple(reversed_pieces) + tuple(simple_pieces)
        pieces = '|'.join(pieces)

        return f'({pieces})'

    def validate(self, password, user=None):
        validation_regex = self._get_validation_regex()
        if re.search(validation_regex, password):
            raise ValidationError(
                _("This password contains a sequence of %(sequence)d digits.")
                % {"sequence": self.sequence_length},
                code='password_contain_digit_sequence',
            )

    def get_help_text(self):
        return _(
            "Your password can't contain a sequence of %(sequence)d digits."
        ) % {"sequence": self.sequence_length}


class LetterSequenceValidator(object):
    """
    Validate whether the password is not contain letter sequence such as 'abc'.
    """

    sequence = string.ascii_letters
    reversed_sequence = sequence[::-1]

    def __init__(self, sequence_length=3):
        self.sequence_length = sequence_length

    def _get_sequence_pieces(self, sequence):
        origin_sequence = sequence[:]
        sequence = (
            origin_sequence[num : num + self.sequence_length]
            for num, i in enumerate(sequence)
        )
        return filter(lambda x: len(x) == self.sequence_length, sequence)

    def _get_validation_regex(self):
        pieces = self._get_sequence_pieces(self.sequence)
        reversed_pieces = self._get_sequence_pieces(self.reversed_sequence)
        simple_pieces = (x * self.sequence_length for x in self.sequence)
        pieces = tuple(pieces) + tuple(reversed_pieces) + tuple(simple_pieces)
        pieces = '|'.join(pieces)

        return f'({pieces})'

    def validate(self, password, user=None):
        validation_regex = self._get_validation_regex()
        if re.search(validation_regex, password):
            raise ValidationError(
                _('This password contains a sequence of %(sequence)d letters.')
                % {"sequence": self.sequence_length},
                code='password_contain_letter_sequence',
            )

    def get_help_text(self):
        return _(
            "Your password can't contain a sequence of %(sequence)d "
            "letters."
        ) % {"sequence": self.sequence_length}


validators = [
    MinimumLengthValidator(8),
    NumberValidator(),
    LetterValidator(),
    SymbolValidator(),
    NumberSequenceValidator(),
    LetterSequenceValidator(),
]