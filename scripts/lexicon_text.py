#!/usr/bin/env python3
"""Text-preserving helpers for lexicon candidate extraction."""

from __future__ import annotations


HEADWORD_TRAILING_MARKS = " .,:;^-—–"


def clean_headword_boundary(text: str) -> str:
    """Remove separator punctuation without deleting lexical letters.

    Historical Spanish guide words frequently end in ``r`` (especially
    infinitives). The extraction boundary cleaner therefore strips only known
    punctuation/separator marks and never alphabetic characters.
    """
    return text.rstrip(HEADWORD_TRAILING_MARKS)
