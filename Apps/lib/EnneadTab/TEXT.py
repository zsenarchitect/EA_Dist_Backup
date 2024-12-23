import ENVIRONMENT

import sys
sys.path.append(ENVIRONMENT.DEPENDENCY_FOLDER)

from termcolor import colored # pyright: ignore
from COLOR import TextColorEnum


def fuzzy_search(keyword, words):
    """Search from a list of words, return the best likely match, there could be case insensitive, and wrong spelling"""
    
    def levenshtein_distance(s1, s2):
        """Calculate the Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    # Error handling
    if not isinstance(keyword, str):
        raise ValueError("Keyword must be a string.")
    if not isinstance(words, list) or not all(isinstance(word, str) for word in words):
        raise ValueError("Words must be a list of strings.")
    if not keyword:
        raise ValueError("Keyword cannot be empty.")
    if not words:
        raise ValueError("Words list cannot be empty.")

    try:
        # keyword = keyword.lower()
        # words = [word.lower() for word in words]

        best_match = None
        lowest_distance = float('inf')

        for word in words:
            if word == keyword:
                return word  # Early exit for perfect match

            distance = levenshtein_distance(keyword, word)
            if distance < lowest_distance:
                lowest_distance = distance
                best_match = word

        return best_match
    except Exception as e:
        print("An error occurred: {}".format(e))
        return None

def colored_text(text, color = TextColorEnum.Cyan, on_color=None, attrs=None):
    """Colorize text.

    Available text colors:
        red, green, yellow, blue, magenta, cyan, white.

    Available text highlights:
        on_red, on_green, on_yellow, on_blue, on_magenta, on_cyan, on_white.

    Available attributes:
        bold, dark, underline, blink, reverse, concealed.

    Example:
        colored('Hello, World!', 'red', 'on_grey', ['blue', 'blink'])
        colored('Hello, World!', 'green')
    """

    
    if "colored" not in globals():
        # in some terminal run, it cannot read the dependecy folder so cannot load the colored moudle
        return text
    return colored(text, color, on_color, attrs)



def unit_test():
    print (colored_text("Test dfault color text"))
    print (colored_text("test green", TextColorEnum.Green))#, attrs=[TextColorEnum.Blue, 'blink']))

    test_searchs = ["CLINICAL SUPPORT", "EMERGENCY DEPARTMENT"]
    pool = ["D -CLINICAL SUPPORT", "C -INPATIENT CARE", "A - EMERGENCY DEPARTMENT"]
    for word in test_searchs:
        print ("Searching : [{}] in {} find [{}]".format(word, pool, fuzzy_search(word, pool)))


if __name__ == "__main__":
    unit_test()