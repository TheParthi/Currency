convert_word_to_tamil = {
    "and": "matrum",
    "one": "oru",
    "two": "irandu",
    "three": "moondru",
    "four": "naangu",
    "five": "iynthu",
    "six": "aaru",
    "seven": "yealu",
    "eight": "ettu",
    "nine": "onbathu",
    "10Rupees": "pathu roobai",
    "20Rupees": "irubathu roobai",
    "50Rupees": "aimbathu roobai",
    "100Rupees": "nooru roobai",
    "200Rupees": "irunooru roobai",
    "500Rupees": "ainooru roobai",
    "Notes": "thaalgal",
    "Note": "thaal",
}

def convert_to_tamil(text):
    if text == "Reload the page and try with another better image" or text == "" or text.lower().strip() == "image contains":
        return "Sariyana padathai kaatavum"
    else:
        wordArr = list(text.split(' '))
        res = "ithil "
        for word in wordArr:
            if word in convert_word_to_tamil:
                res += convert_word_to_tamil[word] + " "
        res += "ullathu"
        
    return res
