from collections import Counter
import string

english_frequencies = 'ETAOINSHRDLCUMWFGYPBVKJXQZ'

cipher_text = input("Enter the encrypted text: ")

cipher_counts = Counter(char.upper() for char in cipher_text if char.isalpha())

sorted_cipher = ''.join([item[0] for item in cipher_counts.most_common()])

mapping = {}
for i, letter in enumerate(sorted_cipher):
    if i < len(english_frequencies):
        mapping[letter] = english_frequencies[i]
    else:
        mapping[letter] = letter

mapping['G'] = 'H'
mapping['K'] = 'O'
mapping['I'] = 'I'
mapping['Q'] = 'N'
mapping['Z'] = 'S'
mapping['J'] = 'X'
mapping['A'] = 'D'
mapping['X'] = 'C'
mapping['M'] = 'R'
mapping['O'] = 'M'
mapping['N'] = 'L'
mapping['F'] = 'F'
mapping['B'] = 'Y'
mapping['S'] = 'P'
mapping['Y'] = 'U'
mapping['W'] = 'Q'


decrypted_text = []
for char in cipher_text:
    if char.isalpha():
        if char.isupper():
            decrypted_text.append(mapping.get(char, char))
        else:
            decrypted_text.append(mapping.get(char.upper(), char).lower())
    else:
        decrypted_text.append(char)
decrypted_text = ''.join(decrypted_text)


print("Mapping used:")
for key in sorted(mapping.keys()):
    print(key, "=", mapping[key])

print("\nDecrypted text:")
print(decrypted_text)
