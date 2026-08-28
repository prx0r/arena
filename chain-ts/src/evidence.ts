import { createHash } from "node:crypto";

export type ArenaEvidenceEnvelope = {
  schema: "arena-evidence-v1";
  resourceUrl: string;
  payer: string;
  providerId: string;
  requestHash: `0x${string}`;
  responseHash: `0x${string}`;
  receipt: unknown;
  transaction?: string;
  observedAt: string;
};

export function sha256Hex(data: Uint8Array | string): `0x${string}` {
  return `0x${createHash("sha256").update(data).digest("hex")}`;
}

export function bindEvidence(args: Omit<ArenaEvidenceEnvelope, "schema"|"requestHash"|"responseHash"|"observedAt"> & {requestBody: string; responseBody: string}): ArenaEvidenceEnvelope {
  return {
    schema: "arena-evidence-v1",
    resourceUrl: args.resourceUrl,
    payer: args.payer,
    providerId: args.providerId,
    requestHash: sha256Hex(args.requestBody),
    responseHash: sha256Hex(args.responseBody),
    receipt: args.receipt,
    transaction: args.transaction,
    observedAt: new Date().toISOString(),
  };
}
