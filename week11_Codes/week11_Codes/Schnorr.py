# Schnorr Digital Signature Scheme (Educational Demo)
import base64
import hashlib
import random
from Crypto.Util import number

# === Generate Keys ===
def generate_keys(bit_length=512):
    print("\n🔐 Generating Schnorr Key Pair...")
    q = number.getPrime(256)  # small prime order
    while True:
        p = q * number.getPrime(256) + 1
        if number.isPrime(p):
            break
    while True:
        g = random.randrange(2, p-1)
        if pow(g, q, p) == 1:
            break
    x = random.randrange(1, q)       # private key
    y = pow(g, x, p)                 # public key
    print("✔️ Key components:")
    print(f"   Prime p = {p}\n   Order q = {q}\n   Generator g = {g}")
    print(f"   Private key x = {x}\n   Public key y = {y}")
    with open("schnorr_private.txt", "w") as f:
        f.write(f"{p}\n{q}\n{g}\n{x}")
    with open("schnorr_public.txt", "w") as f:
        f.write(f"{p}\n{q}\n{g}\n{y}")
    return (p, q, g, x), (p, q, g, y)

# === Load Keys ===
def load_private_key(path="schnorr_private.txt"):
    with open(path) as f:
        p, q, g, x = map(int, f.read().splitlines())
    return p, q, g, x

def load_public_key(path="schnorr_public.txt"):
    with open(path) as f:
        p, q, g, y = map(int, f.read().splitlines())
    return p, q, g, y

# === Sign Message ===
def sign_message(p, q, g, x, message: bytes):
    print("\n✍️ Schnorr Signing...")
    k = random.randrange(1, q)
    r = pow(g, k, p)
    e = int(hashlib.sha256(str(r).encode() + message).hexdigest(), 16) % q
    s = (k - x * e) % q
    print(f"Step 1: k = random in [1, q-1], r = g^k mod p = {r}")
    print(f"Step 2: e = H(r || m) mod q = {e}")
    print(f"Step 3: s = k - x * e mod q = {s}")
    sig = f"{e}\n{s}"
    with open("signature.txt", "w") as f:
        f.write(sig)
    print("✔️ Signature saved to signature.txt")
    return e, s

# === Verify Signature ===
def verify_signature(p, q, g, y, message: bytes, e: int, s: int):
    print("\n🔍 Schnorr Verifying...")
    r_prime = (pow(g, s, p) * pow(y, e, p)) % p
    e_prime = int(hashlib.sha256(str(r_prime).encode() + message).hexdigest(), 16) % q
    print(f"Step 1: r' = g^s * y^e mod p = {r_prime}")
    print(f"Step 2: e' = H(r' || m) mod q = {e_prime}")
    if e == e_prime:
        print("✅ Signature is VALID.")
    else:
        print("❌ Signature is INVALID.")

# === Main Program ===
def main():
    print("=== Schnorr Digital Signature ===")
    mode = input("Choose mode: (1) Sign, (2) Verify [default=1]: ").strip() or "1"

    if mode == "1":
        use_existing = input("Use existing key? (y/n) [default=n]: ").strip().lower() or "n"
        if use_existing == "y":
            p, q, g, x = load_private_key()
        else:
            (p, q, g, x), _ = generate_keys()
        msg = input("Enter message to sign: ").encode()
        sign_message(p, q, g, x, msg)

    elif mode == "2":
        p, q, g, y = load_public_key()
        msg = input("Enter message to verify: ").encode()
        sig_file = input("Signature file [default=signature.txt]: ").strip() or "signature.txt"
        try:
            with open(sig_file) as f:
                e, s = map(int, f.read().splitlines())
        except:
            print("❌ Failed to load signature.")
            return
        verify_signature(p, q, g, y, msg, e, s)

    else:
        print("Invalid mode.")

if __name__ == "__main__":
    main()