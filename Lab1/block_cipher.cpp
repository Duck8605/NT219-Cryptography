#include <iostream>
#include <string>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <cstring>

#include "include/cryptopp/cryptlib.h"
#include "include/cryptopp/secblock.h"
#include "include/cryptopp/osrng.h"
#include "include/cryptopp/modes.h"
#include "include/cryptopp/aes.h"      // for reference
#include "include/cryptopp/des.h"
#include "include/cryptopp/xts.h"       // for XTS mode
#include "include/cryptopp/ccm.h"       // for CCM mode
#include "include/cryptopp/gcm.h"       // for GCM mode
#include "include/cryptopp/filters.h"
#include "include/cryptopp/hex.h"
#include "include/cryptopp/base64.h"


using namespace CryptoPP;

// Helper: read file contents into a string
std::string ReadFile(const std::string &filename) {
    std::ifstream ifs(filename, std::ios::binary);
    std::stringstream buffer;
    buffer << ifs.rdbuf();
    return buffer.str();
}

// Helper: write a string to a file
void WriteFile(const std::string &filename, const std::string &data) {
    std::ofstream ofs(filename, std::ios::binary);
    ofs << data;
}

// Helper: convert string to hex representation
std::string StringToHex(const std::string &input) {
    std::string encoded;
    StringSource ss(input, true,
        new HexEncoder(new StringSink(encoded))
    );
    return encoded;
}

// Helper: convert string to Base64
std::string StringToBase64(const std::string &input) {
    std::string encoded;
    StringSource ss(input, true,
        new Base64Encoder(new StringSink(encoded))
    );
    return encoded;
}

// Generates an 8-byte key and an 8-byte IV for DES
void GenerateKeyAndIV(SecByteBlock &key, byte iv[DES::BLOCKSIZE]) {
    AutoSeededRandomPool prng;
    key.CleanNew(DES::DEFAULT_KEYLENGTH);
    prng.GenerateBlock(key, key.size());
    prng.GenerateBlock(iv, DES::BLOCKSIZE);
}

// Process DES encryption/decryption using selected mode.
// For DES modes that require only key+IV, we use the provided key and IV.
// For XTS, we expand the 8-byte key to 24 bytes (by repeating it).
// For CCM and GCM (authenticated modes), we use an empty associated data.
std::string ProcessDES(const std::string &input, const SecByteBlock &key, const byte iv[DES::BLOCKSIZE],
                       bool encrypt, int modeChoice) {
    std::string output;
    try {
        switch(modeChoice) {
            case 1: { // ECB Mode
                if(encrypt) {
                    ECB_Mode<DES>::Encryption e;
                    e.SetKey(key, key.size());
                    StringSource ss(input, true,
                        new StreamTransformationFilter(e,
                            new StringSink(output)
                        )
                    );
                } else {
                    ECB_Mode<DES>::Decryption d;
                    d.SetKey(key, key.size());
                    StringSource ss(input, true,
                        new StreamTransformationFilter(d,
                            new StringSink(output)
                        )
                    );
                }
                break;
            }
            case 2: { // CBC Mode
                if(encrypt) {
                    CBC_Mode<DES>::Encryption e;
                    e.SetKeyWithIV(key, key.size(), iv);
                    StringSource ss(input, true,
                        new StreamTransformationFilter(e,
                            new StringSink(output)
                        )
                    );
                } else {
                    CBC_Mode<DES>::Decryption d;
                    d.SetKeyWithIV(key, key.size(), iv);
                    StringSource ss(input, true,
                        new StreamTransformationFilter(d,
                            new StringSink(output)
                        )
                    );
                }
                break;
            }
            case 3: { // OFB Mode
                if(encrypt) {
                    OFB_Mode<DES>::Encryption e;
                    e.SetKeyWithIV(key, key.size(), iv);
                    StringSource ss(input, true,
                        new StreamTransformationFilter(e,
                            new StringSink(output)
                        )
                    );
                } else {
                    OFB_Mode<DES>::Decryption d;
                    d.SetKeyWithIV(key, key.size(), iv);
                    StringSource ss(input, true,
                        new StreamTransformationFilter(d,
                            new StringSink(output)
                        )
                    );
                }
                break;
            }
            case 4: { // CFB Mode
                if(encrypt) {
                    CFB_Mode<DES>::Encryption e;
                    e.SetKeyWithIV(key, key.size(), iv);
                    StringSource ss(input, true,
                        new StreamTransformationFilter(e,
                            new StringSink(output)
                        )
                    );
                } else {
                    CFB_Mode<DES>::Decryption d;
                    d.SetKeyWithIV(key, key.size(), iv);
                    StringSource ss(input, true,
                        new StreamTransformationFilter(d,
                            new StringSink(output)
                        )
                    );
                }
                break;
            }
            case 5: { // CTR Mode
                if(encrypt) {
                    CTR_Mode<DES>::Encryption e;
                    e.SetKeyWithIV(key, key.size(), iv);
                    StringSource ss(input, true,
                        new StreamTransformationFilter(e,
                            new StringSink(output)
                        )
                    );
                } else {
                    CTR_Mode<DES>::Decryption d;
                    d.SetKeyWithIV(key, key.size(), iv);
                    StringSource ss(input, true,
                        new StreamTransformationFilter(d,
                            new StringSink(output)
                        )
                    );
                }
                break;
            }
            case 6: { // XTS Mode using XTS<DES>
                // XTS mode requires a 24-byte key. Expand the 8-byte key by repeating it.
                SecByteBlock xtsKey(24);
                for(size_t i = 0; i < xtsKey.size(); i++) {
                    xtsKey[i] = key[i % key.size()];
                }
                // In XTS mode, a "tweak" is needed. We'll use the IV as tweak.
                if(encrypt) {
                    XTS<DES>::Encryption xtsEnc;
                    xtsEnc.SetKeyWithIV(xtsKey, xtsKey.size(), iv);
                    StringSource ss(input, true,
                        new StreamTransformationFilter(xtsEnc,
                            new StringSink(output)
                        )
                    );
                } else {
                    XTS<DES>::Decryption xtsDec;
                    xtsDec.SetKeyWithIV(xtsKey, xtsKey.size(), iv);
                    StringSource ss(input, true,
                        new StreamTransformationFilter(xtsDec,
                            new StringSink(output)
                        )
                    );
                }
                break;
            }
            case 7: { // CCM Mode (Authenticated Encryption)
                if(encrypt) {
                    CCM<DES>::Encryption enc;
                    // Use IV as nonce; tag length is set via default (e.g., 4 bytes)
                    enc.SetKeyWithIV(key, key.size(), iv, DES::BLOCKSIZE);
                    enc.SpecifyDataLengths(0, input.size(), 0);
                    StringSource ss(input, true,
                        new AuthenticatedEncryptionFilter(enc,
                            new StringSink(output)
                        )
                    );
                } else {
                    CCM<DES>::Decryption dec;
                    dec.SetKeyWithIV(key, key.size(), iv, DES::BLOCKSIZE);
                    dec.SpecifyDataLengths(0, input.size() - 4, 0); // assuming 4-byte tag appended
                    StringSource ss(input, true,
                        new AuthenticatedDecryptionFilter(dec,
                            new StringSink(output)
                        )
                    );
                }
                break;
            }
            case 8: { // GCM Mode (Authenticated Encryption)
                if(encrypt) {
                    GCM<DES>::Encryption enc;
                    enc.SetKeyWithIV(key, key.size(), iv, DES::BLOCKSIZE);
                    StringSource ss(input, true,
                        new AuthenticatedEncryptionFilter(enc,
                            new StringSink(output)
                        )
                    );
                } else {
                    GCM<DES>::Decryption dec;
                    dec.SetKeyWithIV(key, key.size(), iv, DES::BLOCKSIZE);
                    StringSource ss(input, true,
                        new AuthenticatedDecryptionFilter(dec,
                            new StringSink(output)
                        )
                    );
                }
                break;
            }
            default:
                throw std::runtime_error("Unsupported mode selected.");
        }
    }
    catch(const Exception &ex) {
        std::cerr << "Error in ProcessDES: " << ex.what() << std::endl;
    }
    return output;
}

