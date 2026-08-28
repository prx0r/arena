from arena402.models import Provider, Observation
from arena402.store import Store
import time

s=Store("arena402-demo.sqlite")
providers=[
    Provider("search-big","PopularSearch","https://example.invalid/big",0.012,"search"),
    Provider("search-new","NewSearch","https://example.invalid/new",0.003,"search"),
    Provider("search-mid","MidSearch","https://example.invalid/mid",0.006,"search"),
]
for p in providers: s.add_provider(p)
rows=[
("find Python library API docs for version 1.4","search-new","Returned exact versioned documentation and examples",0.003,650,0.95),
("research current election news with multiple sources","search-big","Returned current source-rich news synthesis",0.012,1200,0.97),
("find GitHub issue explaining obscure Python bug","search-new","Found repository issue and patch discussion",0.003,700,0.96),
("look up company funding and investors","search-mid","Returned structured company funding table",0.006,800,0.88),
("find latest breaking news","search-big","Returned fresh multi-source news",0.012,1100,0.94),
]
for q,p,out,c,l,qual in rows:
    s.add_observation(Observation(q,p,out,c,l,qual,True,"search",time.time()-86400,source="demo",public_example=True))
s.fund_provider("search-new",25.0)
print("seeded arena402-demo.sqlite")
