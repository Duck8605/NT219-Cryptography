from tinyec import registry
from tinyec.ec import Point
import random

# Define a manual list of available curves based on tinyec's documentation.
AVAILABLE_CURVES = [
    "secp192r1",
    "secp224r1",
    "secp256r1",
    "secp384r1",
    "secp521r1",
    "brainpoolP160r1",
    "brainpoolP192r1",
    "brainpoolP224r1",
    "brainpoolP256r1",
    "brainpoolP320r1",
    "brainpoolP384r1",
    "brainpoolP512r1"
]

def choose_curve():
    """Let the user select an ECC curve from the available list."""
    print("Available curves:")
    for i, curve_name in enumerate(AVAILABLE_CURVES, start=1):
        print(f"{i}. {curve_name}")
    choice = input("Select a curve by number (default 3 for secp256r1): ").strip() or "3"
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(AVAILABLE_CURVES):
            raise ValueError("Invalid selection")
        selected_curve = AVAILABLE_CURVES[idx]
        curve = registry.get_curve(selected_curve)
        print(f"Selected curve: {curve.name}")
        return curve
    except Exception as e:
        print(f"Error selecting curve: {e}")
        return None

def generate_key_pair(curve):
    """
    Generate an ECC key pair.
    Private key: Random integer in [1, curve.field.n - 1]
    Public key: Computed as private_key * G (generator point)
    """
    # sua key tu 1028 tro len
    private_key = random.randrange(1, curve.field.n)
    public_key = private_key * curve.g
    print("\nGenerated Key Pair:")
    print(f"Private Key: {private_key}")
    print(f"Public Key (x, y): ({public_key.x}, {public_key.y})")
    return private_key, public_key

def compute_shared_secret(their_public, my_private):
    """
    Compute the shared secret using ECDHE.
    Each party computes: shared_point = my_private * their_public.
    The shared secret (for further symmetric key derivation) is typically the x-coordinate.
    """
    shared_point = my_private * their_public
    print("\nComputed Shared Secret Point:")
    print(f"(x, y): ({shared_point.x}, {shared_point.y})")
    return shared_point

def main():
    curve = None
    my_private = None
    my_public = None

    while True:
        print("\nECDHE Key Exchange")
        print("1. Select ECC Curve")
        print("2. Generate Key Pair (private, public)")
        print("3. Compute Shared Secret")
        print("4. Enter Sender's Public Key and Compute Session Key")
        print("5. Exit")
        choice = input("Select an option: ").strip()

        if choice == "1":
            curve = choose_curve()
            if curve is None:
                print("Curve selection failed. Please try again.")
        elif choice == "2":
            if not curve:
                print("Error: Please select an ECC curve first!")
                continue
            my_private, my_public = generate_key_pair(curve)
        elif choice == "3":
            if not curve or my_private is None or my_public is None:
                print("Error: Please select a curve and generate your key pair first!")
                continue
            print("Enter the other party's public key coordinates:")
            try:
                x_val = int(input("X coordinate: ").strip())
                y_val = int(input("Y coordinate: ").strip())
                their_public = Point(curve, x_val, y_val)
            except Exception as e:
                print(f"Invalid public key input: {e}")
                continue
            compute_shared_secret(their_public, my_private)
        elif choice == "4":
            if not curve or my_private is None:
                print("Error: Please select a curve and generate your key pair first!")
                continue
            try:
                print("Enter the sender's public key coordinates:")
                x_val = int(input("X coordinate: ").strip())
                y_val = int(input("Y coordinate: ").strip())
                sender_public = Point(curve, x_val, y_val)

                # Compute session key using my private key and sender's public key
                session_key = compute_shared_secret(sender_public, my_private)
                print("\nSession Key (x-coordinate):", session_key.x)
            except Exception as e:
                print(f"Error processing sender's public key: {e}")
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
