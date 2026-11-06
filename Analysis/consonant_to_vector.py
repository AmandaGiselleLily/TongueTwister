def manner_vector(thingy):
    encoding = [0,0,0,0,0]

    plosives = "pbtdkg"
    nasals = "mnŋ"
    fricatives = "fvθðh"
    affricates = "ʤʧ"
    approximants = "wjlɹ"

    manner_list = [plosives, nasals, fricatives, affricates, approximants]

    for i in range(len(manner_list)):
        if thingy in manner_list[i]:
            encoding[i] = 1

    return encoding


def place_vector(thingy):

    encoding = [0,0,0,0,0,0,0,0,0]

    bilabial = "mp"
    labiodental = "bf"
    dental = "td"
    alveolar = "sz"
    palatal = "tʃdʒ"
    velar = "kɡ"
    uvular = "qɢ"
    pharyngeal = "ħʕ"
    glottal = "hʔ"

    place_list = [bilabial, labiodental, dental, alveolar, palatal, velar, uvular, pharyngeal, glottal]

    for i in range(len(place_list)):
        if thingy in place_list[i]:
            encoding[i] = 1

    return encoding