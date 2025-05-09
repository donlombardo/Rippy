""" Functions used in the Rippy """

import os
import shutil
import sys
import re
from collections import Counter
from textwrap import wrap as wp


# Gives a better look to the print
def spaced_print(text):
    print('\n'.join(wp(text)) + "\n")


# Special input function
def special_input(text):
    return input('\n'.join(wp(text)) + " ")

def capitalize_word(word, is_previous_all_caps):
    # If the word contains any digits, skip capitalization
    if any(char.isdigit() for char in word):
        return word

    # If the word is all uppercase (e.g., acronym) and the previous word wasn't all caps, keep as-is
    if word.isupper() and not is_previous_all_caps:
        return word

    # Handle hyphenated words (e.g., sci-fi) by capitalizing each part individually
    if "-" in word:
        parts = word.split("-")
        capitalized_parts = [capitalize_word(part, False) for part in parts]
        return "-".join(capitalized_parts)

    # Capitalize the first alphabetic character A-Ö after any non-letter prefix
    match = re.match(r'^([^A-Za-zÅÄÖåäö]*)([A-Za-zÅÄÖåäö])(.*)', word)
    if match:
        prefix, first_letter, rest = match.groups()
        return prefix + first_letter.upper() + rest.lower()

    # Fallback
    return word.capitalize()


# Changes apostrophes and capitalization
def character_change(text, CAPITALIZE_BOOL, APOSTROPHE_BOOL):
    if CAPITALIZE_BOOL:
        words = text.split(" ")
        result = []
        was_previous_all_caps = False  # To check if the previous word was fully uppercase
        
        for word in words:
            # Check if the word is completely uppercase
            is_all_caps = word.isupper()
            # Apply capitalization rules
            capitalized_word = capitalize_word(word, was_previous_all_caps)
            result.append(capitalized_word)
            # Update flag for next word
            was_previous_all_caps = is_all_caps

        # Join the words back into a sentence
        text = ' '.join(result)
    if APOSTROPHE_BOOL:
        text = text.replace("`", "'").replace("´", "'")
    return text


# Make temp files unharmful
def placeholding(word):
    word = word.replace("'", "apostrophe_placeholder").replace('"', "citation_placeholder")
    return word


def reverse_placeholding(word):
    word = word.replace("apostrophe_placeholder", "'").replace("citation_placeholder", '"')
    return word


# Remove excessive space
def remove_excessive_space(word):
    while "  " in word:
        word = word.replace("  ", " ")
    return word



# Checks for internet connection, needed to find Discogs or MusicBrainz information
def check_internet_httplib(url="www.github.com", timeout=5):
    import http.client as httplib
    connection = httplib.HTTPConnection(url, timeout=timeout)
    try:
        connection.request("HEAD", "/")
        connection.close()
        return True
    except Exception as e:
        return False



