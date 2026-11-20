import numpy as np

import util
import syllable_to_vector as sv
import pandas as pd

def vector_distance(vector1, vector2):
    return np.linalg.norm(np.array(vector1) - np.array(vector2))


def distances_matrix(vectors):
    n = len(vectors)
    distance_matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            distance_matrix[i][j] = vector_distance(vectors[i], vectors[j])
    
    return distance_matrix

def model_syllable(syllable_pair, models_list = ["P_N_N","M_N_N","I_N_N","N_P_N","N_M_N","N_I_N","N_N_P","N_N_M","N_N_I","C_N_N","N_N_C"]):
    distances_list = []
    for i in range(len(models_list)):
        distances_list.append(vector_distance(
            sv.syllable_vector(syllable_pair[0],models_list[i]),
            sv.syllable_vector(syllable_pair[1],models_list[i]))
            )

    return distances_list

def make_predictions(pairs_list):

    model_predictions = []

    for pair in pairs_list:

        model_predictions.append(model_syllable(pair))

    return model_predictions

def experiment_metric(predictions_matrix):

    return np.corrcoef(np.transpose(predictions_matrix))

if __name__== "__main__":
    experiment_metric(make_predictions([('frɛndz', 'aʊt'),
 ('frɛndz', 'tə'),
 ('frɛndz', 'paɪ'),
 ('frɛndz', 'pə'),
 ('frɛndz', 'ɒv'),
 ('frɛndz', 'pɪk'),
 ('frɛndz', 'pəz'),
 ('frɛndz', 'pə'),
 ('frɛndz', 'wɛt'),
 ('frɛndz', 'bɛt'),
 ('frɛndz', 'ᵊri'),
 ('frɛndz', 'ri'),
 ('frɛndz', 'mæ'),
 ('θivz', 'mʌʧ'),
 ('θivz', 'kʊd'),
 ('θivz', 'prɒ'),
 ('ɡraʊnd', 'ðə'),
 ('ɡraʊnd', 'θɜ'),
 ('ɡraʊnd', 'ti'),
 ('ɡraʊnd', 'ðæt'),
 ('ɡraʊnd', 'θɜz'),
 ('ɡraʊnd', 'pi'),
 ('ɡraʊnd', 'tə'),
 ('ɡraʊnd', 'paɪ'),
 ('ɡraʊnd', 'pə'),
 ('ɡraʊnd', 'pɪk'),
 ('ɡraʊnd', 'pɛ'),
 ('ɡraʊnd', 'pəz'),
 ('ɡraʊnd', 'kɒ'),
 ('ɡraʊnd', 'fi'),
 ('ɡraʊnd', 'sə'),
 ('ɡraʊnd', 'lɛ'),
 ('ɡraʊnd', 'ðə'),
 ('ɡraʊnd', 'nɛ'),
 ('ɡraʊnd', 'və'),
 ('ɡraʊnd', 'wɛ'),
 ('ɡraʊnd', 'wɛt'),
 ('ɡraʊnd', 'bɛt'),
 ('ɡraʊnd', 'ʤɪn'),
 ('ɡraʊnd', 'ᵊri'),
 ('ɡraʊnd', 'næ'),
 ('ɡraʊnd', 'ri'),
 ('haʊ', 'ʧʌk'),
 ('haʊ', 'pɛk'),
 ('haʊ', 'və'),
 ('haʊ', 'wɛ'),
 ('mʌʧ', 'θivz'),
 ('mʌʧ', 'θrəʊn'),
 ('mʌʧ', 'tə'),
 ('wʊd', 'θrəʊn'),
 ('ʧʌk', 'haʊ'),
 ('ʧʌk', 'θrɪld'),
 ('ʧʌk', 'θrəʊn'),
 ('ʧʌk', 'deɪ'),
 ('ʧʌk', 'prɒ'),
 ('kʊd', 'θivz'),
 ('kʊd', 'θri'),
 ('kʊd', 'ðəd'),
 ('ðə', 'ɡraʊnd'),
 ('θɜ', 'ɡraʊnd'),
 ('ti', 'ɡraʊnd'),
 ('θri', 'kʊd'),
 ('θɔt', 'deɪ'),
 ('ðæt', 'ɡraʊnd'),
 ('ðæt', 'prɒ'),
 ('θrɪld', 'ʧʌk'),
 ('θrɪld', 'tə'),
 ('θrɪld', 'paɪ'),
 ('θrɪld', 'pə'),
 ('θrɪld', 'pɛk'),
 ('θrɪld', 'pəz'),
 ('θrɪld', 'pə'),
 ('θrɪld', 'ᵊri'),
 ('θrəʊn', 'mʌʧ'),
 ('θrəʊn', 'wʊd'),
 ('θrəʊn', 'ʧʌk'),
 ('θrəʊn', 'və'),
 ('θru', 'pɪkt'),
 ('θru', 'pɛk'),
 ('θru', 'pɪk'),
 ('θru', 'wɛ'),
 ('aʊt', 'frɛndz'),
 ('θɜz', 'ɡraʊnd'),
 ('deɪ', 'ʧʌk'),
 ('deɪ', 'θɔt'),
 ('deɪ', 'wɛt'),
 ('pi', 'ɡraʊnd'),
 ('tə', 'frɛndz'),
 ('tə', 'ɡraʊnd'),
 ('tə', 'θrɪld'),
 ('paɪ', 'frɛndz'),
 ('paɪ', 'ɡraʊnd'),
 ('paɪ', 'θrɪld'),
 ('pə', 'frɛndz'),
 ('pə', 'ɡraʊnd'),
 ('pə', 'θrɪld'),
 ('pɪkt', 'θru'),
 ('pɪkt', 'ɒv'),
 ('pɪkt', 'mæ'),
 ('pɛk', 'haʊ'),
 ('pɛk', 'θrɪld'),
 ('pɛk', 'θru'),
 ('pɛk', 'ᵊld'),
 ('ɒv', 'frɛndz'),
 ('ɒv', 'pɪkt'),
 ('ᵊld', 'pɛk'),
 ('ᵊld', 'pɪk'),
 ('ᵊld', 'bɛt'),
 ('ᵊld', 'ri'),
 ('pɪk', 'frɛndz'),
 ('pɪk', 'ɡraʊnd'),
 ('pɪk', 'θru'),
 ('pɪk', 'ᵊld'),
 ('pɛ', 'ɡraʊnd'),
 ('pəz', 'frɛndz'),
 ('pəz', 'ɡraʊnd'),
 ('pəz', 'θrɪld'),
 ('prɒ', 'θivz'),
 ('prɒ', 'ʧʌk'),
 ('prɒ', 'ðæt'),
 ('prɒ', 'və'),
 ('prɒ', 'wɛt'),
 ('pə', 'frɛndz'),
 ('pə', 'θrɪld'),
 ('kɒ', 'ɡraʊnd'),
 ('fi', 'ɡraʊnd'),
 ('sə', 'ɡraʊnd'),
 ('lɛ', 'ɡraʊnd'),
 ('ðə', 'ɡraʊnd'),
 ('nɛ', 'ɡraʊnd'),
 ('və', 'ɡraʊnd'),
 ('və', 'haʊ'),
 ('və', 'θrəʊn'),
 ('və', 'prɒ'),
 ('wɛ', 'ɡraʊnd'),
 ('wɛ', 'haʊ'),
 ('wɛ', 'θru'),
 ('wɛt', 'frɛndz'),
 ('wɛt', 'ɡraʊnd'),
 ('wɛt', 'deɪ'),
 ('wɛt', 'prɒ'),
 ('tə', 'mʌʧ'),
 ('bɛt', 'frɛndz'),
 ('bɛt', 'ɡraʊnd'),
 ('bɛt', 'ᵊld'),
 ('ðəd', 'kʊd'),
 ('ʤɪn', 'ɡraʊnd'),
 ('ᵊri', 'frɛndz'),
 ('ᵊri', 'ɡraʊnd'),
 ('ᵊri', 'θrɪld'),
 ('næ', 'ɡraʊnd'),
 ('ri', 'frɛndz'),
 ('ri', 'ɡraʊnd'),
 ('ri', 'ᵊld'),
 ('mæ', 'frɛndz'),
 ('mæ', 'pɪkt')]))
