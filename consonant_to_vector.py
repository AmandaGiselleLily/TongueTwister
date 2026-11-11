plosives = "pbtdkg"
nasals = "mnŋ"
fricatives = "fvθðh"
affricates = "ʤʧ"
approximants = "wjlɹ"

bilabial = "mp"
labiodental = "bf"
dental = "td"
alveolar = "szʤ"
palatal = "tʃdʒ"
velar = "kɡ"
uvular = "qɢ"
pharyngeal = "ħʕ"
glottal = "hʔ"

def consonant_vector(syl_part,type="N"):
    if type == "N":
        return None
    elif type == "M":
        return manner_vector(syl_part)
    elif type == "P":
        return place_vector(syl_part)
    elif type == "C":
        return cluster_vector(syl_part)
    else:
        raise ValueError("Invalid type. Must be 'N', 'M', 'P', or 'C'.")
def manner_vector(syl_part):
    encoding = [0,0,0,0,0]

    manner_list = [plosives, nasals, fricatives, affricates, approximants]

    for i in range(len(manner_list)):
        for j in range(len(syl_part)):
            if syl_part[j] in manner_list[i]:
                encoding[i] = 1

    return encoding


def place_vector(syl_part):

    encoding = [0,0,0,0,0,0,0,0,0]


    place_list = [bilabial, labiodental, dental, alveolar, palatal, velar, uvular, pharyngeal, glottal]

    for i in range(len(place_list)):
        for j in range(len(syl_part)):
            if syl_part[j] in place_list[i]:
                encoding[i] = 1

    return encoding

def cluster_vector(syl_part):
    encoding = [0,0]

    if len(syl_part) > 1:
        encoding[1] = 1
    else:
        encoding[0] = 1

    return encoding

if __name__ == "__main__":
    print(manner_vector("ʤ"))
    print(place_vector("ʤ"))
    print(cluster_vector("ʤ"))
