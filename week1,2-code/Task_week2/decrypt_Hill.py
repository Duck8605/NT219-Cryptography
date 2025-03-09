import math
import numpy as np
import sympy

def filter_key(key):
    return ''.join([c for c in key.lower() if c.isalpha()])

def modInverse(a, m):
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    raise ValueError("modInverse không tồn tại!")

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

def computeDecryptMatrix(keyMatrix):
    n = keyMatrix.shape[0]
    det = int(round(np.linalg.det(keyMatrix))) % 26
    if det == 0:
        raise ValueError("Determinant bằng 0, khóa không hợp lệ!")
    inv_det = modInverse(det, 26)
    
    sympy_matrix = sympy.Matrix(keyMatrix.tolist())
    adjugate = sympy_matrix.adjugate()
    inv_matrix = (inv_det * adjugate) % 26
    inv_matrix = np.array(inv_matrix).astype(np.int64)
    return inv_matrix

def multiplyMatrixVector(matrix, vector):
    num_vector = np.array([[ord(c) - ord('a')] for c in vector])
    result = np.dot(matrix, num_vector) % 26
    return ''.join(chr(int(num) + ord('a')) for num in result.flatten())

def hillDecrypt(ciphertext, decryptMatrix):
    n = decryptMatrix.shape[0]
    ciphertext = ''.join(ciphertext.lower().split())
    plaintext = ""
    for i in range(0, len(ciphertext), n):
        block = ciphertext[i:i+n]
        plaintext += multiplyMatrixVector(decryptMatrix, block)
    return plaintext

if __name__ == "__main__":
    raw_key = input("Nhập khóa: ")
    key = filter_key(raw_key)
    
    key_length = len(key)
    n = int(math.sqrt(key_length))
    if n * n != key_length:
        raise ValueError("Độ dài khóa (sau khi lọc) phải là số chính phương, ví dụ 4, 9, 16, ...")
    
    keyMatrix = generateKeyMatrix(key, n)
    print("Ma trận khóa mã hóa ({}x{}):".format(n, n))
    print(keyMatrix)
    
    decryptMatrix = computeDecryptMatrix(keyMatrix)
    print("Ma trận khóa giải mã ({}x{}):".format(n, n))
    print(decryptMatrix)
    
    ciphertext = input("Nhập CipherText: ")
    plaintext = hillDecrypt(ciphertext, decryptMatrix)
    print("PlainText:", plaintext)
