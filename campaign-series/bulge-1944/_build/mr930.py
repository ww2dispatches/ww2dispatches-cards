from geo import *
from mr18 import mv,st,sh,C
MR={}
def m(d): return M(d)
m25,m26,m27,m28,m29,m30,m31,j1=m("25 Dec 1944"),m("26 Dec 1944"),m("27 Dec 1944"),m("28 Dec 1944"),m("29 Dec 1944"),m("30 Dec 1944"),m("31 Dec 1944"),m("1 Jan 1945")
MR[9]=dict(asOf="2400 hrs, 24 Dec 1944",map=m25,line=LINES[9],lineSources=[m25,C+", pp. 437 to 446 (the spearhead at Celles and Foy-Notre-Dame; the map draws the tip short of them)"],
 pockets=[{"side":"allied","ring":RING_MAP25}],
 moves=[mv("2pz","advance",(5.02,50.235),1,[C+", pp. 437 to 446 (Celles, three miles from the Meuse at Dinant)",m25]),
        mv("2ad","arrive",(5.13,50.32),2,[C+", pp. 427 to 437 (the 2d Armored comes down to Ciney)",m25],enters="north")],
 shifts=[sh("84id",(5.36,50.33),[m25])],
 tonight="Christmas Eve. The spearhead is a few miles short of the Meuse.")
MR[10]=dict(asOf="2400 hrs, 25 Dec 1944",map=m26,line=LINES[10],lineSources=[m26,C+", pp. 468 to 480"],
 pockets=[{"side":"allied","ring":RING_MAP26}],
 shifts=[sh("6pa",(6.0,50.33),[m26])],
 set=[st("15pg",(5.60,50.13),[m26,C+", p. 474"]),st("9pz",(5.435,50.191),[m26,C+", p. 437"])],
 moves=[mv("15pg","advance",(5.62,50.10),1,[C+", pp. 474 to 480 (the Christmas attack from the northwest is broken at Champs and Hemroulle)",m26])],
 tonight="The Christmas attack fails. The ring holds.")
MR[11]=dict(asOf="2400 hrs, 26 Dec 1944",map=m27,line=LINES[11],lineSources=[m27,C+", pp. 530 to 532"],
 moves=[mv("4ad","advance",(5.69,49.905),1,[C+", pp. 530 to 532 (Abrams's column breaks through at Assenois)",m27])],
 tonight="Abrams is through. The corridor is one road wide.")
MR[12]=dict(asOf="2400 hrs, 27 Dec 1944",map=m28,line=LINES[12],lineSources=[m28,C+", p. 532 and ch. XXIV"],
 moves=[mv("26vg","fall_back",(5.87,50.0),1,[C+", ch. XXIV (the corridor is widened)",m28]),
        mv("iii","advance",(5.99,49.87),2,[C+", ch. XIX and XXIV (III Corps crosses the Sure)",m28])],
 tonight="Trucks come in. Ambulances go out.")
MR[13]=dict(asOf="2400 hrs, 28 Dec 1944",map=m29,line=LINES[13],lineSources=[m29,C+", pp. 565 to 571"],
 moves=[mv("2ad","advance",(5.10,50.25),1,[C+", pp. 565 to 571 (the Celles pocket is cleared; the spearhead's remnants fall back to Rochefort)",m29],
          drives=[{"unit":"2pz","to":[5.26,50.12]}])],
 tonight="The spearhead is gone. What is left falls back on Rochefort.")
MR[14]=dict(asOf="2400 hrs, 29 Dec 1944",map=m30,line=LINES[14],lineSources=[m30,C+", pp. 610 to 612"],
 moves=[mv("11ad","arrive",(5.525,49.95),1,[C+", p. 334 and pp. 646 to 648 (the 11th Armored comes up west of Bastogne)",m30],enters="south")],
 shifts=[sh("2ad",(5.20,50.355),[m30])],
 tonight="Fresh American armor comes up west of Bastogne.")
MR[15]=dict(asOf="2400 hrs, 30 Dec 1944",map=m31,line=LINES[15],lineSources=[m31,C+", pp. 610 to 648"],
 moves=[mv("11ad","advance",(5.54,49.985),1,[C+", pp. 646 to 648 (Chenogne and Lavaselle)",m31]),
        mv("26vg","advance",(5.87,49.97),2,[C+", pp. 641 to 645 (the attack on the corridor at Lutrebois)",m31])],
 tonight="Both sides attack at Bastogne on the same morning. Neither breaks through.")
MR[16]=dict(asOf="2400 hrs, 31 Dec 1944",map=j1,line=LINES[16],lineSources=[j1,C+", pp. 645 to 648"],
 moves=[mv("6ad","arrive",(5.835,49.88),1,[C+", p. 486 and pp. 645 to 648 (the 6th Armored comes up on the corridor's east side)",j1],enters="south")],
 tonight="The last night of 1944. Fresh armor waits east of Bastogne.")
