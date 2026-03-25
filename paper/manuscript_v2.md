---
title: |
  Incompleteness-Secured Commitments:
  a Dual-Layer Post-Quantum Framework with Reproducibility Guards,
  Wrapper Portability Probes, and an ML-KEM-768 Reference Prototype
author:
  - Kevin Henry Miller
  - Q-Bond Network DeSCI DAO, LLC
  - kevin@qbondnetwork.com
date: March 2026
fontsize: 11pt
geometry: margin=1in
...

# Abstract

We describe a commitment framework that combines an ordinary post-quantum cryptographic body with a proof-carrying logical annotation layer. The cryptographic body is built around ML-KEM-768 as a key-encapsulation mechanism plus a one-bit masking layer and a transcript hash. The logical layer attaches a canonical arithmetic formula encoding the opening relation and uses Gödel numbering only to define a proof-carrying meta-security game; it does not replace ordinary computational security reductions. In this formulation, hiding and binding remain conventional and are argued at the concrete cryptographic layer, while the additional claim is narrower: a successful *certified* double opening must also be accompanied by a formal proof inside a fixed theory that both openings verify. Under standard representability assumptions, such a certified attack would amount to a proof of a false arithmetic statement whenever the concrete cryptographic layer has not already failed.

The paper is deliberately conservative. It does not claim information-theoretic security, production readiness, constant-time behavior for the Python orchestration layer, or a complete IND-CPA, IND-CCA, or UC proof of the full construction. Instead, it focuses on three practical deliverables: a research-based manuscript, a public reference repository, and measured reproducibility artifacts. We report an archived last-good baseline line, a second archived continuity line, a current environment rerun on the legacy ML-KEM alpha route, and a wrapper-portability audit for keeper-ML-KEM and libfips203 skeleton adapters. The result is a clearer separation between what has been formalized, what has been implemented, and what remains future work.

# 1. Introduction

Modern post-quantum cryptography is built on computational assumptions, and that is the correct baseline. The natural question explored here is not whether Gödel's incompleteness theorem can magically strengthen ciphertexts by itself, but whether a *proof-carrying* variant of a standard commitment system can cleanly separate two layers of failure. The first layer is conventional cryptographic failure: for example, a hiding or binding break under an implementation or assumption-level attack. The second layer is logical certification of that failure: an adversary not only outputs two openings to the same commitment, but also outputs a formal derivation inside a fixed theory certifying that both openings verify.

That second requirement is where incompleteness enters. The verifier for the commitment is decidable. Therefore the statement “this commitment admits two distinct valid openings” can be represented in arithmetic. If the concrete cryptographic layer is still behaving as intended, then the represented sentence is false. A proof-carrying adversary is therefore trying to package a cryptographic event together with a formal proof of a false statement. The point of the framework is not to replace standard cryptographic analysis. The point is to isolate a narrow and explicit interface between conventional cryptography and proof theory.

# 2. Contributions and scope discipline

The paper makes six bounded contributions.

1. It defines a dual-layer commitment framework in which the concrete commitment body is standard and the logical layer is explicitly meta-security only.
2. It states a proof-carrying adversary model and a corresponding notion of certified double-opening failure.
3. It implements a reference commitment prototype using ML-KEM-768 as a *key-encapsulation mechanism*, not as an improvised public-key encryption primitive.
4. It publishes a public repository with scripts for backend probing, smoke tests, proof-bundle checks, benchmark runs, and a manuscript claim guard.
5. It records archived benchmark lines for continuity and adds a current rerun line from the present workspace.
6. It performs a wrapper portability audit for keeper-ML-KEM and libfips203 skeleton adapters and records the exact observed failure modes.

# 3. Model and construction

## 3.1 Concrete commitment body

The reference commitment body is

$$
B=(ct_{\mathsf{kem}}, d, 
ho),
$$

where $ct_{\mathsf{kem}}$ is an ML-KEM-768 ciphertext, $
ho$ is a 32-byte public nonce, and $d\in\{0,1\}$ is a masked bit carried on the wire as one byte. The full commitment is then

$$
C=(B,c_G),
$$

where $c_G$ is a SHA3-256 transcript hash over a canonical Gödel-encoded arithmetic statement and the opening randomness.

Operationally, the prototype proceeds as follows.

