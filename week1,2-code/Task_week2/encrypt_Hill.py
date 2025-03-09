import math
import numpy as np

def filter_key(key):
    return ''.join([c for c in key.lower() if c.isalpha()])

def generateKeyMatrix(key, n):
    if len(key) != n * n:
        raise ValueError("Độ dài khóa không phù hợp với kích thước ma trận {}x{}".format(n, n))
    matrix = []
    for i in range(n):
        row = []
        for j in range(n):
            row.append(ord(key[i * n + j]) - ord('a'))
        matrix.append(row)
    matrix = np.array(matrix)

    if int(round(np.linalg.det(matrix))) == 0:
        raise ValueError("Invalid Key! Ma trận khóa không khả nghịch.")
    return matrix

def multiplyMatrixVector(matrix, vector):
    num_vector = np.array([[ord(c) - ord('a')] for c in vector])
    result = np.dot(matrix, num_vector) % 26
    return ''.join(chr(int(num) + ord('a')) for num in result.flatten())

def hillEncrypt(plaintext, keyMatrix):
    n = keyMatrix.shape[0]
    plaintext = ''.join(plaintext.lower().split())
    if len(plaintext) % n != 0:
        plaintext += 'x' * (n - (len(plaintext) % n))
    ciphertext = ""
    for i in range(0, len(plaintext), n):
        block = plaintext[i:i+n]
        ciphertext += multiplyMatrixVector(keyMatrix, block)
    return ciphertext

if __name__ == "__main__":
    raw_key = input("Nhập khóa: ")
    key = filter_key(raw_key)
    
    key_length = len(key)
    n = int(math.sqrt(key_length))
    if n * n != key_length:
        raise ValueError("Độ dài khóa (sau khi lọc) phải là số chính phương, ví dụ 4, 9, 16, ...")
    
    encryptMatrix = generateKeyMatrix(key, n)
    print("Ma trận khóa mã hóa ({}x{}):".format(n, n))
    print(encryptMatrix)
    
    plaintext = input("Nhập PlainText: ")
    ciphertext = hillEncrypt(plaintext, encryptMatrix)
    print("CipherText:", ciphertext)
