"""
app.py
------
Flask application for the Wordle Solver.

Routes
------
GET  /                  – Render the main game page.

POST /submit_guess      – Accept a guessed word with its tile colours and
                          return the next suggested word.
                          
POST /submit_user_word  – Accept a user-supplied word and persist it to the
                          word database.
"""

from flask import Flask, jsonify, render_template, request
import requests

from word_sort import word_sorting

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Initial seed guesses presented to the user before the solver takes over.
# ---------------------------------------------------------------------------
INITIAL_GUESSES = ["riots", "candy", "plume"]

# ---------------------------------------------------------------------------
# Session state (module-level globals, reset on each page load).
# ---------------------------------------------------------------------------
current_word_index: int = 0
sorted_list: list = []

green_dict: dict = {}   # {letter: [positions]}  – correct letter, correct spot
orange_dict: dict = {}  # {letter: [positions]}  – correct letter, wrong spot
gray_list: list = []    # [letters]               – letter not in word


def _reset_state() -> None:
    """Reset all solver state to its initial values."""
    global current_word_index, green_dict, orange_dict, gray_list, sorted_list
    current_word_index = 0
    green_dict = {}
    orange_dict = {}
    gray_list = []
    sorted_list = []


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Render the game page and reset solver state."""
    _reset_state()
    return render_template("index.html", word=INITIAL_GUESSES[current_word_index])


@app.route("/submit_guess", methods=["POST"])
def submit_guess():
    """
    Process the player's colour feedback for the current guess.

    Expected JSON body
    ------------------
    {
        "word":   "<five-letter word>",
        "colors": ["green" | "orange" | "grey", ...]   # one entry per letter
    }

    Returns
    -------
    JSON response containing:
    - result        : status message shown to the user
    - next_word     : next word to guess, or null
    - all_green     : true when the word has been solved
    - show_user_input : true when the user must supply a missing word
    """
    global current_word_index, green_dict, orange_dict, gray_list, sorted_list

    data = request.get_json()
    guessed_word: str = data.get("word", "")
    guessed_colors: list = data.get("colors", [])

    # ------------------------------------------------------------------ #
    # Update colour dictionaries from this round's feedback.              #
    # ------------------------------------------------------------------ #
    for index, color in enumerate(guessed_colors):
        letter = guessed_word[index].lower()

        if color == "green":
            green_dict.setdefault(letter, [])
            if index not in green_dict[letter]:
                green_dict[letter].append(index)

        elif color == "orange":
            orange_dict.setdefault(letter, [])
            if index not in orange_dict[letter]:
                orange_dict[letter].append(index)

        elif color == "grey":
            # Only add to gray_list if the letter has no confirmed positions.
            if letter not in green_dict and letter not in orange_dict:
                if letter not in gray_list:
                    gray_list.append(letter)

    # ------------------------------------------------------------------ #
    # Determine the response.                                             #
    # ------------------------------------------------------------------ #
    all_green = all(color == "green" for color in guessed_colors)

    if all_green:
        response = {
            "result": "Guessed the correct word!!!",
            "next_word": None,
            "all_green": True,
            "show_user_input": False,
        }
        return jsonify(response)

    current_word_index += 1

    # Still within the pre-defined seed guesses.
    if current_word_index < len(INITIAL_GUESSES):
        response = {
            "result": "Check above guess",
            "next_word": INITIAL_GUESSES[current_word_index],
            "all_green": False,
            "show_user_input": False,
        }
        return jsonify(response)

    # Hand off to the word-sorting solver (up to 5 total attempts).
    if current_word_index <= 5:
        next_word, sorted_list = word_sorting(
            gray_list, green_dict, orange_dict, sorted_list
        )

        # Remove that given guess so it does not repeat in future
        sorted_list.remove(next_word)
        
        if next_word == "Not available in db":
            response = {
                "result": (
                    "Word not present in database. "
                    "Please enter that 5-letter word."
                ),
                "next_word": None,
                "all_green": False,
                "show_user_input": True,
            }
        else:
            response = {
                "result": "Check above guess",
                "next_word": next_word,
                "all_green": False,
                "show_user_input": False,
            }
        return jsonify(response)

    # Exceeded maximum attempts without finding the word.
    response = {
        "result": (
            "Word not present in database.\n"
            "Please enter that 5-letter word."
        ),
        "next_word": None,
        "all_green": False,
        "show_user_input": True,
    }

    return jsonify(response)



import requests  # add this at the top with other imports

@app.route("/submit_user_word", methods=["POST"])
def submit_user_word():
    data = request.get_json()
    user_word: str = data.get("word", "").strip().lower()

    if len(user_word) != 5:
        return jsonify({"success": False, "message": "Word must be 5 letters long."})

    # ── Dictionary check ──────────────────────────────────────────────────
    try:
        dict_response = requests.get(
            f"https://api.dictionaryapi.dev/api/v2/entries/en/{user_word}",
            timeout=5
        )
        if dict_response.status_code == 404:
            return jsonify({
                "success": False,
                "message": f'"{user_word.upper()}" is not a valid English word.'
            })
    except requests.RequestException:
        # If the API is unreachable, fail safely and warn the user.
        return jsonify({
            "success": False,
            "message": "Could not verify word — please check your internet connection."
        })
    # ─────────────────────────────────────────────────────────────────────

    try:
        with open("words.txt", "r") as file:
            existing_words = file.read().splitlines()

        if user_word in existing_words:
            return jsonify({"success": False, "message": "Word already present in database."})

        with open("words.txt", "a") as file:
            file.write(user_word + "\n")

        return jsonify({"success": True})

    except OSError as exc:
        return jsonify({"success": False, "message": str(exc)})

@app.route("/reset", methods=["POST"])
def reset():
    """Reset all solver state and return the first seed word."""
    _reset_state()
    return jsonify({"first_word": INITIAL_GUESSES[0]})

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)