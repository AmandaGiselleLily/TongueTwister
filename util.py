def split_syllable(string):
    vowels = "əʊaiɪeɛuʊɔæɒᵊʌɜ"
    nucleus = ""
                
    for char in vowels:
        if string.find(char) != -1:
            nucleus = char
            break
        
    onset = string.split(nucleus)[0]
    coda = string.split(nucleus)[1]

    return onset, nucleus, coda

if __name__ == "__main__":
    o,n,c = split_syllable("plænt")
    print(o,n,c)
    split_syllable("θivz")
    split_syllable("ʤɪŋk")
