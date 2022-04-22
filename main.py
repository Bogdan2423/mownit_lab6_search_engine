import os
from english_words import english_words_lower_set
from scipy import sparse

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


def make_matrix(library_dir, dictionary_list):
    matrix = sparse.dok_matrix((len(dictionary), len(os.listdir(library_dir))))
    dictionary_dict = dict()
    for index, word in enumerate(dictionary_list):
        dictionary_dict[word] = index

    for file_num, filename in enumerate(os.listdir(library_dir)):
        print(file_num)
        with open(library_dir + "/" + filename, 'r', encoding="latin-1") as f:
            wordlist = f.read().split()
            for word in wordlist:
                stripped_word = word.strip(".,!?\"'-:;()[]{} ").lower()
                if stripped_word in dictionary_dict.keys():
                    matrix[dictionary_dict[stripped_word], file_num] += 1

    sparse.save_npz("matrix", matrix.tocsc(), False)


#make_dictionary(library_dir)
dictionary = read_dictionary()
#make_matrix(library_dir, dictionary)
