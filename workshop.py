"""
Name:
Student number:
Western username:
Date created:
File description: Replace this line with a description of this file.
"""

import os
from scramble import *


# Replace this comment with the purpose, parameters, and return value.
def count_letter_occurrences(text):
    pass


# Replace this comment with the purpose, parameters, and return value.
def display_letter_histogram(letter_counts):
    pass


# Provided function. Keep this code unchanged.
# Replace this comment with the purpose, parameters, and return value.
def get_menu_selection():
    while True:
        print("Cipher Workshop options:")
        print("1) Keyword Cipher")
        print("2) Vigenere Cipher")
        print("3) Frequency Analysis")
        print("4) Exit")
        selection_text = input("Input menu option (1 to 4): ").strip()
        if selection_text in ["1", "2", "3", "4"]:
            return int(selection_text)
        print("Invalid input!")


# Replace this comment with the purpose, parameters, and return value.
def main():
    pass


# This guard starts the program when this file is run directly, not when imported.
# Apart from imports and function definitions, keep code inside functions or this guard.
if __name__ == "__main__":
    main()
