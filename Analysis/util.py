def split_syllable(string):
    vowels = "əʊaiɪeɛuʊɔæɒᵊ"
    nucleus = -1
        
    clusters1 = {"onset": False, "coda": False}
        
    
    for char in vowels:
        if string.find(char) != -1:
            nucleus1 = char
            break
        
    
    return string.split(nucleus)
        