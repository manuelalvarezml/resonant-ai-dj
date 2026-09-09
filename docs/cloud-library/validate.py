"""Validate discovery artifacts. Reads no audio and uses no network."""
import json, re, hashlib, zipfile, xml.etree.ElementTree as ET
from pathlib import Path
from math import isclose
ROOT = Path(__file__).resolve().parent
def read(name):
    return json.loads((ROOT/name).read_text())
reg=read("registers.json")
src=read("sources.json")
inputs=read("economics/inputs.json")
calc=read("economics/calculated.json")
events=[json.loads(x) for x in (ROOT/"events.jsonl").read_text().splitlines() if x.strip()]
errors=[]
collections=["gates","questions","risks","paths","decisions","experiments","tasks","failures"]
ids=[x["id"] for k in collections for x in reg[k]]
assert len(ids)==len(set(ids)), "Duplicate register IDs"
idset=set(ids)
sourceids={x["id"] for x in src["sources"]}
assert len(sourceids)==len(src["sources"])
for k in ["gates","tasks"]:
    for x in reg[k]:
        for d in x.get("dependencies",[]):
            if d not in idset: errors.append(f'{x["id"]}: missing dependency {d}')
for k in ["tasks","risks","paths","experiments"]:
    for x in reg[k]:
        for g in x.get("gates", [x["gate"]] if "gate" in x else []):
            if g not in idset: errors.append(f'{x["id"]}: missing gate {g}')
graph={x["id"]:x.get("dependencies",[]) for k in ["gates","tasks"] for x in reg[k]}
def visit(n,trail):
    if n in trail: errors.append("Dependency cycle "+str(trail+[n])); return
    for d in graph.get(n,[]): visit(d,trail+[n])
for n in graph: visit(n,[])
assert len({e["event_id"] for e in events})==len(events), "Duplicate event ID"
for e in events:
    for i in e["target_ids"]:
        if i not in idset: errors.append(f'Missing event target {i}')
for g in reg["gates"]:
    if g["status"]=="passed": errors.append("Unexpected passed empirical gate: "+g["id"])
for e in reg["experiments"]:
    if e["status"]!="not_run" or e["results"] is not None: errors.append("Unexpected experiment result")
links=0
for path in ROOT.glob("*.md"):
    txt=path.read_text()
    for dest in re.findall(r"\[[^\]]+\]\(([^)]+)\)",txt):
        if dest.startswith(("http://","https://","#","mailto:")): continue
        rel=dest.split("#")[0].strip("<>")
        if not rel: continue
        links+=1
        if not (path.parent/rel).exists(): errors.append(f"{path.name}: broken link {dest}")
    for sid in set(re.findall(r"\bS\d{3}\b",txt)):
        if sid not in sourceids: errors.append(f"{path.name}: missing source {sid}")
