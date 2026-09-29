import json, random
random.seed(5)
D={}
D["period"]={"label":"01 to 30 Sep 2026","days":30}

MODE={"alone":{"go":119,"gac":18,"stop":4},"accompanied":{"go":149,"gac":45,"stop":13}}
for m in MODE: MODE[m]["total"]=sum(MODE[m][k] for k in("go","gac","stop"))
ALL={k:MODE["alone"][k]+MODE["accompanied"][k] for k in("go","gac","stop")}; ALL["total"]=sum(ALL.values())
assert ALL["total"]==348
D["outcome"]={"all":ALL,"alone":MODE["alone"],"accompanied":MODE["accompanied"]}
D["submitted"]={m:D["outcome"][m]["total"] for m in D["outcome"]}

def build(a,c,names):
    out={"alone":[],"accompanied":[],"all":[]}
    for i,n in enumerate(names):
        t=[a[i][j]+c[i][j] for j in range(3)]
        for k,r in(("alone",a[i]),("accompanied",c[i]),("all",t)):
            tot=sum(r)
            out[k].append({"name":n,"go":r[0],"gac":r[1],"stop":r[2],"total":tot,
                           "detection":round((r[1]+r[2])/tot*100,1) if tot else 0})
    for k in out:
        src=MODE.get(k,ALL)
        for j,key in enumerate(("go","gac","stop")):
            assert sum(r[key] for r in out[k])==src[key],(k,key)
    return out

D["companies"]=build([(41,4,0),(26,5,2),(21,4,1),(18,3,1),(13,2,0)],
                     [(55,10,2),(35,14,4),(27,10,4),(21,8,2),(11,3,1)],
  ["Company A","Company B","Company C","Company D","Company E"])
D["sites"]=build([(39,5,1),(33,6,2),(27,4,1),(20,3,0)],
                 [(49,12,3),(41,15,5),(34,11,3),(25,7,2)],
  ["Site 1 (Depot)","Site 2 (Terminal)","Site 3 (Plant)","Site 4 (Field)"])
D["workspaces"]=build([(90,12,2),(29,6,2)],[(111,32,9),(38,13,4)],["Workspace A","Workspace B"])

EP={"alone":{"start":112,"already_started":9,"standalone":20},
    "accompanied":{"start":177,"already_started":13,"standalone":17}}
EP["all"]={k:EP["alone"][k]+EP["accompanied"][k] for k in EP["alone"]}
for m in("alone","accompanied","all"): assert sum(EP[m].values())==D["submitted"][m],m
D["entry"]=EP

# ---- old pie kept: which permit the form hangs off ----
# counted on the forms created at the check-in of an intervention only.
# each of those sits under an e-permit or a paper permit, nothing else.
PM={"alone":{"epermit":90,"paper":22},
    "accompanied":{"epermit":141,"paper":36}}
PM["all"]={k:PM["alone"][k]+PM["accompanied"][k] for k in PM["alone"]}
for m in ("alone","accompanied","all"):
    assert PM[m]["epermit"]+PM[m]["paper"]==EP[m]["start"], m
D["permit"]=PM

# ---- N5: Stops and what was done about them (form level) ----
FUN={"alone":{"self":18,"initiator":0,"maintained":4},
     "accompanied":{"self":38,"initiator":7,"maintained":13}}
FUN["all"]={k:FUN["alone"][k]+FUN["accompanied"][k] for k in FUN["alone"]}
for m in("alone","accompanied","all"):
    o=D["outcome"][m]
    assert FUN[m]["self"]+FUN[m]["initiator"]==o["gac"],m       # every Go and Corrected has a corrector
    assert FUN[m]["maintained"]==o["stop"],m                     # every Stop stayed a Stop
    FUN[m]["raised"]=sum(FUN[m][k] for k in("self","initiator","maintained"))
    assert FUN[m]["raised"]==o["gac"]+o["stop"],m
