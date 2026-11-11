
vowels ="əʊaiɪeɛuʊɔæɒᵊ"

def vowel_vector(syl_part,type="N"):
    if type == "N":
        return None
    elif type == "I":
        return vowel_identity(syl_part)
    elif type == "P":
        return vowel_place(syl_part)
    elif type == "M":
        return vowel_manner(syl_part)
    else:
        raise ValueError("Invalid type. Must be 'N', 'I', 'P', or 'M'.")

def vowel_identity(vowel):
    encoding = [0] * len(vowels)

    for i in range(len(vowels)):
        if vowel == vowels[i]:
            encoding[i] = 1

    return encoding
    

def vowel_place(vowel):
    encoding = [0, 0, 0]  # vowels can be front, central, or back

    front = "iɪeɛæ"
    central = "ə"
    back = "uʊɔɒ"

    place_list = [front, central, back]

    for i in range(len(place_list)):
        if vowel in place_list[i]:
            encoding[i] = 1

    return encoding

def vowel_manner(vowel):
    encoding = [0, 0, 0, 0, 0, 0, 0] # vowels can beclose, near-close, close-mid, mid, open-mid, near-open, open

    close = "iu"
    near_close = "ɪʊ"
    close_mid = "eøo"
    mid = "ə"
    open_mid = "ɛɔ"
    near_open = "æ"
    open = "aɒ"

    manner_list = [close, near_close, close_mid, mid, open_mid, near_open, open]

    for i in range(len(manner_list)):
        if vowel in manner_list[i]:
            encoding[i] = 1

    return encoding

