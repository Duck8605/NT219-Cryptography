import string

def mod_inverse(a, m):
    """
    Computes the modular inverse of a modulo m using a simple brute-force approach.
    Returns the inverse if it exists, else None.
    """
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None


def affine_decrypt(text, a, b):
    """
    Decrypts the input text using the Affine cipher with keys a and b.
    Computes the modular inverse of a and applies the decryption formula:
      D(y) = a_inv * (y - b) mod 26.
    """
    a_inv = mod_inverse(a, 26)
    if a_inv is None:
        return None
    
    alphabets = string.ascii_uppercase
    result = []
    for char in text:
        if char.isupper():
            y = ord(char) - ord('A')
            x = (a_inv * (y - b)) % 26
            result.append(alphabets[x])
        elif char.islower():
            y = ord(char.upper()) - ord('A')
            x = (a_inv * (y - b)) % 26
            result.append(alphabets[x].lower())
        else:
            result.append(char)
    return ''.join(result)

def brute_force_affine_cipher(ciphertext):
    """
    Try all possible combinations of a and b for the Affine cipher and print the results.
    """
    for a in range(1, 26):
        if mod_inverse(a, 26) is not None: 
            for b in range(0, 26):
                decrypted_text = affine_decrypt(ciphertext, a, b)
                if decrypted_text:
                    print(f"Trying a = {a}, b = {b}")
                    print(f"Decrypted text: {decrypted_text}\n")
                input("\nPress Enter to continue to decryption...")

def main():
    ciphertext = input("Enter the encrypted text: ")
    brute_force_affine_cipher(ciphertext)

if __name__ == "__main__":
    main()