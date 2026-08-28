"""Reference Cogym worldpack adapter.

This file is deliberately minimal because the exact WorldSpec/ActionSpec API in
prx0r/cg is still evolving. The stable experiment implementation lives in
arena402.replay; this adapter is the seam to wire into the local Cogym runner.
"""
from arena402.cogym import worldpack_manifest

MANIFEST = worldpack_manifest()
