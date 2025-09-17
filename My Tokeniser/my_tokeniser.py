def encode(text):
    tokens = [ord(t) for t in text]
    return tokens

def decode(tokens):
    text = "".join([chr(token) for token in tokens])
    return text