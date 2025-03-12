#include <iostream>
#include <string>
#include <cstdlib>

#include "cryptopp-master/cryptlib.h"
#include "cryptopp-master/secblock.h"
#include "cryptopp-master/osrng.h"
#include "cryptopp-master/modes.h"
#include "cryptopp-master/aes.h"
#include "cryptopp-master/des.h"
#include "cryptopp-master/filters.h"
#include "cryptopp-master/hex.h"

using namespace CryptoPP;

int main() {  
    AutoSeededRandomPool prng;

    SecByteBlock key(0x00, DES_EDE2::DEFAULT_KEYLENGTH);
    prng.GenerateBlock(key, key.size());

    byte iv[DES::BLOCKSIZE];  
    prng.GenerateBlock(iv, sizeof(iv));

    std::cout << "plain text: ";

    std::string plain;
    std::getline(std::cin, plain);
    std::string cipher, encoded, recovered;

    try {
        CBC_Mode<DES_EDE2>::Encryption e;
        e.SetKeyWithIV(key, key.size(), iv);

        StringSource ss1(plain, true, 
            new StreamTransformationFilter(e, new StringSink(cipher))
        );
    }
    catch (const Exception& e) {
        std::cerr << e.what() << std::endl;
        return 1;
    }

    StringSource ss2(cipher, true,
        new HexEncoder(new StringSink(encoded))
    );

    std::cout << "cipher text: " << encoded << std::endl;

    try {
        CBC_Mode<DES_EDE2>::Decryption d;
        d.SetKeyWithIV(key, key.size(), iv);

        StringSource ss3(cipher, true, 
            new StreamTransformationFilter(d, new StringSink(recovered))
        );

        std::cout << "recovered text: " << recovered << std::endl;
    }
    catch (const Exception& e) {
        std::cerr << e.what() << std::endl;
        return 1;
    }

    return 0;
}