a={x[0]:x[2] for x in inputs["assumptions"]}
independent=[]
for i,name in enumerate(inputs["cases"]):
    d={x[0]:x[3][i] for x in inputs["drivers"]}
    n=d["users"]; original=n*d["original_gb"]
    stored=original*(1+a["derivative_ratio"])+n*d["mixes"]*(a["mix_gb"]+a["master_gb"])
    outbound=n*d["listening_hours"]*a["audio_gb_hour"]+n*d["mixes"]*a["mix_gb"]+original*(a["worker_read_ratio"]+a["export_ratio"])
    r2=stored*a["r2_storage"]+n*(a["class_a"]*a["r2_a"]+a["class_b"]*a["r2_b"])/1e6
    b2=stored*a["b2_storage"]+max(outbound-stored*a["b2_allowance"],0)*a["b2_egress"]
    spaces=a["spaces_base"]+max(stored/1.073741824-a["spaces_storage_allow"],0)*a["spaces_storage"]+max(outbound/1.073741824-a["spaces_transfer_allow"],0)*a["spaces_egress"]
    supa=a["supabase_base"]+max(stored-a["supabase_storage_allow"],0)*a["supabase_storage"]+max(outbound*a["supabase_hit"]-a["supabase_transfer_allow"],0)*a["supabase_cached"]+max(outbound*(1-a["supabase_hit"])-a["supabase_transfer_allow"],0)*a["supabase_uncached"]
    wasabi=max(stored/1099.511627776,1)*a["wasabi_base"]
    backup=original*a["backup_ratio"]*a["b2_storage"]
    analysis=n*d["new_tracks"]*a["analysis_minutes"]/60*a["worker_rate"]*a["retry_factor"]
    render=n*d["mixes"]*a["render_minutes"]/60*a["worker_rate"]*a["retry_factor"]
    workerout=n*(d["new_tracks"]*(d["original_gb"]/d["initial_tracks"])*a["derivative_ratio"]+d["mixes"]*(a["mix_gb"]+a["master_gb"]))*a["worker_egress_rate"]
    llm=n*a["calls"]*(a["input_tokens"]*a["input_rate"]+a["output_tokens"]*a["output_rate"])/1e6
    support=n*a["support_minutes"]/60*a["support_rate"]
    recurring=sum([b2,backup,analysis,render,workerout,llm,support])*(1+a["contingency"])+a["fixed_ops"]
    rev=n*d["price"]; payment=rev*a["payment_pct"]+n*a["payment_fixed"]
    contribution=rev-recurring-payment
    initial=n*d["initial_tracks"]*a["analysis_minutes"]/60*a["worker_rate"]*a["retry_factor"]
    allocated=(initial+n*a["acquisition"])/a["retained_months"]
    expected={11:stored,15:outbound,19:r2,20:b2,21:spaces,22:supa,23:wasabi,39:recurring,42:contribution,45:initial,48:contribution-allocated}
    snapshot=calc["snapshots"][i]["model_values"]
    for r,v in expected.items():
        actual=snapshot[r-8][1]
        if not isclose(actual,v,rel_tol=1e-10,abs_tol=1e-8): errors.append(f"{name} row {r}: {actual} != {v}")
    independent.append({"case":name,"checked_rows":list(expected),"recurring_contribution":contribution,"after_initial_allocation":contribution-allocated})
ns={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
book=ROOT/"economics/UNIT_ECONOMICS.xlsx"
with zipfile.ZipFile(book) as z:
    all_sheets=[n for n in z.namelist() if re.fullmatch(r"xl/worksheets/sheet\d+\.xml",n)]
    formulas=sum(len(ET.fromstring(z.read(n)).findall(".//m:f",ns)) for n in all_sheets)
    sheet=ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    cells={c.attrib["r"]:c for c in sheet.findall(".//m:c",ns)}
    for addr in ["B11","B20","B39","B42","B45","B48"]:
        c=cells[addr]
        assert c.find("m:f",ns) is not None, f"Formula lost: {addr}"
        cached=c.find("m:v",ns)
        if cached is None: errors.append("Missing saved cached value "+addr)
        elif not isclose(float(cached.text),calc["snapshots"][1]["model_values"][int(addr[1:])-8][1],rel_tol=1e-9):
            errors.append("Wrong saved value "+addr)
    workbook_sheets=len(ET.fromstring(z.read("xl/workbook.xml")).findall(".//m:sheet",ns))
checks={"date":"2026-09-08","scope":"documents, registers and cost workbook only","source_count":len(sourceids),
"record_counts":{k:len(reg[k]) for k in collections},"events":len(events),"relative_links_checked":links,
"dependency_cycles":False,"independent_arithmetic":independent,"saved_workbook":{"sheets":workbook_sheets,"formulas":formulas,"key_cached_values_verified":True},
"native_excel_tested":False,"cloud_or_audio_tests_run":False,"errors":errors}
(ROOT/"verification.json").write_text(json.dumps(checks,indent=2)+"\n")
assert not errors, errors
print(json.dumps({"sources":len(sourceids),"links":links,"sheets":workbook_sheets,"independent_cases":len(independent),"errors":errors}))
