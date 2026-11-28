"""Compare a frozen documentary sample to archived sources, no network and no merges."""
import argparse,collections,hashlib,json,pathlib,zipfile
from audit_sill_wikidata import normalized,make_index,matches
P=pathlib.Path(__file__).resolve().parent
def readzip(path,name,expected):
    b=path.read_bytes()
    if hashlib.sha256(b).hexdigest()!=expected:raise ValueError("Archive digest mismatch")
    with zipfile.ZipFile(path) as z:
        if z.testzip():raise ValueError("Archive corrupt")
        return json.loads(z.read(name))
def main():
    a=argparse.ArgumentParser();a.add_argument("--catalog",type=pathlib.Path,required=True);a.add_argument("--output",type=pathlib.Path,required=True);x=a.parse_args()
    b=x.catalog.read_bytes();blob=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\x00"+b).hexdigest()
    if blob!="39b32ebbdf33b49a3fb0bb669f8a0809d0e72995":raise ValueError("Catalog mismatch")
    obj=json.loads(b);c=obj if isinstance(obj,list) else next(v for v in obj.values() if isinstance(v,list) and len(v)==2466 and all(isinstance(i,dict) and "name" in i for i in v))
    if len(c)!=2466 or len({str(r["id"]) for r in c})!=2466:raise ValueError("Catalog count")
    base=P/"evidence/2026-11-28"
    sill=readzip(base/"sill.zip","sill_product_inventory.json","8bb73ecd9d326547bd93a1db570ab37501a5fec25cba61cc10005ba610f7bc27")
    wd=readzip(base/"wikidata.zip","inventory.json","e33bbf0775eabb94329b1d53211397ce3047ff41524b17d997a97821d6dd3c46")
    if len(sill)!=672 or len(wd)!=547:raise ValueError("Source count")
    ix={"catalog":make_index(c,"id","name",True),"sill":make_index(sill,"sill_id","names"),"wikidata":collections.defaultdict(set)}
    for r in wd:
        for label in r["labels"].values():
            if normalized(label):ix["wikidata"][normalized(label)].add(r["qid"])
    sample=json.loads((P/"PROSPECTION_MATERIEL_COMMERCIAL_V01.json").read_text())["records"]
    if len({r["id"] for r in sample})!=len(sample):raise ValueError("Duplicate witness")
    result=[]
    for r in sample:
        found={k:sorted(matches(r["alias_probes"],v)) for k,v in ix.items()}
        result.append({"id":r["id"],"name":r["name"],"axis":r["axis"],"unit":r["unit"],"candidates":found,"eligibility":"NOT_ASSESSED"})
    out={"rows":result,"count":len(result),"by_axis":dict(collections.Counter(r["axis"] for r in sample)),"by_unit":dict(collections.Counter(r["unit"] for r in sample)),"with_name_candidates":{k:sum(bool(r["candidates"][k]) for r in result) for k in ix},"without_any_name_candidate":sum(not any(r["candidates"].values()) for r in result),"note":"Name probes include family/component/variant names; not proof of same entity or new product. Purposive sample not recall estimation."}
    x.output.mkdir(parents=True,exist_ok=True);(x.output/"report.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("DOC_PILOT "+json.dumps(out,ensure_ascii=False,separators=(",",":")))
if __name__=="__main__":main()
