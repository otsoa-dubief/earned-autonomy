# Draw log (public calibration / confirmation split)

- Verdict-freeze registration: OSF cusv6, `date_registered` 2026-11-14T08:17:47.424176 UTC (replaces u26kr, withdrawn).
- Designated time (72 hours later): 2026-11-17T08:17:47.424Z.
- Source: NIST Randomness Beacon 2.0, pulse 2031457 (https://beacon.nist.gov/beacon/2.0/chain/2/pulse/2031457), pulse time 2026-11-17T08:18:00.000Z.
- Pulse value: `a0ef4db21df16d7774f1b76d551f19b885b2e8f2889f168d5970b5371212ba82f7f72395ee1dfd044f59ecea46a1a80c2b0ffee3dbaef0028f5571299a1c5e31`.
- Manifest of the frozen verdicts: SHA-256 `904aa8d3829b890c147d548718fe3ae78cd088b9f4402b3af1d2aff3487ff88d`.
- Seed: `3cf2e0cad83a247cc2e94eacdcdd0f85c854103bbc7b90f8089db6fdf5f27f36`; reserve hash `303b96ac5baae8a5a8ef54a341c3d4628e188821a8495c87cd1b274b5264b290`; pairs hash `053e091b1c2c7851fffef85bac16ebbc5a5f9b6d2b2d2d668fddd75327f6f27f`.
- Draw script: `banc/tirage/tirage_public.py`, SHA-256 `6970dfd932490b6d2af6c1aac4229266cdd27c4f9162ea43831a567702efe027` (frozen; the rule is in the pre-registered plan, section 3.4, and in the README of the verdict-freeze registration cusv6; `banc/tirage/TIRAGE.md` describes the earlier development-set draw).
- `draw/impulsion.json` SHA-256 `fa61235b121577a3002a39c5971ee3dc42b7534da1220c2a823f83f69c3028b6`; `draw/partage.json` SHA-256 `76e04fca20140515f11e920efce9eb0a1af537a0e8fa51c6b2f22faacd460f3f`.
- Draw run: recorded by commit ee0df60 (17 November 2026, 10:19:09 +01:00), after the designated time.
- Final replay outputs: see `SHA256SUMS.txt` of this package (authoritative); `SHA256_sorties_finales.txt` is the earlier list written at 13:28 the same day (see README).
- Inputs needed to redo the draw are copied in `draw/frozen_inputs/` (manifest, script, pairs, reserve). From the project repository:
  `python3 banc/tirage/tirage_public.py verifier --dossier experience/tirage --manifeste experience/manifeste_verdicts.txt --en-ligne`
  (answer on 17 November 2026: "tirage vérifié").
