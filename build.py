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

# ---- HSE Observation, the new tab ----
# an observation reports either a good practice or an anomaly; an anomaly may carry
# corrective actions, which have no status today, so we can only count whether one exists.
# golden rules and categories are multi-select, so an observation can count in several
# rows: these lists sum to more than the number of observations, never less.
# a good practice carries no golden rule, so the rules only break down the anomalies
RULES=[("Risky situations",        26),
       ("PPE",                     21),
       ("Body Mechanics & Tools",  18),
       ("Work permit",             15),
       ("Traffic",                 14),
       ("Work at height",          13),
       ("Lifting operations",      11),
       ("Line of danger",          10),
       ("Energized Systems",        9),
       ("Confined spaces",          8),
       ("Hot works",                7),
       ("Excavation work",          6)]
CATS=[("Health",      41, 22),
      ("Safety",      96, 63),
      ("Security",    33, 19),
      ("Environment", 28, 16)]

HG, HA = 128, 84
HT = HG + HA

HC=[("Company A",38,22),("Company B",29,19),("Company C",27,16),
    ("Company D",23,15),("Company E",11,12)]
HS=[("Site 1 (Depot)",41,24),("Site 2 (Terminal)",34,21),
    ("Site 3 (Plant)",30,22),("Site 4 (Field)",23,17)]
HW=[("Workspace A",86,51),("Workspace B",42,33)]
for rows in (HC,HS,HW):
    assert sum(r[1] for r in rows)==HG and sum(r[2] for r in rows)==HA

# a multi-select list: every row fits inside the population, and the whole covers it
assert all(r[1]<=HG and r[2]<=HA for r in CATS)
assert sum(r[1] for r in CATS)>=HG and sum(r[2] for r in CATS)>=HA
# the rules are multi-select too, on the anomalies alone
assert all(r[1]<=HA for r in RULES) and sum(r[1] for r in RULES)>=HA

# ticking a golden rule opens a second multi-select, "Observed anomaly", the list of what
# can go wrong under that rule, with "Compliant" at the top. A rule's count is every anomaly
# that ticked it, Compliant answers included: the bar says the rule was looked at, and the
# modal says what was found. The list is optional, the rule is not.
SITU={
 "Risky situations":["Smoking or vaping outside the authorised areas",
                     "Worker or driver under the influence of alcohol or drugs",
                     "Degraded situation left unsecured and unreported",
                     "Risks not identified before a non routine or complex operation",
                     "Start and stop instructions for equipment not followed"],
 "Traffic":["Vehicle condition not checked before use",
            "Seatbelt not fastened",
            "Speeding or driving unsuited to road conditions",
            "Use of a communication device while driving",
            "Driving time or journey management plan not respected",
            "Pedestrian or cyclist traveling outside designated routes",
            "Handrail not held when taking the stairs"],
 "Work permit":["Pre-job briefing not signed",
                "Safety Green Light not done",
                "No stop, risk reassessment or supervisor notification when conditions changed"],
 "Confined spaces":["No permit and/or confined-space entry certificate",
                    "No verification of isolation from energy and/or fluid sources",
                    "No respiratory protection when required",
                    "No rescue plan",
                    "Atmosphere not tested prior to intervention",
                    "No atmosphere monitoring",
                    "No entry/exit supervision",
                    "Unauthorized entry"],
 "Hot works":["No hot work permit",
              "Flammable substance or ignition source nearby",
              "No written authorization before starting hot work",
              "Gas test not performed in the hazardous area",
              "No continuous gas monitoring in the hazardous area"],
 "Line of danger":["Positioned in the path of a pressure release",
                   "Positioned in the path of a dropped object",
                   "No safety barriers or exclusion zones",
                   "Loose objects not secured",
                   "No respect of safety barriers or exclusion zones"],
 "Excavation work":["No safe access when the excavation is deeper than 1.3 m (4 ft)",
                    "No shoring or sloping of the walls",
                    "Underground networks not located before digging",
                    "Spoil stored at the edge of the excavation"],
 # the five lists below are still placeholders, the real wording is in the app
 "PPE":["Helmet not worn in the required zone","Eye protection missing",
        "Gloves not suited to the product handled","Hearing protection not worn"],
 "Body Mechanics & Tools":["Manual handling beyond the allowed load","Tool not suited to the task",
                           "Damaged or modified tool kept in service","Working posture at risk"],
 "Lifting operations":["Load passing over people","Sling or accessory not checked",
                       "Exclusion zone not marked","Lifting plan missing"],
 "Energized Systems":["Isolation not verified before work","Lock out tag out not applied",
                      "Stored energy not released","Live work without authorisation"],
 "Work at height":["Harness not clipped","Guardrail missing or incomplete",
                   "Ladder used as a work platform","Tools not secured against dropping"]}
