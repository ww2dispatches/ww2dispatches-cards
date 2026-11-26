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
MD="MacDonald, The Last Offensive"
def J(d): return M(d+" 1945")
MR[17]=dict(asOf="2400 hrs, 1 Jan 1945",map=J("2 Jan"),line=JLINES[17],lineSources=[J("2 Jan"),C+", pp. 648 to 650",MD+", pp. 22 to 26"],
 set=[st("6abr",(4.97,50.26),[J("2 Jan"),MD+", p. 26"])],
 moves=[mv("lw","air_mission",None,1,["Operation Bodenplatte, 1 January 1945: some 900 German aircraft strike Allied airfields in Belgium and the Netherlands. "+MD+", p. 25 (the Luftwaffe's New Year's Day attack)",J("2 Jan")],target=[5.10,50.38],enters="east",label="Air Strike")],
 shifts=[sh("84id",(5.29,50.24),[J("2 Jan")]),sh("2ad",(5.32,50.36),[J("2 Jan")]),sh("11ad",(5.54,49.97),[J("2 Jan")])],
 tonight="The Luftwaffe's last great blow lands on the airfields, far behind the front.")
MR[18]=dict(asOf="2400 hrs, 2 Jan 1945",map=J("3 Jan"),line=JLINES[18],lineSources=[J("3 Jan"),MD+", pp. 26 to 27"],
 moves=[mv("17ab","arrive",(5.46,49.87),1,[MD+", p. 37 (the 17th Airborne comes into the line west of Bastogne)",J("3 Jan")],enters="south"),
        mv("28id","leave",None,2,[C+", p. 560",J("3 Jan")],why="The 17th Airborne takes over its sector near Neufchâteau.")],
 shifts=[sh("2ad",(5.44,50.32),[J("3 Jan"),MD+", p. 27"])],
 tonight="First Army is set to attack from the north in the morning.")
MR[19]=dict(asOf="2400 hrs, 3 Jan 1945",map=J("4 Jan"),line=JLINES[19],lineSources=[J("4 Jan"),MD+", pp. 27 to 31"],
 moves=[mv("2ad","advance",(5.45,50.285),1,[MD+", pp. 27 to 31 (VII Corps attacks south toward Houffalize)",J("4 Jan")]),
        mv("3ad","advance",(5.64,50.315),2,[MD+", pp. 27 to 31",J("4 Jan")])],
 shifts=[sh("82ab",(5.80,50.39),[J("4 Jan")])],
 tonight="The First Army is attacking. Snow and ice slow every yard.")
MR[20]=dict(asOf="2400 hrs, 4 Jan 1945",map=J("5 Jan"),line=JLINES[20],lineSources=[J("5 Jan"),MD+", pp. 37 to 39"],
 moves=[mv("11ad","leave",None,1,[MD+", p. 37",J("5 Jan")],why="Relieved by the 17th Airborne and pulled back to refit."),
        mv("17ab","advance",(5.565,50.0),2,[MD+", pp. 37 to 39 (the 17th Airborne's first attack, toward Flamierge)",J("5 Jan")])],
 tonight="A green airborne division learns the hard way on the ridge at Flamierge.")
MR[21]=dict(asOf="2400 hrs, 5 Jan 1945",map=J("6 Jan"),line=JLINES[21],lineSources=[J("6 Jan"),"Battle of Bure, Airborne Assault museum (paradata.org.uk)"],
 moves=[mv("6abr","advance",(5.20,50.10),1,["British 6th Airborne Division at Bure, 3 to 5 January 1945 (paradata.org.uk)",J("6 Jan")],drives=[{"unit":"2pz","to":[5.36,50.10]}])],
 tonight="Bure is in British hands after three days of street fighting.")
MR[22]=dict(asOf="2400 hrs, 6 Jan 1945",map=J("7 Jan"),line=JLINES[22],lineSources=[J("7 Jan"),MD+", pp. 31 to 32"],
 tonight="The fighting grinds on in deep snow.")
