"""Jeu synthétique de 2 880 observations pour l'import longitudinal du Laboratoire EPS.
240 codes non nominatifs (4 groupes x 60), 4 instruments, 3 occasions. Graine fixe : 26."""
import random
random.seed(26)
inst=[("sprint30","s",5.2,.4),("saut_horizontal","cm",185,20),("souplesse_assise","cm",8,6),("leger20","palier",6,1.5)]
rows=["participant;group;instrument;unit;occasion;date;protocol;value"]
dates=["2026-09-15","2026-12-10","2027-03-10"]
for g in ("TC1","TC2","1B1","1B2"):
    for i in range(60):
        pid=f"{g}-{i+1:03d}"
        for code,unit,m,sd in inst:
            base=random.gauss(m,sd)
            for k,dte in enumerate(dates,1):
                rows.append(f"{pid};{g};{code};{unit};T{k};{dte};standard;{round(base+random.gauss(0,sd*.2),2)}")
open("lab_synthetique_2880.csv","w",encoding="utf-8").write("\n".join(rows)+"\n")