RULE_SITU={}
for name,a in RULES:
    names=SITU[name]
    compliant=max(1,round(a*0.15))         # ticked the rule, answered Compliant, nothing wrong
    unspec=max(1,round(a*0.10))            # ticked the rule, answered nothing
    placed=a-compliant-unspec              # ticked at least one line of the list
    assert placed>0, name
    w=[6,5,4,3,3][:len(names)] if len(names)<=5 else [6]*len(names)
    split=spread(round(placed*1.3), w)
    split=[min(v,placed) for v in split]
    while sum(split)<placed:
        i=split.index(min(split)); split[i]+=1
    RULE_SITU[name]={"rows":[{"name":names[i],"anom":split[i]} for i in range(len(names))],
                     "unspecified":unspec,
                     "compliant":compliant}
    assert all(v<=placed for v in split) and sum(split)>=placed, name
    assert compliant+unspec<=a, name

# the Stop Card: one mandatory yes/no at the end of every anomaly form, so the answer
# exists on all of them and the rate is always out of the anomalies, never out of a subset.
SC=37                                            # anomalies where a Stop Card was used
assert 0 <= SC <= HA

SC_RULES={}
for name,a in RULES:                             # multi-select, so these sum to more than SC
    SC_RULES[name]=min(a, max(0, round(a*random.uniform(.18,.62))))
assert all(v<=dict(RULES)[k] for k,v in SC_RULES.items())
assert sum(SC_RULES.values())>=SC
SC_CATS={c[0]:min(c[2], max(0, round(c[2]*random.uniform(.30,.55)))) for c in CATS}
assert all(SC_CATS[c[0]]<=c[2] for c in CATS) and sum(SC_CATS.values())>=SC
AE=41                                            # anomalies raised during an intervention
assert AE<=HA
SC_ENTRY_DURING=18                               # of those, with a Stop Card
assert SC_ENTRY_DURING<=min(AE,SC) and SC-SC_ENTRY_DURING<=HA-AE
SC_ACTION=29                                     # Stop Cards that also carry a corrective action
assert SC_ACTION<=SC
SC_COMP=spread(SC,[r[2] for r in HC]); SC_COMP=[min(SC_COMP[i],HC[i][2]) for i in range(len(HC))]
SC_SITE=spread(SC,[r[2] for r in HS]); SC_SITE=[min(SC_SITE[i],HS[i][2]) for i in range(len(HS))]
SC_WORK=spread(SC,[r[2] for r in HW]); SC_WORK=[min(SC_WORK[i],HW[i][2]) for i in range(len(HW))]

hgd=spread(HG,[max(0.01,random.gauss(1,.35)) for _ in range(n)])
had=spread(HA,[max(0.01,random.gauss(1,.40)) for _ in range(n)])
assert sum(hgd)==HG and sum(had)==HA

# a Stop Card lives on an anomaly, so a day can never hold more of them than it holds
# anomalies: weight the split by the day's anomalies, clamp, then place what is left
# on the days that still have room
sc_daily=spread(SC,[max(0.0001,had[i]) for i in range(n)])
sc_daily=[min(sc_daily[i],had[i]) for i in range(n)]
left=SC-sum(sc_daily)
while left>0:
    room=sorted(((had[j]-sc_daily[j],j) for j in range(n)), reverse=True)
    assert room[0][0]>0, "no room left for the Stop Cards"
    for r,j in room:
        if left==0: break
        if r>0:
            sc_daily[j]+=1; left-=1
assert sum(sc_daily)==SC and all(sc_daily[i]<=had[i] for i in range(n))

