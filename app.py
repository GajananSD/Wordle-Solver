from flask import Flask, render_template, request, jsonify
from word_sort import word_sorting

app = Flask(__name__)

# Set the word to be guessed (this can be dynamic or selected randomly)
Initial_guess = ["riots", "candy", "plume"]
current_word_index = 0  # Global index to keep track of the current word
sorted_list = []
# Dictionaries and list to store color information (persist across guesses)
green_dict = {}  # {letter: [positions]}
orange_dict = {}  # {letter: [positions]}
gray_list = []  # [letters]


@app.route('/')
def index():
    global current_word_index, green_dict, orange_dict, gray_list, sorted_list
    green_dict = {}
    orange_dict = {}
    gray_list = []
    sorted_list = []
    current_word_index = 0  # Reset the index when the page is loaded
    return render_template('index.html',
                           word=Initial_guess[current_word_index])


@app.route('/submit_guess', methods=['POST'])
def submit_guess():
    global current_word_index, green_dict, orange_dict, gray_list, sorted_list
    data = request.get_json()
    guessed_word = data.get('word')
    guessed_colors = data.get('colors')
    # Process the guessed colors
    for index, color in enumerate(guessed_colors):
        letter = guessed_word[index].lower()
        if color == "green":
            if letter not in green_dict:
                green_dict[letter] = []
            if index not in green_dict[letter]:  # Avoid duplicate positions
                green_dict[letter].append(index)
        elif color == "orange":
            if letter not in orange_dict:
                orange_dict[letter] = []
            if index not in orange_dict[letter]:  # Avoid duplicate positions
                orange_dict[letter].append(index)
        elif color == "grey":
            if letter not in gray_list:
                gray_list.append(letter)

    # Check if all blocks are green
    all_green = all(color == "green" for color in guessed_colors)
    # Move to the next word or end the game
    if all_green:
        response = {
            "result": " Guessed the correct word!!! ",
            "next_word": None,
            "all_green": True,
            "show_user_input": False
        }
    else:
        current_word_index += 1
        if current_word_index < len(Initial_guess):
            next_word = Initial_guess[current_word_index]
            response = {
                "result": "Check above guess",
                "next_word": next_word,
                "all_green": False,
                "show_user_input": False
            }
        elif current_word_index <= 5:
            next_word, sorted_list = word_sorting(gray_list, green_dict,
                                                  orange_dict, sorted_list)
            if next_word == 'Not available in db':
                response = {
                    "result":
                    "Word not present in Database. Please enter that 5-letter word.",
                    "next_word": None,
                    "all_green": False,
                    "show_user_input": True
                }
            else:
                response = {
                    "result": "Check above guess",
                    "next_word": next_word,
                    "all_green": False,
                    "show_user_input": False
                }
        else:
            response = {
                "result":
                "Word not present in Database\nPlease enter that 5-letter word.",
                "next_word": None,
                "all_green": False,
                "show_user_input": True
            }
    return jsonify(response)


@app.route('/submit_user_word', methods=['POST'])
def submit_user_word():
    data = request.get_json()
    user_word = data.get('word')
    # Check if the word is exactly 5 letters long
    if len(user_word) != 5:
        return jsonify({
            "success": False,
            "message": "Word must be 5 letters long."
        })
    # Check if the word is already in the file
    try:
        with open("words.txt", "r") as file:
            existing_words = file.read().splitlines()
        if user_word.lower() in existing_words:
            return jsonify({
                "success": False,
                "message": "Word present in database."
            })
        # If the word is not present, append it to the file
        with open("words.txt", "a") as file:
            file.write(user_word.lower() + "\n")

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