D["funnel"]=FUN

ACT={"alone":{"total":18,"photo":9,"written":15},
     "accompanied":{"total":45,"photo":25,"written":36}}
ACT["all"]={k:ACT["alone"][k]+ACT["accompanied"][k] for k in ACT["alone"]}
for m in("alone","accompanied","all"):
    assert ACT[m]["total"]==D["outcome"][m]["gac"],m             # one action per corrected form
    assert ACT[m]["photo"]<=ACT[m]["total"] and ACT[m]["written"]<=ACT[m]["total"]
D["actions"]=ACT

D["pjb_substance"]={"Attestation only, nothing written":128,"Partly written":34,"All four fields written":45}
assert sum(D["pjb_substance"].values())==MODE["accompanied"]["total"]

D["initiator"]={"escalated":20,"overridden":7,"upheld":13}
assert D["initiator"]["overridden"]==FUN["accompanied"]["initiator"]
assert D["initiator"]["upheld"]==MODE["accompanied"]["stop"]
assert D["initiator"]["overridden"]+D["initiator"]["upheld"]==D["initiator"]["escalated"]
D["initiators"]=[{"name":"Initiator A","escalated":9,"overrides":3},
                 {"name":"Initiator B","escalated":4,"overrides":2},
                 {"name":"Initiator C","escalated":3,"overrides":1},
                 {"name":"Initiator D","escalated":4,"overrides":1}]
for r in D["initiators"]: r["rate"]=round(r["overrides"]/r["escalated"]*100,1)
assert sum(r["overrides"] for r in D["initiators"])==7
assert sum(r["escalated"] for r in D["initiators"])==20

# ---- recurring risk categories, top N by volume ----
# rows: (category, alone(self,init,maint), accompanied(self,init,maint), example risk, example action)
CATS=[
 ("Equipment or tool defect",(4,0,1),(8,2,2),
  "Gas detector past its calibration date","Replaced with a calibrated unit from the store"),
 ("Access or work area not secured",(3,0,1),(6,1,3),
  "Ladder footing unstable on loose gravel","Repositioned on a steel plate, second person footing the ladder"),
 ("Missing or wrong PPE",(3,0,0),(7,1,1),
  "Two crew members without cut-resistant gloves","Gloves collected from the store before start"),
 ("Energy isolation not confirmed",(2,0,1),(4,1,2),
  "Pump isolation not confirmed on the line","Isolation verified with the control room, lock applied"),
 ("Weather or ground conditions",(1,0,1),(3,0,3),
  "Access road washed out after overnight rain","Alternative access route used"),
 ("Lighting insufficient",(2,0,0),(3,1,0),
  "Lighting insufficient in the work area","Portable lighting installed"),
 ("Adjacent activity not coordinated",(1,0,0),(3,0,1),
  "Adjacent hot work in progress with no barrier in place","Hot work paused and a barrier installed before start"),
 ("Labelling or documentation mismatch",(1,0,0),(2,0,1),
  "Valve labelling does not match the isolation drawing","Line identified with the control room and re-tagged"),
 ("Gas or atmosphere check missing",(1,0,0),(1,1,0),
  "Atmosphere not tested before entry","Reading taken and logged before entry"),
 ("Other, uncategorised",(0,0,0),(1,0,0),
  "Task scope differs from what was briefed","Scope confirmed with the supervisor before start"),
]
CATEG={"alone":[],"accompanied":[],"all":[]}
for i,(name,a,c,ex,act) in enumerate(CATS):
    t=tuple(a[j]+c[j] for j in range(3))
    for key,r in (("alone",a),("accompanied",c),("all",t)):
        tot=sum(r)
        if tot==0: continue
        CATEG[key].append({"name":name,"self":r[0],"initiator":r[1],"maintained":r[2],"total":tot,
                           "ref":"PJB-2026-%04d"%(400+i*37),"example":ex,"action":act})
