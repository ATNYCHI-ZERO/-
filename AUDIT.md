# DARPA Audit Verification

## Repository Overview
- Total auditable files discovered via `python darpa_audit.py`: **26** (source, docs, and white-paper artifacts).
- Key directories:
  - `docs/` — source white paper (`recursive_identity_white_paper.md`).
  - `tests/` — pytest suite validating the audit helper and documentation headers.
  - Root-level research dossiers (`README.md`, `UNIFIED_BLOCK.txt`, "Unified AI Framework Requested_", etc.).
- Executable assets:
  - `darpa_audit.py` — SHA-256 enumerator used for the DARPA sweep.
  - `audit_check.py` — JSON-emitting integrity scanner.

## File Coverage Results
- `python darpa_audit.py` emits a digest entry for every repository artifact, including large research PDFs/archives.
- Example entries:
  - `README.md` — 218,060 bytes — `SHA256=9d14ac0354e01027ebaaef4bb7f7f81f2cb2b5006c19c53405db6f753ffa54bd`.
  - `docs/recursive_identity_white_paper.md` — 4,746 bytes — `SHA256=859dce45adef408b0675b8b55832b05c67bcfda8dae67f5a7ffa8724e903b89a`.
  - `tests/test_darpa_audit.py` — 539 bytes — `SHA256=cce4e4b5697f338f069b224b5d4872afca5e7f4277cdb4ed03927f7870584576` (full listing available in the generated report).
- All files were readable; no permission or encoding faults were observed.

## Testing Status
- `python darpa_audit.py` — **PASS** (produced deterministic digest list for all assets).
- `pytest -q` — **PASS** (3 tests):
  - Ensures `collect_file_audit_records` discovers `README.md` with valid size/hash metadata.
  - Confirms documentation headers remain intact for `README.md` and `docs/recursive_identity_white_paper.md`.

## Notes
- Generated audit data and pytest logs should be archived with the DARPA submission to preserve chain-of-custody.
- Future audits can optionally invoke `audit_check.py` to capture a JSON snapshot suitable for ledger anchoring.
