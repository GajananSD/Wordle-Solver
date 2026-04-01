"""
word_sort.py
------------
Filtering logic for the Wordle Solver.

The sole public function, :func:`word_sorting`, narrows the candidate word
list by applying three successive filters derived from Wordle colour feedback:

1. **Green filter** – the letter must appear at the specified position.

2. **Grey filter**  – the letter must not appear anywhere in the word.

3. **Orange filter** – the letter must appear in the word but *not* at the
   positions already tried.
"""

import random


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def word_sorting(
    gray_list: list,
    green_dict: dict,
    orange_dict: dict,
    sorted_list: list,
) -> tuple:
    """
    Return a candidate word and the updated candidate list.

    On the first call (``sorted_list`` is empty) the full word database is
    read from *words.txt*.  On subsequent calls the already-filtered list is
    used so that each new round of colour feedback further reduces the pool.

    Parameters
    ----------
    gray_list : list of str
        Letters confirmed to be absent from the target word.
    green_dict : dict
        Mapping of ``{letter: [positions]}`` for letters in the correct spot.
    orange_dict : dict
        Mapping of ``{letter: [positions]}`` for letters present but misplaced.
    sorted_list : list of str
        The candidate pool from the previous round.  Pass an empty list on the
        first invocation.

    Returns
    -------
    tuple[str, list]
        A ``(next_word, remaining_candidates)`` pair.  If no candidates remain
        ``next_word`` is ``'Not available in db'`` and the list is empty.
    """
    candidates = _load_candidates(sorted_list)
    candidates = _apply_green_filter(candidates, green_dict)
    candidates = _apply_gray_filter(candidates, gray_list)
    candidates = _apply_orange_filter(candidates, orange_dict)

    if candidates:
        return random.choice(candidates), candidates

    return "Not available in db", []


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _load_candidates(sorted_list: list) -> list:
    """
    Return the current candidate pool.

    If ``sorted_list`` is non-empty it is returned as-is.  Otherwise the full
    word database is read from *words.txt* (one five-letter word per line).
    """
    if sorted_list:
        return list(sorted_list)

    with open("words.txt", "r") as word_db:
        return [line[:5] for line in word_db]


def _apply_green_filter(candidates: list, green_dict: dict) -> list:
    """
    Keep only words where every green letter appears at its required position.
    """
    filtered = []
    for word in candidates:
        if _matches_green(word, green_dict):
            filtered.append(word)
    return filtered


def _matches_green(word: str, green_dict: dict) -> bool:
    """Return ``True`` if *word* satisfies all green constraints."""
    for letter, positions in green_dict.items():
        for pos in positions:
            if word[pos] != letter:
                return False
    return True


def _apply_gray_filter(candidates: list, gray_list: list) -> list:
    """
    Remove words that contain any letter known to be absent from the target.
    """
    return [
        word for word in candidates
        if not any(letter in word for letter in gray_list)
    ]


def _apply_orange_filter(candidates: list, orange_dict: dict) -> list:
    """
    Keep only words where every orange letter is present but not at a
    previously tried position.
    """
    filtered = []
    for word in candidates:
        if _matches_orange(word, orange_dict):
            filtered.append(word)
    return filtered


def _matches_orange(word: str, orange_dict: dict) -> bool:
    """Return ``True`` if *word* satisfies all orange constraints."""
    for letter, wrong_positions in orange_dict.items():
        # The letter must appear somewhere in the word.
        if letter not in word:
            return False
        # It must not appear at any of the positions where it was already tried.
        for pos in wrong_positions:
            if word[pos] == letter:
                return False
    return True