import "dotenv/config";
import express from "express";
import { paymentMiddleware, x402ResourceServer } from "@x402/express";
import { HTTPFacilitatorClient } from "@x402/core/server";
import { ExactEvmScheme } from "@x402/evm/exact/server";
import { createOfferReceiptExtension, createEIP712OfferReceiptIssuer, declareOfferReceiptExtension } from "@x402/extensions/offer-receipt";
import { privateKeyToAccount } from "viem/accounts";
import { BASE_SEPOLIA } from "./config.js";
import { evidenceMessage, sha256Hex, type ProviderEvidence } from "./providerEvidence.js";

const payTo = process.env.SELLER_PAYMENT_ADDRESS as `0x${string}`;
const signingPk = process.env.SELLER_SIGNING_PRIVATE_KEY as `0x${string}`;
if (!payTo || !signingPk) throw new Error("SELLER_PAYMENT_ADDRESS and SELLER_SIGNING_PRIVATE_KEY required");
const signing = privateKeyToAccount(signingPk);
const kid = `did:pkh:eip155:1:${signing.address}#key-1`;
const issuer = createEIP712OfferReceiptIssuer(kid, signing.signTypedData.bind(signing));
const facilitator = new HTTPFacilitatorClient({url:process.env.FACILITATOR_URL ?? "https://x402.org/facilitator"});
const resourceServer = new x402ResourceServer(facilitator)
  .register(BASE_SEPOLIA.network, new ExactEvmScheme())
  .registerExtension(createOfferReceiptExtension(issuer));

const app=express(); app.use(express.json());
app.use(paymentMiddleware({
  "POST /api/search": {
    accepts:[{scheme:"exact",price:"$0.001",network:BASE_SEPOLIA.network,payTo}],
    description:"402Arena deterministic Sepolia witness provider",
    mimeType:"application/json",
    extensions:{...declareOfferReceiptExtension({includeTxHash:true})},
  },
}, resourceServer));

app.post("/api/search", async (req,res)=>{
  const resourceUrl=`${req.protocol}://${req.get("host")}${req.originalUrl}`;
  const requestBody=JSON.stringify(req.body ?? {});
  const responseObject={ok:true,query:req.body?.query ?? "",result:"deterministic-test-output-v1"};
  const responseBody=JSON.stringify(responseObject);
  const unsigned: Omit<ProviderEvidence,"signature">={
    schema:"arena-provider-evidence-v1",resourceUrl,
    requestHash:sha256Hex(requestBody),responseHash:sha256Hex(responseBody),
    issuedAt:Math.floor(Date.now()/1000),signer:signing.address,
  };
  const signature=await signing.signMessage({message:evidenceMessage(unsigned)});
  res.json({...responseObject,arenaEvidence:{...unsigned,signature}});
});
app.listen(4021,()=>console.log("seller listening on :4021"));
