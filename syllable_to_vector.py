import util
import consonant_to_vector as cons
import vowel_to_vector as vow

# Models are notated onset_nucleus_coda, where each part is either P (place), M (manner), I(Identity), or N (none).
# e.g. Place for everything is P_P_P, manner for everything is M_M_M, place at start manner at end None in middle is P_N_M

def syllable_vector(syllable,model_name='P_P_P'):

    construct = util.split_syllable(syllable)
    vector_list = []

    if model_name == "special_sauce":
        pass

    else:
        comp = model_name.split("_") 

    for i in range(len(comp)):
        if i == 0 or i == 2:
            vector_list.append(cons.consonant_vector(construct[i],comp[i]))
        elif i == 1:
            vector_list.append(vow.vowel_vector(construct[i],comp[i]))

    return vector_list

if __name__ == "__main__":
    print(syllable_vector("cat"))