1. Generate an ML-KEM-768 keypair $(pk,sk)$.
2. Run $\mathsf{Encaps}(pk)$ to obtain a shared secret $ss$ and a KEM ciphertext $ct_{\mathsf{kem}}$.
3. Derive a public nonce $
ho$ from explicit randomness and the ciphertext.
4. Derive a one-bit mask from $(ss,
ho)$ and publish the masked bit $d=m\oplus b$.
5. Build a canonical arithmetic formula $\phi$ describing the opening relation for the current transcript.
6. Gödel-encode $\phi$ and compute
   $$
   c_G = \mathrm{SHA3	ext{-}256}(\mathrm{enc}(\phi)\parallel B\parallel r).
   $$
7. Publish $C=(B,c_G)$ and retain the opening witness $w=(m,r,\phi)$.

Opening uses decapsulation to recompute the mask and recover the bit. Verification is public and checks that the canonical formula recomputed from $(B,m,r)$ matches the supplied formula and that the transcript digest recomputes exactly.

## 3.2 What remains standard

The cryptographic layer remains conventional. Hiding depends on the encapsulation-and-mask path. Binding depends on the transcript hash, the canonicalization routine, and the underlying backend behaving consistently. Nothing in the paper claims that incompleteness upgrades these ordinary guarantees into unconditional security. The construction remains a normal cryptographic object with a secondary logical game attached to it.

## 3.3 Proof-carrying adversary model

Let $\mathsf{Bad}(C,w_0,w_1)$ denote the arithmetic sentence stating that commitment $C$ admits two distinct valid openings $w_0$ and $w_1$. A proof-carrying adversary succeeds only if it outputs not merely the commitment and two openings, but also a derivation $\pi$ in a fixed theory $T$ that certifies $\mathsf{Bad}(C,w_0,w_1)$.

The role of Gödel numbering here is narrow. It is a bridge from the verification relation into arithmetic syntax so that the proof-carrying game is well-defined. It is not a claim that every practical attack on the implementation must route through theorem proving. The only added security statement is about a stronger attacker model that wants a certified break.

# 4. Informal security discussion

The concrete hiding story is the familiar one: before opening, an observer sees a KEM ciphertext, a nonce, a one-byte masked bit, and a transcript digest. If the shared secret derived by encapsulation remains hidden and the one-bit mask is derived from that secret and the public nonce, then the published masked bit does not reveal the committed bit. The concrete binding story is equally familiar: two successful openings for the same commitment should either indicate a collision in the transcript hash or a defect in the canonicalization routine or backend behavior.

The meta-security statement is weaker and more specialized. If the concrete layer has not already failed, then a sentence asserting the existence of a valid double opening is false. A consistent and sufficiently expressive theory should therefore not prove it. In that sense, incompleteness does not make the commitment body cryptographically stronger by itself; it makes *certified falsehood* harder in the proof-carrying game.

This distinction is worth repeating because it prevents the common failure mode of overstatement. The scheme is not above all computation-based systems in the ordinary cryptographic sense. It is a standard post-quantum commitment architecture with an additional, logically flavored certificate layer.

# 5. Reference implementation

## 5.1 Why the implementation path matters

The current reference implementation uses ML-KEM-768 in the way the standard intends: as a *key-encapsulation mechanism*. The paper therefore avoids descriptions such as “encrypt a bit with Kyber.” Instead, the bit is masked using material derived from the shared secret, and the commitment transcript is bound by a SHA3-256 digest.

## 5.2 Wire format

The current wire format is shown below.

| Component | Size | Comment |
|---|---:|---|
| ML-KEM-768 ciphertext | 1088 B | KEM ciphertext |
| Public nonce $
ho$ | 32 B | nonce derived from randomness and ciphertext |
| Masked bit $d$ | 1 B | one-byte wire encoding |
| Transcript digest $c_G$ | 32 B | SHA3-256 over canonical statement and opening data |
| **Total** | **1153 B** | current commitment size |

## 5.3 Public repository contents

The public repository accompanying this paper includes the following items.

