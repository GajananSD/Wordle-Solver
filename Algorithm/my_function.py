"""
Function code
Input: Word to be guessed  
Output: Number of guesses required to guess word by functio
"""

import random
with open("../words.txt", 'r') as file:
    WORDS_LIST = [word.strip()[:5] for word in file]

# This function will update green, orange, gray according to new guess
def update_utils(green, orange, gray, guess, word):
    # gray_list update
    for letter in guess:
        if letter not in word:
            gray.add(letter)
    # green_dict update
    for i in range(5):
        if guess[i]==word[i]:
            green[i] = guess[i]
    # orange dict update
    for i in range(5):
        if guess[i] in word and guess[i]!=word[i]:
            if guess[i] not in orange:
                orange[guess[i]]=[i]
            else:
                orange[guess[i]].append(i)
    return (green, orange, gray)

# This function will decide whether word is satisfying condition to add in list
def choose_word(green, orange, gray, word):
    for letter in gray:
        if letter in word:
            return False
    for i in range(5):
        if green[i]=='' or green[i]==word[i]:
            continue
        else:
            return False
    for letter in orange:
        if letter not in word:
            return False
        not_pos = orange[letter]
        for i in range(5):
            if word[i]==letter:
                if i in not_pos:
                    return False
    return True

# Function will sort word list according to conditions of green, orange, gray
def word_sort(green, orange, gray, sorted_word_list):
    # Use sorted_word_list if available; otherwise, use the full word list
    if sorted_word_list:
        word_list = sorted_word_list
    else:
        word_list = WORDS_LIST
    # Filter words based on the constraints
    filtered_words = []
    for word in word_list:
        if choose_word(green, orange, gray, word):
            filtered_words.append(word)
    return filtered_words

    
# Main function
def main(initial_guess, word):
    green = ['']*5
    orange = {}
    gray = set()
    no_of_guess = 0
    sorted_word_list = []
    for guess in initial_guess:
        no_of_guess += 1
        if guess == word:
            return no_of_guess
        # Updating position
        green, orange, gray = update_utils(green, orange, gray, guess, word)
    # Now after giving initial guesses, we will choose from word.txt file
    sorted_word_list = word_sort(green, orange, gray, sorted_word_list)
    guess = random.choice(sorted_word_list)
    no_of_guess += 1
    while guess!=word:
        green, orange, gray = update_utils(green, orange, gray, guess, word)
        sorted_word_list = word_sort(green, orange, gray, sorted_word_list)
        guess = random.choice(sorted_word_list)
        no_of_guess += 1
    return no_of_guess
