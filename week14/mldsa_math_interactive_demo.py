# NIST FIPS 204 (ML-DSA) Interactive Mathematical Demonstrations

import math
import time

class MLDSA_Math_Demo:
    """Interactive demonstration of ML-DSA mathematical foundations from FIPS 204."""

    def __init__(self):
        # --- Constants (as defined in FIPS 204) ---
        self.Q = 8380417 # Prime modulus q = 2^23 - 2^13 + 1
        self.N = 256     # Polynomial degree n = 256
        # Other parameters (d, eta, gamma1, gamma2, beta, tau, omega) are specific
        # to parameter sets (ML-DSA-44, -65, -87) and not needed for these basic demos.

    def wait_for_user(self):
        """Pauses execution until the user presses Enter."""
        input("\nPress Enter to continue to the next step...")
        print("-"*70)
        time.sleep(0.5) # Small delay for visual flow

    # --- Basic Modular Arithmetic ---
    def mod_q(self, a):
        """Computes a mod q."""
        return a % self.Q

    def mod_plus_minus_q(self, a):
        """Computes a mod+- q (result in (-q/2, q/2])."""
        val = self.mod_q(a)
        if val > self.Q // 2:
            val -= self.Q
        return val

    def demo_modular_arithmetic(self):
        """Demonstrates basic modular arithmetic operations mod q and mod+- q."""
        print("Step 1: Basic Modular Arithmetic")
        print("ML-DSA operates over integers modulo a prime q.")
        print(f"The prime modulus is q = {self.Q} (which is 2^23 - 2^13 + 1).")
        print("Two main modular operations are used:")
        print("  1. Standard modulo q: `a mod q` results in a value in [0, q-1].")
        print("     Formula: a mod q = a - q * floor(a/q)")
        print("  2. Centered modulo q: `a mod+- q` results in a value in (-q/2, q/2].")
        print("     Formula: Unique m' such that m' = a mod q and -q/2 < m' <= q/2.")
        print("\n--- Demo --- ")

        a1 = 10
        a2 = -10
        a3 = self.Q + 5
        a4 = 5000000
        a5 = -5000000
        a6 = 4190208 # q/2
        a7 = 4190209 # q/2 + 1

        print(f"Standard Modulo q ({self.Q}):")
        print(f"  {a1} mod q = {self.mod_q(a1)}")
        print(f"  {a2} mod q = {self.mod_q(a2)}")
        print(f"  {a3} mod q = {self.mod_q(a3)}")

        print(f"\nCentered Modulo q ({self.Q}):")
        print(f"  {a4} mod+- q = {self.mod_plus_minus_q(a4)}")
        print(f"  {a5} mod+- q = {self.mod_plus_minus_q(a5)}")
        print(f"  {a6} mod+- q = {self.mod_plus_minus_q(a6)} (Expected: {self.Q // 2})")
        print(f"  {a7} mod+- q = {self.mod_plus_minus_q(a7)} (Expected: {self.Q // 2 + 1 - self.Q})")

        self.wait_for_user()

    # --- Polynomial Representation and Arithmetic (Ring R_q) ---
    def poly_add(self, p1, p2):
        """Adds two polynomials in R_q."""
        if len(p1) != self.N or len(p2) != self.N:
            raise ValueError(f"Polynomials must have degree {self.N-1}")
        res = [(self.mod_q(p1[i] + p2[i])) for i in range(self.N)]
        return res

    def poly_sub(self, p1, p2):
        """Subtracts polynomial p2 from p1 in R_q."""
        if len(p1) != self.N or len(p2) != self.N:
            raise ValueError(f"Polynomials must have degree {self.N-1}")
        res = [(self.mod_q(p1[i] - p2[i])) for i in range(self.N)]
        return res

    def poly_mul(self, p1, p2):
        """Multiplies two polynomials in R_q = Z_q[X]/(X^N + 1)."""
        if len(p1) != self.N or len(p2) != self.N:
            raise ValueError(f"Polynomials must have degree {self.N-1}")
        res = [0] * self.N
        temp_prod = [0] * (2 * self.N - 1)

        # Standard polynomial multiplication
        for i in range(self.N):
            for j in range(self.N):
                temp_prod[i + j] = self.mod_q(temp_prod[i + j] + p1[i] * p2[j])

        # Reduction modulo (X^N + 1)
        # For X^k where k >= N, X^k = X^(k-N) * X^N = X^(k-N) * (-1) = -X^(k-N)
        for i in range(self.N, 2 * self.N - 1):
            res[i - self.N] = self.mod_q(res[i - self.N] - temp_prod[i]) # Subtract X^(i-N)

        # Add the lower degree terms
        for i in range(self.N):
            res[i] = self.mod_q(res[i] + temp_prod[i])

        return res

    def demo_polynomial_arithmetic(self):
        """Demonstrates polynomial arithmetic in the ring R_q."""
        print("Step 2: Polynomial Arithmetic in R_q")
        print("ML-DSA heavily uses polynomial arithmetic.")
        print(f"The ring used is R_q = Z_q[X] / (X^N + 1), where N = {self.N}.")
        print("This means polynomials have coefficients in Z_q (integers mod q), and")
        print(f"the polynomial X^{self.N} is treated as being equal to -1.")
        print(f"Polynomials are represented as lists of {self.N} coefficients [p0, p1, ..., p{self.N-1}].")
        print("\nOperations:")
        print("  Addition: (p1 + p2)[i] = (p1[i] + p2[i]) mod q")
        print("  Subtraction: (p1 - p2)[i] = (p1[i] - p2[i]) mod q")
        print("  Multiplication: Standard polynomial multiplication followed by reduction using X^N = -1.")
        print("\n--- Demo --- ")

        # Demo Polynomials
        p_a = [i + 1 for i in range(self.N)] # [1, 2, ..., N]
        p_b = [(self.N - i) for i in range(self.N)] # [N, N-1, ..., 1]
        p_zero = [0] * self.N
        p_x = [0] * self.N; p_x[1] = 1
        p_one = [0] * self.N; p_one[0] = 1
        p_xn_minus_1 = [0] * self.N; p_xn_minus_1[self.N-1] = 1

        print("Let p_a = [1, 2, ..., N] and p_b = [N, N-1, ..., 1]")

        p_sum = self.poly_add(p_a, p_b)
        print(f"\nAddition: p_a + p_b")
        print(f"  Result (first 5 coeffs): {p_sum[:5]}... Last coeff: {p_sum[-1]}")
        print(f"  Expected sum coeff: (i+1) + (N-i) = N+1 = {self.mod_q(self.N+1)}")

        p_diff = self.poly_sub(p_a, p_a)
        print(f"\nSubtraction: p_a - p_a")
        print(f"  Result (first 5 coeffs): {p_diff[:5]}... Last coeff: {p_diff[-1]}")
        print(f"  Expected diff coeff: 0")

        p_prod = self.poly_mul(p_a, p_b)
        print(f"\nMultiplication: p_a * p_b")
        print(f"  Result (first 5 coeffs): {p_prod[:5]}... Last coeff: {p_prod[-1]}")

        print("\nMultiplication Examples:")
        p_x_times_one = self.poly_mul(p_x, p_one)
        print(f"  X * 1 (coeffs): {p_x_times_one[:5]}... Expected: [0, 1, 0, 0, 0]...")

        p_xn = self.poly_mul(p_xn_minus_1, p_x)
        print(f"  X^(N-1) * X = X^N = -1 (coeffs): {p_xn[:5]}... Expected: [-1 mod q, 0, 0, 0, 0]...")
        print(f"  Expected first coeff: {self.mod_q(-1)}")

        self.wait_for_user()

    # --- Add demos for NTT, Rounding, Sampling, Hints here ---
    def bit_reverse_permute(a):
        n = len(a)
        k = int(math.log2(n))
        for j in range(n):
            r = 0
            x = j
            for _ in range(k):
                r = (r << 1) | (x & 1)
                x >>= 1
            if r > j:
                a[j], a[r] = a[r], a[j]

    def ntt(self, a, omega, q):
        # a: length-N array in Z_q,
        # omega: primitive Nth root of unity mod q,
        # q: prime modulus.
        n = len(a)
        logn = int(math.log2(n))
        # 1) bit-reverse permutation
        self.bit_reverse_permute(a)
        # 2) compute butterflies
        m = 2
        for s in range(1, logn+1):  # s=1..logn, m=2^s
            # ζ_m = ω^(N/m) mod q
            zeta_m = pow(omega, n // m, q)
            for start in range(0, n, m):
                w = 1
                for j in range(m // 2):
                    u = a[start + j]
                    v = (a[start + j + m//2] * w) % q
                    # “butterfly” combine
                    a[start + j] = (u + v) % q
                    a[start + j + m//2] = (u - v) % q
                    w = (w * zeta_m) % q
            m *= 2
        # now a[] contains NTT(a)

    def intt(self, a, omega, q):
        # a: length-N NTT values in Z_q,
        # omega: primitive Nth root of unity mod q,
        # q: prime modulus.
        n = len(a)
        logn = int(math.log2(n))
        # 1) bit-reverse permutation
        self.bit_reverse_permute(a)
        # 2) butterflies with omega^{-1}
        inv_omega = pow(omega, q-2, q)  # modular inverse of omega
        m = 2
        for s in range(1, logn+1):
            zeta_m_inv = pow(inv_omega, n // m, q)
            for start in range(0, n, m):
                w = 1
                for j in range(m // 2):
                    u = a[start + j]
                    v = a[start + j + m//2]
                    # invert the “butterfly” step:
                    a[start + j] = (u + v) % q
                    a[start + j + m//2] = ((u - v) * w) % q
                    w = (w * zeta_m_inv) % q
            m *= 2
        # 3) multiply each by n^{-1} mod q
        inv_n = pow(n, q-2, q)
        for i in range(n):
            a[i] = (a[i] * inv_n) % q
        # now a[] contains the original coefficient representation

        
    def poly_mul_ntt(self, a, b, omega, q):
        n = len(a)
        # 1) Copy into two separate buffers
        A = a.copy()
        B = b.copy()
        # 2) Forward NTT on both
        self.ntt(A, omega, q)
        self.ntt(B, omega, q)
        # 3) Pointwise multiply
        C = [(A[i] * B[i]) % q for i in range(n)]
        # 4) Inverse NTT
        self.intt(C, omega, q)
        return C  # C now holds (a * b) mod (X^N + 1) in coefficient form

    def demo_ntt(self):
        print("\n--- Demo: Number‐Theoretic Transform (NTT) ---\n")
        print("NTT is the ‘Fourier‐like’ transform over Z_q that maps a polynomial")
        print("from coefficient form into point‐value form at the N roots of unity.")
        print("In ML‐DSA, we work in R_q = Z_q[X]/(X^N + 1) with N = 2^k, q ≡ 1 (mod 2N).")
        print()
        print("1) Choose prime q such that 2N | (q−1).")
        print("   For example, in a full‐size ML‐DSA, N=256, q=8380417.")
        print("2) Find a primitive root g mod q, then let ω = g^{(q−1)/(2N)} mod q.")
        print("   ⇒ ω^{2N} ≡ 1 mod q, ω^N ≡ -1 mod q.")
        print("3) Forward NTT(a):")
        print("   - Bit‐reverse‐permute the coefficients a[0..N−1].")
        print("   - Do log2(N) stages of ‘butterflies’ using powers of ω.")
        print("   - Result is the vector (a(ω^0), a(ω^1), …, a(ω^{N−1})) mod q.")
        print()
        print("   Pseudocode sketch for NTT(a) — size N=8 example:")
        print("     N = 8,  log2(N) = 3")
        print("     # Suppose ω^4 ≡ -1 mod q, ω^8 ≡ 1 mod q.")
        print("     bit_reverse(a)")
        print("     m = 2")
        print("     for s in 1..3:                   # s=1,2,3; m=2,4,8")
        print("         ζ = ω^(N/m)")
        print("         for start in range(0, N, m):")
        print("             w = 1")
        print("             for j in 0..(m/2−1):")
        print("                 u = a[start+j]")
        print("                 v = a[start+j+m/2] * w mod q")
        print("                 a[start+j]        = (u + v) mod q")
        print("                 a[start+j + m/2] = (u - v) mod q")
        print("                 w = (w * ζ) mod q")
        print("         m = 2*m")
        print("     # now a[] holds NTT(a)")
        print()
        print("4) Inverse NTT is the same butterfly pattern but using ω⁻¹ and")
        print("   multiplying each output by N⁻¹ mod q at the end.")
        print()
        print("5) To multiply two polynomials A(X), B(X) in R_q:")
        print("     A_ntt = NTT(A)   # cost ~ N log N")
        print("     B_ntt = NTT(B)")
        print("     C_ntt = (A_ntt[i] * B_ntt[i]) mod q   # pointwise")
        print("     C = INTT(C_ntt)   # cost ~ N log N")
        print("   => overall ~ N log N instead of N^2.")
        print()
        print("--- (Optional toy run for N=8, q=17) ---")
        # If you want to show a tiny actual NTT example where N=8, q=17, ω=3:
        q = 17
        N = 8
        # 3^((17-1)/8) = 3^2 = 9 mod 17, but 9^4=6561 ≡ 1 mod17, 9^2=81≡13 mod17 = -4, not -1.
        # Let’s pick ω = 3 anyway to illustrate shape:
        omega = 3
        # a small polynomial
        a = [5, 2, 7, 1, 0, 3, 4, 6]
        print(f" Original a (coeffs): {a}")
        # Forward NTT(a):
        def bit_reverse_permute(arr):
            n_ = len(arr)
            k_ = int(math.log2(n_))
            for j in range(n_):
                r = 0
                x = j
                for _ in range(k_):
                    r = (r << 1) | (x & 1)
                    x >>= 1
                if r > j:
                    arr[j], arr[r] = arr[r], arr[j]
        def ntt_small(arr, ω, mod):
            n_ = len(arr)
            bit_reverse_permute(arr)
            m_ = 2
            while m_ <= n_:
                ζ = pow(ω, n_ // m_, mod)
                for start in range(0, n_, m_):
                    w_ = 1
                    half = m_ // 2
                    for j in range(half):
                        u_ = arr[start + j]
                        v_ = (arr[start + j + half] * w_) % mod
                        arr[start + j] = (u_ + v_) % mod
                        arr[start + j + half] = (u_ - v_) % mod
                        w_ = (w_ * ζ) % mod
                m_ *= 2
        arr_ntt = a.copy()
        ntt_small(arr_ntt, omega, q)
        print(f" NTT(a) (values at ω^i): {arr_ntt}")
        print("\n(For a full‐size ML‐DSA demo, we’d use N=256, q=8380417, ω chosen accordingly.)")
        self.wait_for_user()

    # Placeholder for Rounding demo
    def demo_rounding(self):
        print("Step 4: Rounding Functions (Power2Round, HighBits, LowBits)")
        print("Used for compressing parts of the key (t) and commitment (w).")
        print("Power2Round(r, d) splits r into high/low bits based on 2^d:")
        print("  r = r1 * 2^d + r0, where -2^(d-1) < r0 <= 2^(d-1)")
        print("  HighBits(r, d) returns r1")
        print("  LowBits(r, d) returns r0")
        print("\n--- Demo --- ")
        # Example values (need parameter 'd' from a specific Dilithium level)
        d_example = 13 # Example from Dilithium spec
        r_example = 1234567
        power_of_2d = 1 << d_example

        # Simplified Power2Round logic for demo
        r0 = self.mod_plus_minus_q(r_example % power_of_2d)
        r1 = (r_example - r0) // power_of_2d

        print(f"Example: r = {r_example}, d = {d_example} (2^d = {power_of_2d})")
        print(f"  Power2Round -> (r1, r0) = ({r1}, {r0})")
        print(f"  Check: r1 * 2^d + r0 = {r1 * power_of_2d + r0} (should be {r_example})")
        print(f"  HighBits(r, d) = {r1}")
        print(f"  LowBits(r, d) = {r0}")
        self.wait_for_user()

    # Placeholder for Hint demo
    def make_hint(self, w_poly, r_poly):
        """
        Inputs:
        w_poly: the original A·y polynomial (coeffs mod q).
        r_poly: the recomputed A·z - c·t1 polynomial (coeffs mod q).
        Output:
        h_poly: an array length N where h_i ∈ {−1, 0, +1}.
        The hint tells the verifier if floor(r_i/2^d) = floor(w_i/2^d) or differs by ±1.
        """
        N = self.n
        h = np.zeros(N, dtype=int)
        # STEP A: compute (w1, w0) and (r1, r0)
        w1, w0 = self.power2round(w_poly)  # True high, true low
        r1, r0 = self.power2round(r_poly)  # Recomputed high, recomputed low

        # STEP B: for each coefficient index i:
        for i in range(N):
            if r1[i] == w1[i]:
                h[i] = 0
            elif r1[i] == (w1[i] + 1) % self.q:  # mod q if we’re working mod q
                h[i] = +1
            elif r1[i] == (w1[i] - 1) % self.q:
                h[i] = -1
            else:
                # Any other difference means a large discrepancy → signature
                # would have been rejected during signing. For safety, set h[i]=0.
                h[i] = 0
        return h
    def use_hint(self, h_poly, r_poly):
        """
        Inputs:
        h_poly: array of length N with entries in {−1,0,+1}.
        r_poly: array length N of recomputed A·z - c·t1.
        Output:
        w1_pred: array of length N that should equal the original high bits of A·y.
        """
        w1_pred = np.zeros(self.n, dtype=int)
        r1, r0 = self.power2round(r_poly)  # decomposed r

        for i in range(self.n):
            if h_poly[i] == 0:
                w1_pred[i] = r1[i]
            elif h_poly[i] == +1:
                w1_pred[i] = (r1[i] - 1) % self.q
            else:  # h_poly[i] == -1
                w1_pred[i] = (r1[i] + 1) % self.q
        return w1_pred

    def demo_hints(self):
        print()
        print("Step 5: Hint Functions (MakeHint, UseHint)")
        print("=========================================")
        print("In ML-DSA, the signer does not reveal the low bits of w = A·y.")
        print("Instead, they reveal only w1 = HighBits(w) and a small hint h(X).")
        print()
        print("● HighBits/LoweBits recap:")
        print("  - If w_i is a coefficient in Z_q, then Power2Round(w_i) = (w1_i, w0_i) satisfies")
        print("      w0_i = w_i mod 2^d,  |w0_i| < 2^(d-1),")
        print("      w1_i = (w_i - w0_i) / 2^d mod q.")
        print("    HighBits(w_i) = w1_i,  LowBits(w_i) = w0_i.")
        print()
        print("● Why a hint is needed:")
        print("  Verifier computes r = A·z - c·t1, but never knows the signer’s w0 or w0·c.")
        print("  In fact, r_i = w_i + c_i * t0_i, where t0_i = LowBits(A·s1_i).")
        print("  If c_i * t0_i is small enough, then dividing by 2^d doesn’t cross a boundary,")
        print("  so HighBits(r_i) = HighBits(w_i). But if it crosses ±2^(d-1), then the high bits differ by ±1.")
        print("  The hint h_i ∈ {0, +1, -1} tells the verifier whether to add or subtract 1 when recovering w1_i.")
        print()
        print("● MakeHint(w, r) pseudocode:")
        print("    Input: w_poly (A·y), r_poly (A·z - c·t1), both length N.")
        print("    Output: h_poly of length N with entries in {−1, 0, +1}.")
        print("    For each coefficient index i:")
        print("      (w1_i, w0_i) = Power2Round(w_i)")
        print("      (r1_i, r0_i) = Power2Round(r_i)")
        print("      if   r1_i ==  w1_i:       h_i =  0")
        print("      elif r1_i == (w1_i + 1 mod q): h_i = +1")
        print("      elif r1_i == (w1_i - 1 mod q): h_i = -1")
        print("      else:  h_i = 0   # out-of-bounds → should not occur in a valid signature")
        print()
        print("● UseHint(h, r) pseudocode (verifier side):")
        print("    Input: h_poly (length N), r_poly = A·z - c·t1.")
        print("    Output: w1_pred (length N).")
        print("    For each i:")
        print("      (r1_i, r0_i) = Power2Round(r_i)")
        print("      if   h_i ==  0:    w1_pred[i] = r1_i")
        print("      elif h_i == +1:    w1_pred[i] = (r1_i - 1) mod q")
        print("      else (h_i == -1):  w1_pred[i] = (r1_i + 1) mod q")
        print()
        print("  The verifier then checks that w1_pred == w1 (the signer’s published high bits).")
        print()
        print("--- Toy Example (N=4, q=17, d=2) ---")
        print(" Suppose the signer had w = [5, 10, 3, 14] (coeffs mod 17).")
        print("   ➔ Power2Round(w):")
        print("        5  = 4*1 +  1   ⇒ w1[0]=1, w0[0]=+1")
        print("       10  = 4*2 +  2   ⇒ w1[1]=2, w0[1]=+2")
        print("        3  = 4*1 -  1   ⇒ w1[2]=1, w0[2]= -1")
        print("       14  = 4*4 -  2   ⇒ w1[3]=4, w0[3]= -2")
        print("   so w1 = [1,2,1,4],  w0 = [1,2,-1,-2].")
        print()
        print(" Suppose c = [1,0,1,0] and the signer’s t0[2] = 1. Then c·t0 = [0,0,1,0].")
        print("   r = w + c·t0 = [5,10, 3,14] + [0,0,1,0] = [5,10,4,14].")
        print("   Power2Round(r):")
        print("        5  = 4*1 +  1   ⇒ r1[0]=1, r0[0]=+1")
        print("       10  = 4*2 +  2   ⇒ r1[1]=2, r0[1]=+2")
        print("        4  = 4*1 +  0   ⇒ r1[2]=1, r0[2]= 0")
        print("       14  = 4*4 -  2   ⇒ r1[3]=4, r0[3]= -2")
        print("   so r1 = [1,2,1,4]. Compare to w1 = [1,2,1,4]. All match → h = [0,0,0,0].")
        print("  Verifier’s UseHint: each r1[i] == w1[i], so w1_pred = [1,2,1,4] matches.")
        print()
        print("In a real ML-DSA, indices where r1 differs by ±1 would get h_i=±1,")
        print("and the verifier would correct r1[i] → w1[i] using that hint bit.")
        self.wait_for_user()

    def run_all_demos(self):
        """Runs all demonstration steps sequentially."""
        print("Starting ML-DSA Mathematical Foundations Demo...")
        print("="*70)
        self.demo_modular_arithmetic()
        self.demo_polynomial_arithmetic()
        self.demo_ntt() # Placeholder
        self.demo_rounding() # Placeholder
        self.demo_hints() # Placeholder
        print("\nAll demonstration steps complete.")
        print("="*70)

# --- Main Execution ---
if __name__ == "__main__":
    demo = MLDSA_Math_Demo()
    demo.run_all_demos()

