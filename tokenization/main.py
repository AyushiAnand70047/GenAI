import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")

text = "Hey There! My name is Ayushi Anand"
tokens = enc.encode(text)

print("Tokens: ", tokens)

decoded = enc.decode([25216, 3274, 0, 3673, 1308, 382, 21918, 41074, 180895])

print("Decoded tokens: ", decoded)