HSE={
 "submitted":HT, "good":HG, "anom":HA,
 "daily":{"good":hgd,"anom":had},
 "entry":{"during":97,"standalone":HT-97},
 "actions":{"with_action":61},
 "stopcard":{"used":SC,
             "daily":sc_daily,
             "rules":[{"name":r[0],"anom":r[1],"stop":SC_RULES[r[0]]} for r in RULES],
             "categories":[{"name":c[0],"anom":c[2],"stop":SC_CATS[c[0]]} for c in CATS],
             "companies":[{"name":HC[i][0],"anom":HC[i][2],"stop":SC_COMP[i]} for i in range(len(HC))],
             "sites":[{"name":HS[i][0],"anom":HS[i][2],"stop":SC_SITE[i]} for i in range(len(HS))],
             "workspaces":[{"name":HW[i][0],"anom":HW[i][2],"stop":SC_WORK[i]} for i in range(len(HW))],
             "entry":{"anom_during":AE,"stop_during":SC_ENTRY_DURING},
             "actions":{"stop_with_action":SC_ACTION}},
 "rules":[{"name":r[0],"anom":r[1],"situations":RULE_SITU[r[0]]} for r in RULES],
 "categories":[{"name":c[0],"good":c[1],"anom":c[2],"total":c[1]+c[2]} for c in CATS],
 "companies":[{"name":r[0],"good":r[1],"anom":r[2],"total":r[1]+r[2]} for r in HC],
 "sites":[{"name":r[0],"good":r[1],"anom":r[2],"total":r[1]+r[2]} for r in HS],
 "workspaces":[{"name":r[0],"good":r[1],"anom":r[2],"total":r[1]+r[2]} for r in HW],
}
assert HSE["good"]+HSE["anom"]==HSE["submitted"]
assert sum(HSE["entry"].values())==HSE["submitted"]
assert 0 <= HSE["actions"]["with_action"] <= HSE["anom"]
SCB=HSE["stopcard"]
assert 0 <= SCB["used"] <= HSE["anom"]
assert sum(SCB["daily"])==SCB["used"] and len(SCB["daily"])==n
for k in ("companies","sites","workspaces"):
    assert sum(r["stop"] for r in SCB[k])==SCB["used"], k
    assert all(r["stop"]<=r["anom"] for r in SCB[k]), k
assert SCB["entry"]["anom_during"]<=HSE["anom"]
assert SCB["entry"]["stop_during"]<=min(SCB["entry"]["anom_during"], SCB["used"])
assert SCB["used"]-SCB["entry"]["stop_during"] <= HSE["anom"]-SCB["entry"]["anom_during"]
assert SCB["actions"]["stop_with_action"]<=min(SCB["used"], HSE["actions"]["with_action"])
for k in ("rules","categories"):                 # multi-select: at least the total, never a row above its own population
    assert sum(r["stop"] for r in SCB[k])>=SCB["used"], k
    assert all(r["stop"]<=r["anom"] for r in SCB[k]), k
for k in ("companies","sites","workspaces"):
    assert sum(r["total"] for r in HSE[k])==HSE["submitted"], k
assert sum(r["total"] for r in HSE["categories"])>=HSE["submitted"]
assert sum(r["anom"] for r in HSE["rules"])>=HSE["anom"]
assert all(r["anom"]<=HSE["anom"] for r in HSE["rules"])
for r in HSE["rules"]:
    S=r["situations"]; placed=r["anom"]-S["unspecified"]-S["compliant"]
    assert S["unspecified"]+S["compliant"]<=r["anom"], r["name"]
    assert all(x["anom"]<=placed for x in S["rows"]), r["name"]
    assert sum(x["anom"] for x in S["rows"])>=placed, r["name"]
D["hse"]=HSE

json.dump(D,open("data.json","w",encoding="utf-8"),indent=1,ensure_ascii=False)
print("ALL ASSERTIONS PASSED")
for m in("all","alone","accompanied"):
    o,f,a=D["outcome"][m],D["funnel"][m],D["actions"][m]
    print(f"{m:12s} forms {o['total']:4d} · risk raised {f['raised']:3d} "
          f"({round(f['raised']/o['total']*100,1):4}%) · self {f['self']:2d} · initiator {f['initiator']} · "
          f"maintained {f['maintained']:2d} · actions {a['total']:2d} (photo {round(a['photo']/a['total']*100)}%)")
H=D["hse"]
print(f"stop card    used on {H['stopcard']['used']:3d} of {H['anom']} anomalies "
      f"({round(H['stopcard']['used']/H['anom']*100,1)}%)")
print(f"hse          observations {H['submitted']:4d} · good practice {H['good']:3d} · anomalies {H['anom']:3d} "
      f"({round(H['anom']/H['submitted']*100,1)}%) · with a corrective action {H['actions']['with_action']:3d} "
      f"({round(H['actions']['with_action']/H['anom']*100,1)}%)")
