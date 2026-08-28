import { createHash } from "node:crypto";
import { verifyMessage } from "viem";

export type ProviderEvidence = {
  schema: "arena-provider-evidence-v1";
  resourceUrl: string;
  requestHash: `0x${string}`;
  responseHash: `0x${string}`;
  issuedAt: number;
  signer: `0x${string}`;
  signature: `0x${string}`;
};

export function sha256Hex(s: string): `0x${string}` {
  return `0x${createHash("sha256").update(s).digest("hex")}`;
}

export function evidenceMessage(e: Omit<ProviderEvidence,"signature">): string {
  return [e.schema,e.resourceUrl,e.requestHash,e.responseHash,String(e.issuedAt),e.signer.toLowerCase()].join("|");
}

export async function verifyProviderEvidence(e: ProviderEvidence): Promise<boolean> {
  const {signature,...unsigned}=e;
  return verifyMessage({address:e.signer,message:evidenceMessage(unsigned),signature});
}
