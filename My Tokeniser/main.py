import my_tokeniser

text = input("Enter text to encode: ")
encoded_text = my_tokeniser.encode(text)
print("Encoded text: ",encoded_text)

token_input = input("Enter token to decode: ")
token = [int(t.strip()) for t in token_input.split(',')]
decoded_token = my_tokeniser.decode(token)
print("Decoded token: ", decoded_token)