- `src/gce/engine.py`: commit, verify, and open logic.
- `src/gce/kem_backends.py`: backend selectors for keeper-style, legacy-alpha, libfips203, and simulated lanes.
- `src/gce/kem_wrappers/keeper_mlkem_wrapper.py`: skeleton adapter for a Keeper-style ML-KEM package.
- `src/gce/kem_wrappers/libfips203_wrapper.py`: skeleton adapter for Python `fips203` / `libfips203` style bindings.
- `scripts/00_backend_probe.py`: report backend metadata and wire-format sizes.
- `scripts/01_smoke_test.py`: minimal round-trip check.
- `scripts/02_proof_bundle.py`: round-trip, wrong-opening rejection, tamper-detection, and Gödel-number uniqueness checks.
- `scripts/03_benchmark.py`: timing benchmark.
- `scripts/04_cross_backend_validate.py`: compare multiple backend lanes.
- `scripts/05_probe_wrapper_status.py`: probe the skeleton wrappers and record exact availability or failure modes.
- `scripts/check_claims.py`: fail if banned phrases or missing disclaimer language appear in the manuscript.

# 6. Measured results

## 6.1 Archived continuity lines

The paper preserves two archived measurement lines because the user requested that continuity record explicitly. Those lines describe prior local validated runs at the same 1153-byte commitment size.

| Archived line | Keygen ms | Commit ms | Verify ms | Open ms | Size B |
|---|---:|---:|---:|---:|---:|
| Archived last-good baseline | 0.566 | 0.861 | 0.023 | 0.902 | 1153 |
| Archived second continuity line | 0.580 | 0.870 | 0.025 | 0.910 | 1153 |

These are retained as provenance and continuity data, not as newly rerun measurements from the present workspace.

## 6.2 Current workspace rerun

The current workspace rerun is different. In this environment, the legacy ML-KEM alpha path remains runnable and produced the following benchmark line over 20 trials.

| Current rerun backend | Trials | Keygen ms | Commit ms | Verify ms | Open ms | Size B |
|---|---:|---:|---:|---:|---:|---:|
| Legacy ML-KEM alpha route | 20 | 0.407 | 0.627 | 0.018 | 0.658 | 1153 |

The corresponding smoke and proof-bundle results were all successful in the current rerun: verify `true`, opened bit `1`, round trip `20/20`, wrong opening rejected `20/20`, tamper detected `20/20`, and Gödel-number uniqueness `20/20 unique`.

## 6.3 Archived keeper-backed line

The repository also preserves an earlier keeper-backed benchmark artifact from a previous environment. That archived line reported 30-trial timings of 0.302 ms key generation, 0.452 ms commit, 0.011 ms verify, and 0.489 ms open at the same 1153-byte wire format. We keep that line because it supports the paper’s implementation narrative, but we do *not* relabel it as a new rerun from the present workspace.

# 7. Wrapper portability audit

A major change from previous drafts is that the wrapper story is written down honestly. Instead of simply saying that keeper-ML-KEM and libfips203 skeleton wrappers exist, the repository now includes dedicated wrapper skeleton files and a probe script that records what happened when they were exercised in the current environment.

| Wrapper probe | Current status | Observed result |
|---|---|---|
| `keeper_mlkem_skeleton` | unavailable | the installed `mlkem` package in this workspace does not export `ML_KEM` and `MLKEM_768_PARAMETERS` at the expected top level |
| `libfips203_skeleton` | unavailable | the Python package `fips203` is not installed in the current workspace |

.
# 8. Reproducibility safeguards

The repository is intended to be uploadable as a public GitHub project rather than as an internal scratch directory. To support that use case, the paper and repository now include the following reproducibility safeguards.

First, the benchmark and probe results are stored as JSON rather than only as prose. Second, the claim-guard script checks for both banned phrases and missing disclaimer language. The script fails the build if unsupported deployment language or off-scope positioning language is reintroduced. Third, a minimal GitHub Actions workflow is included so that basic checks run automatically on push. Fourth, the manuscript and repository both keep the same sharp distinction between archived continuity lines and current reruns.

# 9. Relation to the broader research corpus

The broader uploaded corpus includes substantial material on TICE qubits, Floquet codes, dynamical decoupling, κ-meter metrology, and information-curvature frameworks. Some of those materials contain code-heavy implementations and patent-style descriptions of quantum-control architectures, stabilizer logic, and metrology devices. That larger corpus is valuable project context, but it is intentionally kept out of the theorem statements and benchmark claims of this cryptography paper.

