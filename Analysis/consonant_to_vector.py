def manner_vector(syl_part):
    encoding = [0,0,0,0,0]

    plosives = "pbtdkg"
    nasals = "mnŋ"
    fricatives = "fvθðh"
    affricates = "ʤʧ"
    approximants = "wjlɹ"

    manner_list = [plosives, nasals, fricatives, affricates, approximants]

    for i in range(len(manner_list)):
        for j in range(len(syl_part)):
            if syl_part[j] in manner_list[i]:
                encoding[i] = 1

    return encoding


def place_vector(syl_part):

    encoding = [0,0,0,0,0,0,0,0,0]

    bilabial = "mp"
    labiodental = "bf"
    dental = "td"
    alveolar = "szʤ"
    palatal = "tʃdʒ"
    velar = "kɡ"
    uvular = "qɢ"
    pharyngeal = "ħʕ"
    glottal = "hʔ"

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

print(place_vector("ʤ"))
print(manner_vector("ʤ"))
print(cluster_vector("ʤ"))