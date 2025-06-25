#!/usr/bin/env python3

import numpy as np
import secrets
import hashlib
import textwrap
import time

class MLDSA_Educational_Demo:
    """Interactive educational demo for ML-DSA based on FIPS 204, using toy parameters."""

    def __init__(self, n=6, q=31):
        # --- Toy Parameters (INSECURE - For Educational Purposes Only!) ---
        self.n = n        # Polynomial degree (Real ML-DSA uses 256)
        self.q = q        # Prime modulus (Real ML-DSA uses 8380417)
        self.eta = 1      # Secret key coefficient bound (Real ML-DSA uses 2 or 4)
        self.gamma1 = 6   # Masking vector coefficient bound (Increased slightly for demo)
        self.gamma2 = (q - 1) // 4 # Rounding range parameter (Real ML-DSA uses (q-1)/88 or (q-1)/32)
        self.beta = 1     # Rejection sampling bound component (Decreased for demo)
        self.d = 2        # Number of bits dropped for t1 compression (Real ML-DSA uses 13)
        self.lam = 128    # Hash output length for c_tilde (bits) (Real ML-DSA uses 128, 192, or 256)
        self.tau = 2      # Number of non-zero coeffs in c (Simplified, real uses 39, 49, 60)

        # --- Internal State ---
        self.A = None
        self.pk = None
        self.sk = None
        self.message = b"This is the message to be signed for the demo."
        self.sigma = None

        print("="*70)
        print("ML-DSA Interactive Educational Demo (FIPS 204) - Revised")
        print("="*70)
        print("WARNING: Using INSECURE toy parameters for demonstration purposes only!")
        print(f"Parameters: n={self.n}, q={self.q}, eta={self.eta}, gamma1={self.gamma1}, d={self.d}, beta={self.beta}, tau={self.tau}")
        print("Real ML-DSA uses much larger parameters (n=256, q=8380417, etc.).")
        print("Polynomial operations are simulated using numpy arrays.")
        print("Hashing uses SHA-256 instead of SHAKE.")
        print("NTT, proper sampling, rounding, hints, and rejection sampling are simplified.")
        print("-"*70)
        self.pause()

    def pause(self, msg=None):
        """Pauses execution and waits for Enter key."""
        input(msg or "Press Enter to continue...")
        print("-"*70)
        time.sleep(0.2)

    def H(self, data, length_bytes=32):
        """Simulates SHAKE using SHA-256, returning specified length."""
        # Insecure: Using repeated/truncated SHA-256 instead of SHAKE
        output = b""
        counter = 0
        while len(output) < length_bytes:
            hasher = hashlib.sha256()
            hasher.update(data)
            hasher.update(counter.to_bytes(4, 'big')) # Add counter for different blocks
            output += hasher.digest()
            counter += 1
        return output[:length_bytes]

    def poly_mod(self, poly):
        """Reduce polynomial coefficients modulo q."""
        return np.mod(poly, self.q)

    def poly_add(self, p1, p2):
        """Add two polynomials mod q."""
        return self.poly_mod(p1 + p2)

    def poly_sub(self, p1, p2):
        """Subtract two polynomials mod q."""
        return self.poly_mod(p1 - p2)

    def poly_mul(self, p1, p2):
        """Multiply two polynomials in R_q = Z_q[X]/(X^n + 1) (Simulated)."""
        # Simplified: Using numpy convolve and manual reduction for X^n = -1
        if isinstance(p1, int):
             p1_coeffs = np.zeros(self.n, dtype=int); p1_coeffs[0] = p1
        else: p1_coeffs = p1
        if isinstance(p2, int):
             p2_coeffs = np.zeros(self.n, dtype=int); p2_coeffs[0] = p2
        else: p2_coeffs = p2

        full_prod = np.convolve(p1_coeffs, p2_coeffs)
        res = np.zeros(self.n, dtype=int)
        for i in range(len(full_prod)):
            deg = i % self.n
            sign = -1 if (i // self.n) % 2 != 0 else 1 # Correction for higher powers X^n = -1, X^2n = 1 etc.
            res[deg] = self.poly_mod(res[deg] + sign * full_prod[i])
        return res

    def poly_dot(self, matrix, vector):
         """Dot product of matrix of polys and vector of polys (Simulated)."""
         rows = matrix.shape[0]
         cols = matrix.shape[1]
         vec_len = vector.shape[0]
         if cols != vec_len:
             raise ValueError(f"Matrix columns ({cols}) must match vector length ({vec_len})")

         res = np.zeros((rows, self.n), dtype=int)
         for i in range(rows):
             row_sum = np.zeros(self.n, dtype=int)
             for j in range(cols):
                 term = self.poly_mul(matrix[i, j], vector[j])
                 row_sum = self.poly_add(row_sum, term)
             res[i] = row_sum
         # If result is a vector (k=1), return 1D array
         return res[0] if rows == 1 else res

    def sample_poly_eta(self):
        """Sample polynomial with coefficients in [-eta, eta] (Simulated)."""
        # Insecure: Using uniform random instead of centered binomial distribution
        return np.random.randint(-self.eta, self.eta + 1, self.n)

    def sample_poly_gamma1(self):
        """Sample polynomial with coefficients in [-gamma1+1, gamma1] (Simulated)."""
        # Insecure: Using uniform random
        # Ensure range is valid even if gamma1=1
        low = -self.gamma1 + 1
        high = self.gamma1 + 1
        if low >= high: high = low + 1 # Ensure randint range is valid
        return np.random.randint(low, high, self.n)

    def mod_plus_minus(self, val, modulus):
        """Compute centered modulo."""
        res = val % modulus
        if res > modulus // 2:
            res -= modulus
        return res

    def power2round(self, r_poly):
        """Simulates Power2Round(r) -> (r1, r0). FIPS 204 Sec 7.4"""
        # r = r1 * 2^d + r0, with -2^(d-1) < r0 <= 2^(d-1)
        modulus = 1 << self.d
        r0 = np.array([self.mod_plus_minus(c, modulus) for c in r_poly])
        r1 = self.poly_mod((r_poly - r0) >> self.d)
        return r1, r0

    def highbits(self, r_poly):
        """Simulates HighBits(r, alpha). FIPS 204 Sec 7.4"""
        # alpha = 2 * gamma2 for Dilithium
        alpha = 2 * self.gamma2
        # Decompose r = r1*alpha + r0, with -alpha/2 < r0 <= alpha/2
        r0 = np.array([self.mod_plus_minus(c, alpha) for c in r_poly])
        r1 = self.poly_mod((r_poly - r0) // alpha) # Integer division for r1
        return r1

    def lowbits(self, r_poly):
        """Simulates LowBits(r, alpha). FIPS 204 Sec 7.4"""
        # alpha = 2 * gamma2 for Dilithium
        alpha = 2 * self.gamma2
        # Decompose r = r1*alpha + r0, with -alpha/2 < r0 <= alpha/2
        r0 = np.array([self.mod_plus_minus(c, alpha) for c in r_poly])
        return r0

    def sample_in_ball(self, seed: bytes) -> np.ndarray:
        """
        Simulates SampleInBall(seed) -> c with tau non-zero ±1 coeffs.
        In this toy version, we use the first 8 bytes of 'seed' (64 bits,
        potentially huge) but reduce it modulo 2**32 before seeding NumPy.
        """
        c_poly = np.zeros(self.n, dtype=int)
        indices = np.arange(self.n)
        
        # Convert first 8 bytes to a big integer, then reduce mod 2**32
        raw_int = int.from_bytes(seed[:8], 'big')
        seed32  = raw_int % (2**32)
        np.random.seed(seed32)       # now guaranteed between 0 and 2**32-1
        
        # Shuffle and pick indices
        np.random.shuffle(indices)
        chosen_indices = indices[: self.tau]
        
        # Signs: use subsequent bits of 'seed' (as before)
        signs = [
            (int.from_bytes(seed[8 + i // 8 : 9 + i // 8], 'big') >> (i % 8)) & 1
            for i in range(self.tau)
        ]
        for i, idx in enumerate(chosen_indices):
            c_poly[idx] = 1 if signs[i] == 0 else -1
        
        # Reseed to system‐random (optional):
        np.random.seed()  # puts it back into nondeterministic mode
        return c_poly

    def make_hint(self, z_poly, r_poly):
        """Simulates MakeHint(z, r) -> h (Simulated). FIPS 204 Sec 7.4"""
        # h=1 iff HighBits(r) != HighBits(r+z)
        # Simplified: Returns dummy value, real hint depends on rounding details
        # alpha = 2 * gamma2
        # r1_r = self.highbits(r_poly)
        # r1_rz = self.highbits(self.poly_add(r_poly, z_poly))
        # h = np.where(r1_r != r1_rz, 1, 0)
        # return h
        return np.zeros(self.n, dtype=int) # Dummy hint for this demo

    def use_hint(self, h_poly, r_poly):
        """Simulates UseHint(h, r) -> w1 (Simulated). FIPS 204 Sec 7.4"""
        # Corrects HighBits(r) using hint h
        # Simplified: Ignores hint, just uses HighBits
        return self.highbits(r_poly)

    def check_norm_z(self, z_poly):
         """Simulates check ||z||_inf < gamma1 - beta."""
         bound = self.gamma1 - self.beta
         # Need centered coeffs for norm check
         z_centered = np.array([self.mod_plus_minus(c, self.q) for c in z_poly])
         max_coeff = np.max(np.abs(z_centered))
         # print(f"    Debug z_norm: max(|z_coeff|) = {max_coeff}, bound = {bound}")
         return max_coeff < bound

    def check_norm_lowbits(self, w_poly, cs2_poly):
         """Simulates check ||LowBits(w - cs2)||_inf < gamma2 - beta."""
         bound = self.gamma2 - self.beta
         diff = self.poly_sub(w_poly, cs2_poly)
         low = self.lowbits(diff)
         # LowBits already returns centered coeffs
         max_coeff = np.max(np.abs(low))
         # print(f"    Debug lowbits_norm: max(|lowbits_coeff|) = {max_coeff}, bound = {bound}")
         return max_coeff < bound

    def run_keygen(self):
        print("\n=== ML-DSA Key Generation (FIPS 204 Algorithm 1 & 6) ===\n")

        # --- Step 1: Generate Master Seed --- (Alg 1 Line 1)
        print("Step 1: Generate 32-byte master seed 𝜉")
        print("Formula: 𝜉 ← 𝔹32 (approved RBG)")
        zeta = secrets.token_bytes(32)
        print(f"Code: zeta = secrets.token_bytes(32)")
        print(f"Value: 𝜉 = {zeta.hex()}")
        self.pause()

        # --- Step 2: Expand Seed --- (Alg 6 Line 1)
        print("Step 2: Expand 𝜉 into public seed 𝜌, private seed 𝜌', key K")
        print("Formula: (𝜌, 𝜌′ , 𝐾) ← H(𝜉‖I2OSP(1,1)‖I2OSP(1,1), 128)")
        expanded = self.H(zeta, 128)            # 128 bytes total
        rho = expanded[:32]
        rho_prime = expanded[32:96]            # next 64 bytes
        K = expanded[96:]                      # last 32 bytes
        print(f"Code: expanded = H(zeta, 128); rho=expanded[:32]; rho_prime=expanded[32:96]; K=expanded[96:]")
        print(f"Value: 𝜌 = {rho.hex()}")
        print(f"Value: 𝜌′= {rho_prime.hex()}")
        print(f"Value: K = {K.hex()}")
        self.pause()

        # --- Step 3: Generate Matrix A --- (Alg 6 Line 3)
        print("Step 3: Expand 𝜌 to generate matrix A (or its NTT form Â)")
        print("Formula: Â ← ExpandA(𝜌) (using SHAKE)")
        # Seed RNG for deterministic A from rho, but reduce to 32 bits
        raw_int = int.from_bytes(rho[:8], 'big')
        seed32 = raw_int % (2**32)
        np.random.seed(seed32)
        self.A = np.array([[ self.poly_mod(np.random.randint(0, self.q, self.n)) ]])  # k=1, l=1
        np.random.seed()  # Reseed
        print(f"Code: self.A = ExpandA(rho) (Simulated)")
        print(f"Value: A[0,0] (first 5 coeffs) = {self.A[0,0][:5]}...")
        self.pause()

        # --- Step 4: Sample Secret Vectors s1, s2 --- (Alg 6 Line 4)
        print("Step 4: Expand 𝜌' to sample secret vectors s1, s2 with small coefficients")
        print("Formula: (s1, s2) ← ExpandS(𝜌′) (coeffs in [-𝜂, 𝜂])")
        raw_int2 = int.from_bytes(rho_prime[:8], 'big')
        seed32_2 = raw_int2 % (2**32)
        np.random.seed(seed32_2)
        s1_vec = np.array([self.sample_poly_eta()])  # l=1
        s2_vec = np.array([self.sample_poly_eta()])  # k=1
        np.random.seed()  # Reseed
        print(f"Code: s1_vec, s2_vec = ExpandS(rho_prime) (Simulated)")
        print(f"Value: s1[0] (first 5 coeffs) = {s1_vec[0][:5]}...")
        print(f"Value: s2[0] (first 5 coeffs) = {s2_vec[0][:5]}...")
        self.pause()

        # --- Step 5: Compute Public Vector t --- (Alg 6 Line 5)
        print("Step 5: Compute public vector t = A·s1 + s2")
        print("Formula: t ← NTT⁻¹(Â ∘ NTT(s1)) + s2 (using NTT for efficiency)")
        t_vec = self.poly_add(self.poly_dot(self.A, s1_vec), s2_vec[0])
        print(f"Code: t_vec = poly_add(poly_dot(A, s1_vec), s2_vec[0])")
        print(f"Value: t[0] (first 5 coeffs) = {t_vec[:5]}...")
        self.pause()

        # --- Step 6: Compress t --- (Alg 6 Line 6)
        print("Step 6: Compress t into high-order (t1) and low-order (t0) parts")
        print("Formula: (t1, t0) ← Power2Round(t) (component-wise, using parameter d)")
        t1_vec, t0_vec = self.power2round(t_vec)
        print(f"Code: t1_vec, t0_vec = power2round(t_vec)")
        print(f"Value: t1[0] (first 5 coeffs) = {t1_vec[:5]}...")
        print(f"Value: t0[0] (first 5 coeffs) = {t0_vec[:5]}...")
        self.pause()

        # --- Step 7: Encode Public and Private Keys --- (Alg 6 Lines 8, 9, 10)
        print("Step 7: Encode public key pk and private key sk")
        print("Formula: pk ← pkEncode(𝜌, t1)")
        print("Formula: tr ← H(pk, 64)")
        print("Formula: sk ← skEncode(𝜌, K, tr, s1, s2, t0)")
        pk_bytes = rho + t1_vec.tobytes()  # Simplified
        tr = self.H(pk_bytes, 64)
        self.pk = (rho, t1_vec)
        self.sk = (rho, K, tr, s1_vec, s2_vec, t0_vec)
        print(f"Code: pk = (rho, t1_vec); tr = H(pk_bytes); sk = (...)")
        print(f"Value: pk = (rho={self.pk[0].hex()}, t1=...)")
        print(f"Value: sk = (rho={self.sk[0].hex()}, K={self.sk[1].hex()}, tr={self.sk[2].hex()}, s1=..., s2=..., t0=...)")
        print("\nKey Generation Complete.")
        self.pause()

    def run_sign(self):
        if self.sk is None:
            print("Error: Key Generation must be run first.")
            return

        print("\n=== ML-DSA Signing (FIPS 204 Algorithm 2 & 7) ===\n")
        rho, K, tr, s1_vec, s2_vec, t0_vec = self.sk
        kappa = 0  # Iteration counter for ExpandMask

        # --- Step 1: Prepare Message --- (Alg 2 Line 10 / Alg 7 Line 6)
        print("Step 1: Prepare formatted message M' (includes context, domain sep - simplified here)")
        print("Formula: M' ← FormatMessage(M, ctx)")  # Simplified
        M_prime = self.message
        print(f"Code: M_prime = self.message")
        print(f"Value: M' = {M_prime!r}")
        self.pause()

        # --- Step 2: Generate Signing Randomness --- (Alg 2 Line 5 / Alg 7 Line 5)
        print("Step 2: Generate per-signature randomness 𝜌''")
        print("Formula: rnd ← 𝔹32 (for hedged) or {0}32 (for deterministic)")
        print("Formula: 𝜇 ← H(tr‖M'‖rnd, 64)")
        print("Formula: 𝜌'' ← H(K‖𝜇, 64)")
        rnd = secrets.token_bytes(32)  # Hedged version
        mu = self.H(tr + M_prime + rnd, 64)
        rho_double_prime = self.H(K + mu, 64)
        print(f"Code: rnd = random(32); mu = H(tr+M'+rnd); rho_double_prime = H(K+mu)")
        print(f"Value: rnd = {rnd.hex()}")
        print(f"Value: 𝜇 = {mu.hex()}")
        print(f"Value: 𝜌'' = {rho_double_prime.hex()}")
        self.pause()

        # --- Rejection Sampling Loop --- (Alg 7 Lines 8–25)
        print("Step 3: Enter Rejection Sampling Loop (Try until signature is valid)")
        attempts = 0
        while attempts < 100:  # Safety break for demo
            attempts += 1
            print(f"\nAttempt {attempts}:")

            # --- Step 3a: Sample Masking Vector y --- (Alg 7 Line 10)
            print("  Step 3a: Sample masking vector y with small coefficients")
            print(f"  Formula: y ← ExpandMask(𝜌'', κ) (coeffs in [-γ1+1, γ1])")
            raw_int3 = int.from_bytes(rho_double_prime[:8], 'big') + kappa
            seed32_3 = raw_int3 % (2**32)
            np.random.seed(seed32_3)
            y_vec = np.array([self.sample_poly_gamma1()])  # l=1
            np.random.seed()  # Reseed
            kappa += 1  # Increment counter
            print(f"  Code: y_vec = ExpandMask(rho_double_prime, kappa) (Simulated)")
            print(f"  Value: y[0] (first 5 coeffs) = {y_vec[0][:5]}...")

            # --- Step 3b: Compute Commitment w1 --- (Alg 7 Line 11)
            print("  Step 3b: Compute high bits of commitment w1 = HighBits(A·y)")
            print("  Formula: w = A·y (using NTT); w1 ← HighBits(w, 2γ2)")
            w_vec = self.poly_dot(self.A, y_vec)
            w1_vec = self.highbits(w_vec)
            print(f"  Code: w_vec = poly_dot(A, y_vec); w1_vec = highbits(w_vec)")
            print(f"  Value: w[0] (first 5 coeffs) = {w_vec[:5]}...")
            print(f"  Value: w1[0] (first 5 coeffs) = {w1_vec[:5]}...")

            # --- Step 3c: Compute Challenge Hash c̃ --- (Alg 7 Line 13)
            print("  Step 3c: Compute challenge hash c_tilde = H(mu ‖ w1)")
            print("  Formula: c̃ ← H(μ‖Encode(w1), λ/4)")
            c_tilde = self.H(mu + w1_vec.tobytes(), self.lam // 8)
            print(f"  Code: c_tilde = H(mu + w1_vec.tobytes())")
            print(f"  Value: c̃ = {c_tilde.hex()}")

            # --- Step 3d: Sample Challenge Polynomial c --- (Alg 7 Line 14)
            print("  Step 3d: Sample challenge polynomial c from c_tilde")
            print("  Formula: c ← SampleInBall(c̃) (has τ non-zero ±1 coeffs)")
            c_poly = self.sample_in_ball(c_tilde)
            print(f"  Code: c_poly = sample_in_ball(c_tilde)")
            print(f"  Value: c (first 5 coeffs) = {c_poly[:5]}...")

            # --- Step 3e: Compute Response Vector z --- (Alg 7 Line 15)
            print("  Step 3e: Compute response vector z = y + c·s1")
            print("  Formula: z ← y + c·s1")
            cs1 = self.poly_mul(c_poly, s1_vec[0])
            z_vec_poly = self.poly_add(y_vec[0], cs1)
            z_vec = np.array([z_vec_poly])  # l=1
            print(f"  Code: cs1 = poly_mul(c, s1[0]); z_vec = [poly_add(y[0], cs1)]")
            print(f"  Value: z[0] (first 5 coeffs) = {z_vec[0][:5]}...")

            # --- Step 3f: Check Norm Bounds (Rejection) — (Alg 7 Lines 16–19)
            print("  Step 3f: Check rejection bounds on z and LowBits(w – c·s2)")
            print(f"  Formula: ∥z∥∞ < γ1 – β ? (Bound = {self.gamma1 - self.beta})")
            print(f"  Formula: ∥LowBits(w – c·s2, 2γ2)∥∞ < γ2 – β ? (Bound = {self.gamma2 - self.beta})")
            cs2 = self.poly_mul(c_poly, s2_vec[0])
            norm_z_ok = self.check_norm_z(z_vec[0])
            norm_lowbits_ok = self.check_norm_lowbits(w_vec, cs2)
            print(f"  Code: norm_z_ok = check_norm_z(z[0])")
            print(f"  Code: norm_lowbits_ok = check_norm_lowbits(w[0], cs2)")
            print(f"  Result: Check z: {norm_z_ok}, Check LowBits: {norm_lowbits_ok}")

            if norm_z_ok and norm_lowbits_ok:
                print("  Checks PASSED. Proceeding to compute hint.")

                # --- Step 3g: Compute Hint h — (Alg 7 Line 21)
                print("  Step 3g: Compute hint vector h")
                print("  Formula: h = MakeHint(-c·t0, w – c·s2 + c·t0)")
                ct0 = self.poly_mul(c_poly, t0_vec)
                term2 = self.poly_add(self.poly_sub(w_vec, cs2), ct0)
                h_vec = np.array([self.make_hint(self.poly_sub(0, ct0), term2)])
                print(f"  Code: h_vec = [make_hint(...)]")
                print(f"  Value: h[0] (first 5 coeffs) = {h_vec[0][:5]}... (Dummy hint)")

                # --- Step 3h: Check Hint Validity (Rejection) — (Alg 7 Lines 22–23)
                print("  Step 3h: Check hint validity (simplified check – always passes here)")
                print("  Formula: Check ∥h∥₁ ≤ ω and low‐bit consistency.")
                hint_ok = True  # Simplified
                print(f"  Result: Hint OK: {hint_ok}")

                if hint_ok:
                    print("\nSignature components computed successfully!")
                    # --- Step 4: Encode Signature — (Alg 7 Line 24)
                    print("Step 4: Encode signature σ = (c_tilde, z, h)")
                    print("Formula: σ ← sigEncode(c̃, z, h)")
                    self.sigma = (c_tilde, z_vec, h_vec)
                    print(f"Code: self.sigma = (c_tilde, z_vec, h_vec)")
                    print(f"Value: σ = (c̃={self.sigma[0].hex()}, z=..., h=...)")
                    print("\nSigning Complete.")
                    self.pause()
                    return
                else:
                    print("  Hint check FAILED. Retrying loop...")
                    self.pause("Press Enter to retry signing loop…")
            else:
                print("  Norm bounds check FAILED. Retrying loop…")
                self.pause("Press Enter to retry signing loop…")

        print("Error: Signing failed after too many attempts.")

    def run_verify(self):
        if self.pk is None or self.sigma is None:
            print("Error: Key Generation and Signing must be run first.")
            return

        print("\n=== ML-DSA Verification (FIPS 204 Algorithm 3 & 8) ===\n")
        rho, t1_vec = self.pk
        c_tilde, z_vec, h_vec = self.sigma

        # --- Step 1: Decode Keys and Signature --- (Alg 8 Lines 1–3)
        print("Step 1: Decode public key pk and signature σ")
        print("Formula: (ρ, t1) ← pkDecode(pk)")
        print("Formula: (c̃, z, h) ← sigDecode(σ)")
        print(f"Code: rho, t1_vec = self.pk; c_tilde, z_vec, h_vec = self.sigma")
        print(f"Value: ρ = {rho.hex()}")
        print(f"Value: t1 (first 5 coeffs) = {t1_vec[:5]}...")
        print(f"Value: c̃ = {c_tilde.hex()}")
        print(f"Value: z (first 5 coeffs) = {z_vec[0][:5]}...")
        print(f"Value: h (first 5 coeffs) = {h_vec[0][:5]}...")
        self.pause()

        # --- Step 2: Check Norm Bound on z --- (Alg 8 Line 4)
        print("Step 2: Check norm bound on response vector z")
        print(f"Formula: ∥z∥∞ < γ1 - β ? (Bound = {self.gamma1 - self.beta})")
        norm_z_ok = self.check_norm_z(z_vec[0])
        print(f"Code: norm_z_ok = check_norm_z(z[0])")
        print(f"Result: Check z: {norm_z_ok}")
        if not norm_z_ok:
            print("Verification FAILED: z norm check failed.")
            self.pause()
            return False
        self.pause()

        # --- Step 3: Regenerate Matrix A --- (Alg 8 Line 5)
        print("Step 3: Expand ρ to regenerate matrix A (or Â)")
        print("Formula: Â ← ExpandA(ρ)")
        # Deterministically seed from rho[:8], reduced mod 2**32
        raw_int = int.from_bytes(rho[:8], 'big')
        seed32 = raw_int % (2**32)
        np.random.seed(seed32)
        A_recomputed = np.array([[ 
            self.poly_mod(np.random.randint(0, self.q, self.n)) 
        ]])  # k=1, l=1
        np.random.seed()  # Reseed
        print(f"Code: A_recomputed = ExpandA(rho) (Simulated)")
        print(f"Value: A[0,0] (first 5 coeffs) = {A_recomputed[0,0][:5]}...")
        self.pause()

        # --- Step 4: Compute Message Representative μ --- (Alg 8 Line 6)
        print("Step 4: Compute message representative μ")
        print("Formula: pk_bytes ← pkEncode(ρ, t1)")
        print("Formula: tr ← H(pk_bytes, 64)")
        print("Formula: μ ← H(tr‖M', 64)  # M' includes context")
        pk_bytes = rho + t1_vec.tobytes()
        tr = self.H(pk_bytes, 64)
        M_prime = self.message
        mu = self.H(tr + M_prime, 64)
        print(f"Code: mu = H(tr + M')")
        print(f"Value: μ = {mu.hex()}")
        self.pause()

        # --- Step 5: Sample Challenge Polynomial c --- (Alg 8 Line 7)
        print("Step 5: Sample challenge polynomial c from c_tilde")
        print("Formula: c ← SampleInBall(c̃)")
        c_poly = self.sample_in_ball(c_tilde)
        print(f"Code: c_poly = sample_in_ball(c_tilde)")
        print(f"Value: c (first 5 coeffs) = {c_poly[:5]}...")
        self.pause()

        # --- Step 6: Reconstruct Commitment w1′ --- (Alg 8 Line 8)
        print("Step 6: Reconstruct high bits of commitment w1′ using hint h")
        print("Formula: w1′ ← UseHint(h, A·z − c·t1)")
        Az = self.poly_dot(A_recomputed, z_vec)  # A is 1×1, z is 1×1 → poly
        ct1 = self.poly_mul(c_poly, t1_vec)       # c · t1 (each is a length‐n poly)
        term = self.poly_sub(Az, ct1)
        w1_prime_vec = np.array([ self.use_hint(h_vec[0], term) ])
        print(f"Code: w1_prime_vec = [use_hint(h[0], (A·z) − c·t1)]")
        print(f"Value: w1′[0] (first 5 coeffs) = {w1_prime_vec[0][:5]}...")
        self.pause()

        # --- Step 7: Verify Challenge Hash --- (Alg 8 Line 9)
        print("Step 7: Verify if reconstructed challenge hash matches the one in signature")
        print("Formula: c̃ == H(μ‖Encode(w1′), λ/4) ?")
        c_tilde_prime = self.H(mu + w1_prime_vec[0].tobytes(), self.lam // 8)
        print(f"Code: c_tilde_prime = H(mu + w1_prime_vec[0].tobytes())")
        print(f"Value: c̃′ (recomputed) = {c_tilde_prime.hex()}")
        print(f"Value: c̃ (from σ) = {c_tilde.hex()}")

        if c_tilde_prime == c_tilde:
            print("\nVerification PASSED.")
            self.pause()
            return True
        else:
            print("\nVerification FAILED: Challenge hash mismatch.")
            self.pause()
            return False

# --- Main Execution ---
if __name__ == "__main__":
    demo = MLDSA_Educational_Demo()
    demo.run_keygen()
    if demo.sk:
        demo.run_sign()
    if demo.sigma:
        demo.run_verify()
    print("\nEnd of ML-DSA Interactive Educational Demo.")