The reason is methodological. A cryptography manuscript becomes weaker, not stronger, if it mixes concrete implementation claims with speculative adjacent claims about cosmology, symbolic gravity, or generalized information-curvature physics. The current paper therefore uses the broader corpus only in the narrow sense that it reinforced the importance of code packaging, explicit scripts, and reproducibility artifacts. The security claims in this paper do not depend on the TICE or κ-meter frameworks.

# 10. Limitations and future work

This project remains a reference prototype.

We do not claim production readiness.
We do not claim constant-time behavior for the Python orchestration layer.

1. **No production-readiness claim.** The code is packaged for public review and reproducibility, not deployment.
2. **No constant-time claim for Python glue.** Secret-dependent work should remain delegated to native or hybrid cryptographic backends; the Python layer should be treated as orchestration only.
3. **No complete computational proof yet.** The manuscript still does not provide a full IND-CPA, IND-CCA, or UC proof for the complete construction.
4. **Canonicalization remains part of the security surface.** If two semantically identical opening relations can be encoded in materially different ways, the neat transcript-hash argument weakens.
5. **Wrapper maturity is incomplete.** The keeper-style and libfips203 wrapper skeletons are useful, but the present environment probe shows that neither is turnkey in this workspace.
6. **Archived lines are not present reruns.** The continuity lines are preserved because they were explicitly requested, but they must not be confused with measurements produced by the current rerun environment.

# 11. Conclusion

This is Q-Bond Network's public repository that reflects the paper, archived continuity lines preserved without being relabeled, a current workspace rerun line, and explicit wrapper-portability probe results. The cryptographic body remains ordinary and post-quantum. The incompleteness component remains a meta-security layer for proof-carrying adversaries only. That separation is the main intellectual contribution of the paper, and the reproducibility tooling is the main practical contribution.

# 12. Artifact inventory and workflow

| Script | Purpose | Primary output |
|---|---|---|
| `00_backend_probe.py` | inspect backend metadata and wire-format sizing | `backend_probe_<backend>.json` |
| `01_smoke_test.py` | minimal end-to-end commit/verify/open check | `smoke_<backend>.json` |
| `02_proof_bundle.py` | round-trip and tamper tests | `proof_<backend>.json` |
| `03_benchmark.py` | timing measurements | `benchmark_<backend>.json` |
| `04_cross_backend_validate.py` | multi-backend matrix run | `cross_backend_validation.json` |
| `05_probe_wrapper_status.py` | keeper/libfips203 skeleton-wrapper audit | `wrapper_probe_bundle.json` |
| `check_claims.py` | manuscript language guard | process exit code and console report |


# 13. Threats to validity

Three threats to validity deserve explicit attention.

First, backend availability is environment-sensitive. The current workspace can execute the legacy alpha route but not the keeper-style or libfips203 skeleton wrappers. That does not falsify the architecture, but it does mean that portability claims must be kept narrow. A future reader should treat the wrapper section as a precise environment report, not as a universal statement about those packages.

Second, microbenchmarks are fragile. Numbers in the sub-millisecond range depend on interpreter version, CPU state, package build options, and whether a fast path or pure-Python path was selected. For that reason, the paper does not claim that 0.401 ms or 0.566 ms is the uniquely correct key-generation number. It claims only that those lines were observed in the stated artifact trail and that the 1153-byte wire format remained stable across them.

Third, proof-carrying language can easily be misunderstood. Readers may overread the term “Gödel-hardness” and assume it means a new unconditional cryptographic hardness class. That is not what is being claimed. The paper uses the term only for the certified-adversary game in which the attacker is required to provide a formal proof of the bad event. Outside that game, the scheme lives or dies by ordinary post-quantum cryptographic reasoning.

# References

1. Kurt Gödel, *Über formal unentscheidbare Sätze der Principia Mathematica und verwandter Systeme I*, 1931.
2. A. M. Turing, *On Computable Numbers, with an Application to the Entscheidungsproblem*, 1936.
3. National Institute of Standards and Technology, *FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism Standard*, 2024.
4. Joppe Bos et al., *CRYSTALS-Kyber Algorithm Specifications and Supporting Documentation*, 2021.
5. Public repository artifacts bundled with this manuscript: benchmark JSONs, wrapper-probe JSONs, and claim-guard script.
