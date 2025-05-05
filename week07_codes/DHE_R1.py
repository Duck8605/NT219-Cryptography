import random
from sympy import nextprime

def fast_prime(bits=1024):
    """Generate a large prime number efficiently."""
    num = random.getrandbits(bits)
    return nextprime(num)  # Get the next prime number

def find_generator(p):
    """Find a generator g efficiently for Diffie-Hellman."""
    for g in range(2, p):
        # A basic test for generator: if g^((p-1)/2) mod p != 1, then g might be a generator.
        if pow(g, (p-1)//2, p) != 1:
            return g
    return None

def generate_dh_parameters(bits=1024):
    """Automatically generate and display field parameters (p, g)."""
    p = fast_prime(bits)
    g = find_generator(p)
    print(f"\nGenerated Field Parameters:\nPrime (p): {p}\nGenerator (g): {g}")
    return p, g

def generate_key_pair(p, g):
    """
    Generate a key pair (private key and public key).
    This function allows the user to either generate the private key randomly or enter it manually.
    """
    method = input("Do you want to generate the private key randomly? (Y/n): ").strip().lower()
    if method == "" or method == "y":
        private_key = random.randint(2, p - 2)
        print(f"Randomly generated private key: {private_key}")
    else:
        while True:
            try:
                private_key = int(input("Enter your private key (an integer between 2 and p-2): ").strip())
            except ValueError:
                print("Invalid input. Please enter an integer.")
                continue
            if 2 <= private_key <= p - 2:
                break
            else:
                print(f"Private key must be between 2 and {p-2}.")
    public_key = pow(g, private_key, p)
    print(f"\nGenerated Key Pair:\nPrivate Key (x): {private_key}\nPublic Key (g^x): {public_key}")
    return private_key, public_key

def compute_shared_secret(p):
    """Compute the shared session key using manual input of keys."""
    while True:
        try:
            my_private = int(input("Enter your private key (an integer between 2 and p-2): ").strip())
        except ValueError:
            print("Invalid input. Please enter an integer.")
            continue
        if 2 <= my_private <= p - 2:
            break
        else:
            print(f"Private key must be between 2 and {p-2}.")
    while True:
        try:
            their_public = int(input("Enter the other party's public key: ").strip())
        except ValueError:
            print("Invalid input. Please enter an integer.")
            continue
        if 2 <= their_public < p:
            break
        else:
            print(f"Public key must be between 2 and {p-1}.")
    shared_secret = pow(their_public, my_private, p)
    print(f"\nComputed Shared Secret: {shared_secret}")
    return shared_secret

def main():
    p = None
    g = None
    my_private = None
    my_public = None

    while True:
        print("\nDiffie-Hellman Key Exchange")
        print("1. Generate Field Parameters (p, g)")
        print("2. Generate Key Pair (x, g^x) [Random or Manual]")
        print("3. Compute Shared Secret (Session Key)")
        print("4. Exit")
        choice = input("Select an option: ").strip()

        if choice == "1":
            p, g = generate_dh_parameters(1024)

        elif choice == "2":
            # If field parameters are not available, prompt the user to input them manually.
            if not p or not g:
                try:
                    p = int(input("Enter prime number p: ").strip())
                    g = int(input("Enter generator g: ").strip())
                except ValueError:
                    print("Invalid input. p and g must be integers.")
                    continue
            my_private, my_public = generate_key_pair(p, g)

        elif choice == "3":
            # Ensure that p is provided, else prompt the user to input p manually.
            if not p:
                try:
                    p = int(input("Enter prime number p: ").strip())
                except ValueError:
                    print("Invalid input. p must be an integer.")
                    continue
            compute_shared_secret(p)

        elif choice == "4":
            print("Exiting...")
            break

        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main()
