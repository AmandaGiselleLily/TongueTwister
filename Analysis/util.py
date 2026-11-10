def split_syllable(string):
    vowels = "əʊaiɪeɛuʊɔæɒᵊ"
    nucleus = -1
        
    clusters1 = {"onset": False, "coda": False}
        
    
    for char in vowels:
        if string.find(char) != -1:
            nucleus = char
            break
        
    print(f"Onset and Coda: {string.split(nucleus)}")

    return string.split(nucleus)


split_syllable("plænt")
split_syllable("θivz")
split_syllable("ʤɪŋk")
