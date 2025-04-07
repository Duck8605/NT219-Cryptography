import os
from .AES import AES

class modes:
    def __init__(self, key):
        key_length = len(key) * 8  # Convert key length to bits
        if key_length not in [128, 192, 256]:
            raise ValueError("Invalid key length. Supported lengths are 128, 192, and 256 bits.")
        self.aes = AES(key, key_length)  # an AES class that takes a key and key_length
        self.iv = os.urandom(16)
        # This can be set externally (e.g. from your main script):
        self.mode = None

    ############################################################################
    # HELPER METHODS
    ############################################################################

    def utf8_to_bytes(self, utf8_str):
        """Convert a UTF-8 string to bytes."""
        return utf8_str.encode('utf-8')

    def bytes_to_utf8(self, bytes_data):
        """Convert bytes to a UTF-8 string."""
        return bytes_data.decode('utf-8')

    def binary_to_bytes(self, binary_str):
        """
        Convert a binary string (e.g. '1010101...') to bytes.
        - We pad the bit string to a multiple of 8 bits by appending '1' + the needed '0's.
        """
        padding_length = 8 - (len(binary_str) % 8)
        # Append a '1' followed by the necessary '0's to reach a multiple of 8
        binary_str += '1' + '0' * (padding_length - 1)
        n = int(binary_str, 2)
        byte_length = len(binary_str) // 8
        return n.to_bytes(byte_length, 'big')

    def bytes_to_binary(self, bytes_data):
        """
        Convert bytes to a binary string (e.g. '0b101001...'), 
        removing any padding we added (searching for the last '1' bit).
        """
        binary_str = bin(int.from_bytes(bytes_data, 'big'))[2:]  # skip the '0b'
        # Find the last '1' (indicating where our padding started) 
        # and slice off everything after it.
        last_one_index = binary_str.rfind('1')
        return '0b' + binary_str[:last_one_index]

    ############################################################################
    # PKCS7 PADDING
    ############################################################################

    def pkcs7_padding(self, data):
        """
        Apply PKCS7 padding.
        'data' can be:
          - A string (will be encoded to UTF-8),
          - A binary string starting with '0b' (will be converted to bytes),
          - Already bytes (no conversion needed).
        """
        if isinstance(data, str):
            # If it's a '0b...' string
            if data.startswith('0b'):
                # treat it as a binary string
                data = self.binary_to_bytes(data[2:])
            else:
                # treat it as normal text -> encode to UTF-8
                data = data.encode('utf-8')
        elif not isinstance(data, bytes):
            # If it's neither str nor bytes, raise an error
            raise TypeError("pkcs7_padding requires data to be str or bytes.")

        padding_length = 16 - (len(data) % 16)
        padded_data = data + bytes([padding_length] * padding_length)
        return padded_data

    def pkcs7_unpadding(self, data):
        """
        Remove PKCS7 padding. Returns raw bytes (no UTF-8 decoding here).
        """
        if not data:
            return data
        padding_length = data[-1]
        if padding_length < 1 or padding_length > 16:
            # Invalid padding
            raise ValueError("Invalid PKCS7 padding.")
        return data[:-padding_length]

    ############################################################################
    # ECB MODE
    ############################################################################

    def ecb_encrypt(self, plaintext):
        """
        Encrypt data in ECB mode.
        'plaintext' can be str or bytes (or '0b...' string).
        Returns raw encrypted bytes.
        """
        padded_data = self.pkcs7_padding(plaintext)

        encrypted_blocks = []
        for i in range(0, len(padded_data), 16):
            block = padded_data[i:i+16]
            encrypted_block = self.aes.encrypt(block)
            encrypted_blocks.append(encrypted_block)
        return b''.join(encrypted_blocks)

    def ecb_decrypt(self, ciphertext):
        """
        Decrypt data in ECB mode. 
        'ciphertext' must be bytes. 
        Returns raw bytes (with PKCS7 unpadding removed).
        """
        if len(ciphertext) % 16 != 0:
            raise ValueError("Ciphertext length must be multiple of 16 bytes for ECB mode.")

        decrypted_blocks = []
        for i in range(0, len(ciphertext), 16):
            block = ciphertext[i:i+16]
            decrypted_block = self.aes.decrypt(block)
            decrypted_blocks.append(decrypted_block)

        decrypted_data = self.pkcs7_unpadding(b''.join(decrypted_blocks))
        # Return raw bytes. If you know it's text, decode externally.
        return decrypted_data

    ############################################################################
    # CBC MODE
    ############################################################################

    def cbc_encrypt(self, plaintext):
        """
        Encrypt data in CBC mode.
        'plaintext' can be str/bytes.
        Returns IV + encrypted bytes.
        """
        padded_data = self.pkcs7_padding(plaintext)
        encrypted_blocks = []
        previous_block = self.iv
        print("The Initial Vector (IV):", previous_block.hex())

        for i in range(0, len(padded_data), 16):
            block = padded_data[i:i+16]
            # XOR with previous ciphertext block or IV for the first
            xor_block = bytes([block[j] ^ previous_block[j] for j in range(16)])
            encrypted_block = self.aes.encrypt(xor_block)
            encrypted_blocks.append(encrypted_block)
            previous_block = encrypted_block

        return self.iv + b''.join(encrypted_blocks)

    def cbc_decrypt(self, ciphertext):
        """
        Decrypt data in CBC mode.
        Expects: IV (16 bytes) + ciphertext.
        Returns raw bytes after unpadding.
        """
        if len(ciphertext) < 16 or (len(ciphertext) % 16) != 0:
            raise ValueError("Ciphertext (including IV) must be multiple of 16 bytes for CBC.")

        iv = ciphertext[:16]
        ciphertext = ciphertext[16:]
        previous_block = iv

        print("The Initial Vector (IV):", iv.hex())

        decrypted_blocks = []
        for i in range(0, len(ciphertext), 16):
            block = ciphertext[i:i+16]
            decrypted_block = self.aes.decrypt(block)
            # XOR with previous ciphertext block
            xor_block = bytes([decrypted_block[j] ^ previous_block[j] for j in range(16)])
            decrypted_blocks.append(xor_block)
            previous_block = block

        decrypted_data = self.pkcs7_unpadding(b''.join(decrypted_blocks))
        return decrypted_data

    ############################################################################
    # CFB MODE (64-bit or 128-bit)
    ############################################################################

    def cfb_encrypt(self, plaintext, segment_size=128):
        """
        Encrypt data in CFB mode.
        For text data, 'plaintext' can be str. For arbitrary data, pass bytes.
        segment_size can be 64 or 128 bits.
        """
        if segment_size not in [64, 128]:
            raise ValueError("Segment size must be either 64 or 128 bits for CFB.")

        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')

        segment_bytes = segment_size // 8
        encrypted_blocks = []
        previous_block = self.iv

        print("The Initial Vector (IV):", previous_block.hex())

        for i in range(0, len(plaintext), segment_bytes):
            segment = plaintext[i:i+segment_bytes]
            encrypted_iv = self.aes.encrypt(previous_block)
            encrypted_segment = bytes([segment[j] ^ encrypted_iv[j] for j in range(len(segment))])
            encrypted_blocks.append(encrypted_segment)

            # Shift register
            if segment_size == 64:
                # Move left by segment_bytes in a 16-byte shift register
                previous_block = previous_block[segment_bytes:] + encrypted_segment
            else:
                # 128-bit shift
                previous_block = encrypted_segment

        return self.iv + b''.join(encrypted_blocks)

    def cfb_decrypt(self, ciphertext, segment_size=128):
        """
        Decrypt data in CFB mode.
        Expects: IV + ciphertext blocks.
        Returns raw bytes. If you know it is text, decode externally.
        """
        if segment_size not in [64, 128]:
            raise ValueError("Segment size must be either 64 or 128 bits for CFB.")

        iv = ciphertext[:16]
        ciphertext = ciphertext[16:]
        previous_block = iv
        segment_bytes = segment_size // 8

        print("The Initial Vector (IV):", iv.hex())

        decrypted_blocks = []
        for i in range(0, len(ciphertext), segment_bytes):
            segment = ciphertext[i:i+segment_bytes]
            encrypted_iv = self.aes.encrypt(previous_block)
            decrypted_segment = bytes([segment[j] ^ encrypted_iv[j] for j in range(len(segment))])
            decrypted_blocks.append(decrypted_segment)

            # Shift register
            if segment_size == 64:
                previous_block = previous_block[segment_bytes:] + segment
            else:
                previous_block = segment

        return b''.join(decrypted_blocks)

    ############################################################################
    # OFB MODE
    ############################################################################

    def ofb_encrypt(self, plaintext):
        """
        Encrypt data using OFB mode.
        Returns IV + ciphertext bytes.
        """
        padded_data = self.pkcs7_padding(plaintext)
        encrypted_blocks = []
        previous_block = self.iv

        print("The Initial Vector (IV):", previous_block.hex())

        for i in range(0, len(padded_data), 16):
            block = padded_data[i:i+16]
            encrypted_iv = self.aes.encrypt(previous_block)
            encrypted_block = bytes([block[j] ^ encrypted_iv[j] for j in range(len(block))])
            encrypted_blocks.append(encrypted_block)
            previous_block = encrypted_iv

        return self.iv + b''.join(encrypted_blocks)

    def ofb_decrypt(self, ciphertext):
        """
        Decrypt data using OFB mode.
        Expects: IV (16 bytes) + ciphertext.
        Returns raw unpadded bytes.
        """
        if len(ciphertext) < 16 or (len(ciphertext) % 16) != 0:
            raise ValueError("Ciphertext (including IV) must be multiple of 16 bytes for OFB.")

        iv = ciphertext[:16]
        ciphertext = ciphertext[16:]
        previous_block = iv

        print("The Initial Vector (IV):", iv.hex())

        decrypted_blocks = []
        for i in range(0, len(ciphertext), 16):
            block = ciphertext[i:i+16]
            encrypted_iv = self.aes.encrypt(previous_block)
            decrypted_block = bytes([block[j] ^ encrypted_iv[j] for j in range(len(block))])
            decrypted_blocks.append(decrypted_block)
            previous_block = encrypted_iv

        decrypted_data = self.pkcs7_unpadding(b''.join(decrypted_blocks))
        return decrypted_data

    ############################################################################
    # CTR MODE
    ############################################################################

    def ctr_encrypt(self, plaintext):
        """
        Encrypt data in CTR mode.
        No padding is required. Returns IV + encrypted bytes.
        """
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')

        encrypted_blocks = []
        counter = int.from_bytes(self.iv, byteorder='big')  # convert IV to a big-endian integer
        print("The Initial Vector (IV):", self.iv.hex())

        for i in range(0, len(plaintext), 16):
            block = plaintext[i:i+16]
            encrypted_counter = self.aes.encrypt(counter.to_bytes(16, byteorder='big'))
            encrypted_block = bytes([block[j] ^ encrypted_counter[j] for j in range(len(block))])
            encrypted_blocks.append(encrypted_block)
            counter += 1

        return self.iv + b''.join(encrypted_blocks)

    def ctr_decrypt(self, ciphertext):
        """
        Decrypt data in CTR mode.
        Expects IV (16 bytes) + ciphertext blocks.
        Returns raw bytes (no padding).
        """
        if len(ciphertext) < 16:
            raise ValueError("Ciphertext is too short for CTR mode (missing IV).")

        iv = ciphertext[:16]
        ciphertext = ciphertext[16:]
        counter = int.from_bytes(iv, byteorder='big')
        print("The Initial Vector (IV):", iv.hex())

        decrypted_blocks = []
        for i in range(0, len(ciphertext), 16):
            block = ciphertext[i:i+16]
            encrypted_counter = self.aes.encrypt(counter.to_bytes(16, byteorder='big'))
            decrypted_block = bytes([block[j] ^ encrypted_counter[j] for j in range(len(block))])
            decrypted_blocks.append(decrypted_block)
            counter += 1

        return b''.join(decrypted_blocks)
