import os
from english_words import english_words_lower_set
from scipy import sparse
from scipy.sparse.linalg import norm
import numpy as np
import math
import tkinter as tk
import pickle

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


def format_matrix(matrix, idf, path):
    row_list = []
    for i in range(len(idf)):
        row = matrix.getrow(i)
        row = row.multiply(idf[i])
        row_list.append(row)

    new_matrix = sparse.vstack(row_list)

    print("Saving formatted matrix...")
    sparse.save_npz(path, new_matrix, False)


def normalise_and_save(matrix, path):
    col_list = []
    for i in range(matrix.shape[1]):
        col = matrix.getcol(i)
        if norm(col) != 0:
            col = col.multiply(1.0 / norm(col))
        col_list.append(col)

    matrix = sparse.hstack(col_list)
    print("saving matrix " + path)
    sparse.save_npz(path, matrix, False)


def get_q_vector(input, dictionary):
    q = sparse.dok_matrix((1, len(dictionary)))
    input_list = input.split()
    input_list = [word.strip().lower() for word in input_list]
    for word in input_list:
        if word in dictionary:
            q[0, dictionary.index(word)] += 1

    q = q.multiply(1.0 / norm(q))
    return q


def low_rank_approx(matrix, k, filename):
    U, E, VT = sparse.linalg.svds(matrix, k=k)
    svd_matrix = sparse.csc_matrix(matrix.shape)
    sparseU = sparse.csc_matrix(U)
    sparseE = sparse.csc_matrix(E)
    sparseVT = sparse.csc_matrix(VT)

    for i in range(k):
        print(i)
        svd_matrix += sparseE[0, i] * sparseU.getcol(i) @ sparseVT.getrow(i)
        if (i+1) % 15 == 0:
            normalise_and_save(svd_matrix, filename + str(k))


def process_input(input, dictionary, matrix, n, library_dir):
    q = get_q_vector(input, dictionary)
    matrix = q.transpose().multiply(matrix)
    col_list = []
    for i in range(len(os.listdir(library_dir))):
        col = matrix.getcol(i)
        col_list.append(norm(col))

    return np.argpartition(col_list, n * (-1))[n * (-1):]


def make_title_list(library_dir):
    with open('title_list', 'wb') as f:
        pickle.dump(os.listdir(library_dir), f)


def read_title_list():
    with open('title_list', 'rb') as f:
        list = pickle.load(f)
    return list


dictionary = read_dictionary()

# matrix: macierz wyjściowa
# idf_matrix: macierz z uwzględnionym IDF
# formatted_matrix: macierz z uwzględnionym IDF i znormalizowana
# svd_matrix[k]: macierz svd dla k=k

matrix=read_matrix("idf_matrix.npz")
normalise_and_save(matrix, "formatted_matrix")

svd_matrix = read_matrix("svd_matrix60.npz")
sparse.save_npz("compressed_svd60", svd_matrix, True)

title_list = read_title_list()

root = tk.Tk()

canvas1 = tk.Canvas(root, width=300, height=350)
canvas1.pack()

label1 = tk.Label(root, text='Enter the phrase to search:')
canvas1.create_window(150, 60, window=label1)

entry1 = tk.Entry(root, width=50)
canvas1.create_window(150, 100, window=entry1)


def get_results():
    global title_list
    input = entry1.get()

    best_matches = process_input(input, dictionary, svd_matrix, 5, library_dir)

    label3 = tk.Label(root, text='Most matching results:', font=('helvetica', 10))
    canvas1.create_window(150, 170, window=label3)

    label4 = tk.Label(root, text=title_list[best_matches[0]][:-4], font=('helvetica', 10, 'bold'))
    label5 = tk.Label(root, text=title_list[best_matches[1]][:-4], font=('helvetica', 10, 'bold'))
    label6 = tk.Label(root, text=title_list[best_matches[2]][:-4], font=('helvetica', 10, 'bold'))
    label7 = tk.Label(root, text=title_list[best_matches[3]][:-4], font=('helvetica', 10, 'bold'))
    label8 = tk.Label(root, text=title_list[best_matches[4]][:-4], font=('helvetica', 10, 'bold'))
    canvas1.create_window(150, 200, window=label4)
    canvas1.create_window(150, 230, window=label5)
    canvas1.create_window(150, 260, window=label6)
    canvas1.create_window(150, 290, window=label7)
    canvas1.create_window(150, 320, window=label8)


button1 = tk.Button(text='Search', command=get_results)
canvas1.create_window(200, 140, window=button1)

root.mainloop()