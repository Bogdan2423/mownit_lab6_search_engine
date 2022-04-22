import os
from english_words import english_words_lower_set

library_dir = "./wiki"


def make_dictionary(library_dir):
    word_set = set()
    for filename in os.listdir(library_dir):
        with open(library_dir + "/" + filename, 'r', encoding="latin-1") as f:
            wordlist = f.read().split()
            for word in wordlist:
                stripped_word = word.strip(".,!?\"'-:;()[]{} ").lower()
                if stripped_word in english_words_lower_set:
                    word_set.add(stripped_word)

    dict_file = open("dictionary.txt", 'w', encoding="latin-1")
    for word in word_set:
        dict_file.write(word + " ")
    dict_file.close()


def read_dictionary():
    dict_file = open("dictionary.txt", 'r', encoding="latin-1")
    word_list = dict_file.read().split()
    dict_file.close()
    return word_list


make_dictionary(library_dir)
di = read_dictionary()
print(di)
print(len(di))