for key in CATEG:
    src=FUN[key]
    for k in ("self","initiator","maintained"):
        assert sum(r[k] for r in CATEG[key])==src[k],(key,k)
    assert sum(r["total"] for r in CATEG[key])==src["raised"],key
    CATEG[key].sort(key=lambda r:-r["total"])
D["categories"]=CATEG
D["top_n"]=10

def split(total,n,lo=0,hi=None):
    """Spread `total` over n days with largest-remainder rounding, so no day absorbs the leftover."""
    if total == 0: return [0]*n
    w = [random.uniform(0.55, 1.45) for _ in range(n)]
    sw = sum(w)
    raw = [total*x/sw for x in w]
    base = [int(x) for x in raw]
    rem = total - sum(base)
    for i in sorted(range(n), key=lambda i: -(raw[i]-base[i]))[:rem]:
        base[i] += 1
    assert sum(base) == total and min(base) >= 0
    return base

n=30; daily={}
for m in("alone","accompanied"):
    daily[m]={k:split(MODE[m][k],n) for k in("go","gac","stop")}
daily["all"]={k:[daily["alone"][k][i]+daily["accompanied"][k][i] for i in range(n)] for k in("go","gac","stop")}
for m in("alone","accompanied","all"):
    src=MODE.get(m,ALL)
    for k in("go","gac","stop"): assert sum(daily[m][k])==src[k],(m,k)
D["daily"]=daily
D["daily_labels"]=["%02d Sep"%d for d in range(1,n+1)]

# ---- the permit block, day by day: counts per permit type ----
# the population is the forms created at the check-in of an intervention, so the
# daily bars must add up to entry.start, and each permit type to its own total.
share=PM["all"]["epermit"]/(PM["all"]["epermit"]+PM["all"]["paper"])*100
tot_all=[daily["all"]["go"][i]+daily["all"]["gac"][i]+daily["all"]["stop"][i] for i in range(n)]
grand=sum(tot_all)

def spread(total, weights):
    """integer split of `total` over `weights`, largest remainder, never negative"""
    raw=[total*w/sum(weights) for w in weights]
    out=[int(x) for x in raw]
    rest=total-sum(out)
    order=sorted(range(len(raw)), key=lambda i: raw[i]-out[i], reverse=True)
    for i in order[:rest]: out[i]+=1
    return out

checkin=spread(EP["all"]["start"], tot_all)
day_share=[min(100.0,max(0.0,random.gauss(share,7))) for _ in range(n)]
ep=spread(PM["all"]["epermit"], [max(0.01, checkin[i]*day_share[i]) for i in range(n)])
ep=[min(ep[i], checkin[i]) for i in range(n)]
missing=PM["all"]["epermit"]-sum(ep)
i=0
while missing>0:
    if ep[i]<checkin[i]: ep[i]+=1; missing-=1
    i=(i+1)%n
pa=[checkin[i]-ep[i] for i in range(n)]
D["permit_daily"]={"epermit":ep,"paper":pa}
assert sum(ep)==PM["all"]["epermit"] and sum(pa)==PM["all"]["paper"]
assert all(e>=0 and p>=0 for e,p in zip(ep,pa))
assert sum(ep)+sum(pa)==EP["all"]["start"]

json.dump(D,open("data.json","w",encoding="utf-8"),indent=1,ensure_ascii=False)
print("ALL ASSERTIONS PASSED")
for m in("all","alone","accompanied"):
    o,f,a=D["outcome"][m],D["funnel"][m],D["actions"][m]
    print(f"{m:12s} forms {o['total']:4d} · risk raised {f['raised']:3d} "
          f"({round(f['raised']/o['total']*100,1):4}%) · self {f['self']:2d} · initiator {f['initiator']} · "
          f"maintained {f['maintained']:2d} · actions {a['total']:2d} (photo {round(a['photo']/a['total']*100)}%)")
