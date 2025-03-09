import math
import numpy as np
import sympy

def modInverse(a, m):
    """Tìm số nghịch đảo của a modulo m, nếu tồn tại."""
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    raise ValueError("modInverse không tồn tại!")

def generateKeyMatrix(key, n):
    """
    Sinh ma trận khóa kích thước n x n từ chuỗi key.
    Key phải có độ dài bằng n^2.
    Các ký tự được chuyển thành số: 'a' -> 0, ..., 'z' -> 25.
    """
    if len(key) != n * n:
        raise ValueError("Độ dài khóa không phù hợp với kích thước ma trận {}x{}".format(n, n))
    Matrix = []
    for i in range(n):
        row = []
        for j in range(n):
            row.append(ord(key[i * n + j]) - ord('a'))
        Matrix.append(row)
    Matrix = np.array(Matrix)
    if int(round(np.linalg.det(Matrix))) == 0:
        raise ValueError("Invalid Key! Ma trận khóa không khả nghịch.")
    return Matrix

def computeDecryptMatrix(keyMatrix):
    """
    Tính ma trận khóa nghịch đảo theo modulo 26.
    Sử dụng sympy để tính ma trận phụ hợp và sau đó nhân với nghịch đảo của định thức modulo 26.
    """
    n = keyMatrix.shape[0]
    det = int(round(np.linalg.det(keyMatrix))) % 26
    if det == 0:
        raise ValueError("Determinant bằng 0, khóa không hợp lệ!")
    inv_det = modInverse(det, 26)
    
    # Sử dụng sympy để tính ma trận nghịch đảo
    sympy_matrix = sympy.Matrix(keyMatrix.tolist())
    # Ma trận phụ hợp: adjugate matrix
    adjugate = sympy_matrix.adjugate()
    # Tính ma trận nghịch đảo modulo 26: inv_key = inv_det * adjugate mod 26
    inv_matrix = (inv_det * adjugate) % 26
    
    # Chuyển về dạng numpy array kiểu int
    inv_matrix = np.array(inv_matrix).astype(np.int64)
    return inv_matrix

def multiplyMatrixVector(matrix, vector):
    """
    Nhân ma trận với vector (được biểu diễn dưới dạng danh sách các ký tự).
    Chuyển các ký tự sang số, nhân, sau đó lấy modulo 26 và chuyển lại thành ký tự.
    """
    n = matrix.shape[0]
    # Chuyển vector thành cột số
    num_vector = np.array([[ord(c) - ord('a')] for c in vector])
    result = np.dot(matrix, num_vector)
    # Lấy modulo 26
    result = result % 26
    # Chuyển số về ký tự
    return ''.join(chr(int(num) + ord('a')) for num in result.flatten())

def hillEncrypt(plaintext, keyMatrix):
    """
    Mã hóa theo Hill cipher:
      - Chia plaintext thành các khối có độ dài n.
      - Nếu độ dài không chia hết, thêm ký tự 'x' để đủ.
      - Với mỗi khối, nhân với ma trận khóa và chuyển kết quả thành chuỗi ký tự.
    """
    n = keyMatrix.shape[0]
    # Loại bỏ khoảng trắng và chuyển về chữ thường
    plaintext = ''.join(plaintext.lower().split())
    # Nếu độ dài không chia hết cho n, thêm 'x'
    if len(plaintext) % n != 0:
        plaintext += 'x' * (n - (len(plaintext) % n))
    ciphertext = ""
    for i in range(0, len(plaintext), n):
        block = plaintext[i:i+n]
        ciphertext += multiplyMatrixVector(keyMatrix, block)
    return ciphertext

def hillDecrypt(ciphertext, decryptMatrix):
    """
    Giải mã theo Hill cipher:
      - Chia ciphertext thành các khối có độ dài n.
      - Với mỗi khối, nhân với ma trận khóa nghịch đảo và chuyển kết quả thành chuỗi ký tự.
    """
    n = decryptMatrix.shape[0]
    ciphertext = ''.join(ciphertext.lower().split())
    plaintext = ""
    for i in range(0, len(ciphertext), n):
        block = ciphertext[i:i+n]
        plaintext += multiplyMatrixVector(decryptMatrix, block)
    return plaintext

if __name__ == "__main__":
    # Nhập khóa và xác định kích thước ma trận (2x2, 3x3, hoặc 4x4)
    key = ''.join(input("Nhập khóa (chỉ chữ cái, không dấu cách): ").lower().split())
    key_length = len(key)
    
    # Xác định kích thước ma trận: chỉ chấp nhận các số chính phương như 4, 9, 16
    n = int(math.sqrt(key_length))
    if n * n != key_length:
        raise ValueError("Độ dài khóa không phải là số chính phương, không thể tạo ma trận {}x{}".format(n, n))
    
    # Sinh ma trận mã hóa (Encrypt Matrix)
    encryptMatrix = generateKeyMatrix(key, n)
    print("Ma trận khóa mã hóa ({}x{}):".format(n, n))
    print(encryptMatrix)
    
    # Tính ma trận khóa giải mã (Decrypt Matrix)
    decryptMatrix = computeDecryptMatrix(encryptMatrix)
    print("Ma trận khóa giải mã ({}x{}) (Inverse mod 26):".format(n, n))
    print(decryptMatrix)
    
    # Lựa chọn chế độ mã hóa hoặc giải mã
    choice = input("Bạn muốn mã hóa (E) hay giải mã (D)? ").strip().upper()
    if choice == 'E':
        plaintext = input("Nhập PlainText (chỉ chữ cái, không khoảng trắng): ")
        ciphertext = hillEncrypt(plaintext, encryptMatrix)
        print("CipherText:", ciphertext)
    elif choice == 'D':
        ciphertext = input("Nhập CipherText (chỉ chữ cái, không khoảng trắng): ")
        plaintext = hillDecrypt(ciphertext, decryptMatrix)
        print("PlainText:", plaintext)
    else:
        print("Lựa chọn không hợp lệ!")