MR[23]=dict(asOf="2400 hrs, 7 Jan 1945",map=J("8 Jan"),line=JLINES[23],lineSources=[J("8 Jan"),MD+", pp. 31 to 32"],
 tonight="The road from La Roche to Vielsalm is cut.")
MR[24]=dict(asOf="2400 hrs, 8 Jan 1945",map=J("9 Jan"),line=JLINES[24],lineSources=[J("9 Jan"),MD+", pp. 31 to 32"],
 moves=[mv("9pz","leave",None,1,[MD+", pp. 31 to 32 and 39 (Hitler allows a withdrawal from the tip; the German armor begins to leave)",J("9 Jan")],why="Pulled out as Hitler allows the withdrawal from the tip."),
        mv("2pz","fall_back",(5.47,50.16),2,[MD+", pp. 31 to 32",J("9 Jan")])],
 tonight="The tip of the Bulge begins to empty.")
MR[25]=dict(asOf="2400 hrs, 9 Jan 1945",map=J("10 Jan"),line=JLINES[25],lineSources=[J("10 Jan"),MD+", pp. 39 to 40"],
 moves=[mv("26vg","fall_back",(5.93,50.02),1,[MD+", p. 40 (the 90th Division attacks northeast through the 26th Division southeast of Bastogne and surprises the 5th Parachute Division)",J("10 Jan")])],
 tonight="Third Army attacks again. Southeast of Bastogne, the Germans give ground.")
MR[26]=dict(asOf="2400 hrs, 10 Jan 1945",map=J("11 Jan"),line=JLINES[26],lineSources=[J("11 Jan"),MD+", pp. 39 to 40"],
 moves=[mv("2pz","leave",None,1,[MD+", pp. 31 to 32 and 39",J("11 Jan")],why="Falls back out of the tip toward Houffalize under Hitler's withdrawal order."),
        mv("15pg","fall_back",(5.72,50.16),2,[MD+", p. 39 (units west of Bastogne pull back toward the line Longchamps to the Ourthe)",J("11 Jan")])],
 tonight="Quietly, behind rear guards and mines, the Germans are leaving the tip.")
MR[27]=dict(asOf="2400 hrs, 11 Jan 1945",map=J("12 Jan"),line=JLINES[27],lineSources=[J("12 Jan"),"La Roche liberated 11 Jan 1945 by the 1st Black Watch, 51st Highland Division (51hd.co.uk; Liberation Route Europe); the map, drawn at noon on the 12th, still shows the town German"],
 moves=[mv("51hd","arrive",(5.56,50.195),1,["51st Highland Division at La Roche, 11 January 1945 (51hd.co.uk)",J("12 Jan")],enters="west")],
 tonight="Highlanders and Americans meet in the ruins of La Roche.")
MR[28]=dict(asOf="2400 hrs, 12 Jan 1945",map=J("13 Jan"),line=JLINES[28],lineSources=[J("13 Jan"),MD+", pp. 33 to 41"],
 tonight="Far to the east, the Red Army has opened its winter offensive.")
MR[29]=dict(asOf="2400 hrs, 13 Jan 1945",map=J("14 Jan"),line=JLINES[29],lineSources=[J("14 Jan"),MD+", pp. 40 to 41"],
 moves=[mv("101ab","advance",(5.72,50.05),1,[MD+", p. 41 (the fight for Foy, south of Noville)",J("14 Jan")])],
 tonight="Foy is taken. Noville is next.")
MR[30]=dict(asOf="2400 hrs, 14 Jan 1945",map=J("15 Jan"),line=JLINES[30],lineSources=[J("15 Jan"),MD+", pp. 33 and 41 to 42"],
 moves=[mv("3ad","advance",(5.74,50.255),1,[MD+", pp. 32 to 33 (VII Corps closes on Houffalize from the north)",J("15 Jan")])],
 tonight="Two armies are a few miles apart. They meet at Houffalize on the 16th.")
