import os
from english_words import english_words_lower_set
from scipy import sparse
from scipy.sparse.linalg import norm
import numpy as np
import math

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

    print("Saving matrix...")
    sparse.save_npz("matrix", matrix.tocsc(), False)


def read_matrix(dir):
    return sparse.load_npz(dir)


def calc_idf(dictionary, library_dir, matrix):
    N = len(os.listdir(library_dir))
    idf = [0 for _ in range(len(dictionary))]
    for i in range(len(idf)):
        nw = matrix.getrow(i).count_nonzero()
        if nw > 0:
            idf[i] = math.log(float(N) / nw)

    return idf


def format_matrix(matrix, idf, library_dir):
    row_list = []
    for i in range(len(idf)):
        row = matrix.getrow(i)
        row = row.multiply(idf[i])
        row_list.append(row)

    new_matrix = sparse.vstack(row_list)

    col_list = []
    for i in range(len(os.listdir(library_dir))):
        col = new_matrix.getcol(i)
        col = col.multiply(1.0/norm(col))
        col_list.append(col)

    new_matrix = sparse.hstack(col_list)
    print(new_matrix.shape)
    print("Saving formatted matrix...")
    sparse.save_npz("new_matrix", new_matrix, False)


def get_q_vector(input, dictionary):
    q = sparse.dok_matrix((1,len(dictionary)))
    input_list = input.split()
    input_list = [word.strip().lower() for word in input_list]
    for word in input_list:
        if word in dictionary:
            q[0, dictionary.index(word)] += 1

    q = q.multiply(1.0/norm(q))
    return q


dictionary = read_dictionary()
matrix = read_matrix("new_matrix.npz")
q = get_q_vector("most popular song", dictionary)
matrix = q.transpose().multiply(matrix)
col_list = []
for i in range(len(os.listdir(library_dir))):
    col = matrix.getcol(i)
    col_list.append(norm(col))
title_list=os.listdir(library_dir)
print(title_list[np.argmax(col_list)])