int main() {
    int operation, modeChoice, outputFormat, textOption, keyOption;
    std::string inputText;
    SecByteBlock key(DES::DEFAULT_KEYLENGTH);
    byte iv[DES::BLOCKSIZE];

    std::cout << "Select operation:\n1. Encrypt\n2. Decrypt\nChoice: ";
    std::cin >> operation;
    std::cin.ignore();

    std::cout << "Select DES mode:\n";
    std::cout << "1. ECB\n2. CBC\n3. OFB\n4. CFB\n5. CTR\n6. XTS\n7. CCM\n8. GCM\nChoice: ";
    std::cin >> modeChoice;
    std::cin.ignore();

    std::cout << "Select key/IV option:\n1. Generate randomly\n2. Read from file\nChoice: ";
    std::cin >> keyOption;
    std::cin.ignore();
    if(keyOption == 1) {
        GenerateKeyAndIV(key, iv);
    } else {
        std::string keyFile, ivFile;
        std::cout << "Enter key file name: ";
        std::getline(std::cin, keyFile);
        std::string keyData = ReadFile(keyFile);
        key.Assign((const byte*)keyData.data(), DES::DEFAULT_KEYLENGTH);
        std::cout << "Enter IV file name: ";
        std::getline(std::cin, ivFile);
        std::string ivData = ReadFile(ivFile);
        std::memcpy(iv, ivData.data(), DES::BLOCKSIZE);
    }

    std::cout << "Select text input option:\n1. Input from screen\n2. Read from file\nChoice: ";
    std::cin >> textOption;
    std::cin.ignore();
    if(textOption == 1) {
        std::cout << "Enter text (UTF-8 supported):\n";
        std::getline(std::cin, inputText);
    } else {
        std::string textFile;
        std::cout << "Enter text file name: ";
        std::getline(std::cin, textFile);
        inputText = ReadFile(textFile);
    }

    // Process DES operation
    std::string processed = ProcessDES(inputText, key, iv, (operation == 1), modeChoice);

    // Choose output format
    std::cout << "Select output format:\n1. Hex\n2. Base64\n3. Raw binary\nChoice: ";
    std::cin >> outputFormat;
    std::cin.ignore();
    std::string formattedOutput;
    if(outputFormat == 1) {
        formattedOutput = StringToHex(processed);
    } else if(outputFormat == 2) {
        formattedOutput = StringToBase64(processed);
    } else {
        formattedOutput = processed;
    }

    std::cout << "\nResult:\n" << formattedOutput << "\n";

    std::string outputFile;
    std::cout << "Enter output file name to save result: ";
    std::getline(std::cin, outputFile);
    WriteFile(outputFile, formattedOutput);

    return 0;
}
