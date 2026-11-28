from geo import *
C="Cole, The Ardennes"
def mv(u,kind,to=None,order=1,src=(),**k):
    d={"unit":u,"move":kind,"order":order}
    if to: d["to"]=list(to)
    d.update(k); d["sources"]=list(src); return d
def st(u,at,src): return {"unit":u,"at":list(at),"sources":list(src)}
def sh(u,to,src): return {"unit":u,"to":list(to),"sources":list(src)}
POCKET7={"side":"allied","ring":RING_COLE}
MR={}
m16,m17=M("16 Dec 1944"),M("17 Dec 1944")
MR[1]=dict(asOf="2400 hrs, 16 Dec 1944",map=m17,lineStart=LINE_START,lineStartSources=[m16,C+", pp. 75 to 80 and Map I"],
 line=LINES[1],lineSources=[m17,C+", pp. 179 to 191"],
 set=[st("v",(6.20,50.505),[m16,"Set about 3.5 km north of the map symbol so the Sixth Panzer Army block, arriving on Day 2, does not slide across it"]),st("28id",(5.99,50.01),[m16]),st("106id",(6.22,50.27),[m16]),st("18vg",(6.48,50.31),[m16,C+", p. 142 (the 18th Volks Grenadier Division holds the West Wall along the Schnee Eifel and attacks north and south of it)","Set about 9 km south of the map symbol, east of the Schnee Eifel where its attack on the 106th began, so the Sixth Panzer Army block arriving on Day 2 has a clear lane along Peiper's road"]),
      st("2pz",(6.61,50.07),[m16]),st("7a",(6.51,49.93),[m16,"Shown at the 352d Volksgrenadier Division, the Seventh Army's right"])],
 moves=[mv("2pz","advance",(6.12,50.07),1,[C+", pp. 184 to 186 (Marnach falls; the Germans press toward Clerf)",m17])],
 shifts=[sh("106id",(6.14,50.28),[m17,C+", p. 156"])],
 tonight="The Skyline Drive villages still hold. The Germans are across the Our.")
m18=M("18 Dec 1944")
MR[2]=dict(asOf="2400 hrs, 17 Dec 1944",map=m18,line=LINES[2],lineSources=[m18,C+", pp. 260 to 263"],
 set=[st("26vg",(6.15,49.98),[m18,C+", pp. 182 to 184 (the map shows the division near Prüm; Cole puts it at the Our crossings near Gemünd)"])],
 moves=[mv("6pa","arrive",(5.98,50.40),1,[C+", pp. 260 to 263 (Peiper halts outside Stavelot for the night)",m18],enters="east"),
        mv("7ad","arrive",(5.93,50.30),2,[C+", p. 265 and ch. XVII",m18,"Enters from the west: the 7th Armored marched south from the Netherlands and made its last leg into St. Vith from Vielsalm"],enters="west")],
 shifts=[sh("106id",(6.08,50.27),[m18,C+", ch. VII"]),sh("28id",(5.93,49.95),[m18,C+", p. 196"])],
 tonight="Peiper waits outside Stavelot. The 7th Armored reaches St. Vith.")
m19=M("19 Dec 1944")
MR[3]=dict(asOf="2400 hrs, 18 Dec 1944",map=m19,line=LINES[3],lineSources=[m19,C+", pp. 266 to 272 and 305 to 310"],
 set=[st("30id",(5.97,50.49),[m19,C+", p. 269"]),st("82ab",(5.67,50.415),[m19,C+", p. 269"])],
 moves=[mv("101ab","arrive",(5.65,50.03),1,[C+", pp. 305 to 307 (the 101st assembles west of Bastogne)",m19],enters="west"),
        mv("26vg","advance",(5.85,50.0),2,[C+", pp. 299 to 304 (the XLVII Panzer Corps closes on Bastogne)",m19])],
 shifts=[sh("28id",(5.80,49.89),[m19,C+", p. 196 (Wiltz)"])],
 tonight="The 101st is in Bastogne. The Germans are a few miles east.")
m20=M("20 Dec 1944")
MR[4]=dict(asOf="2400 hrs, 19 Dec 1944",map=m20,line=LINES[4],lineSources=[m20,C+", pp. 156 to 172"],
 moves=[mv("18vg","advance",(6.25,50.29),1,[C+", pp. 167 to 172 (the 422d and 423d surrender on the Schnee Eifel)",m20])],
 shifts=[sh("6pa",(5.86,50.39),[m20,C+", pp. 266 to 268 and 335 to 345 (Trois Ponts, Stoumont, La Gleize)"])],
 tonight="Two regiments of the 106th are gone. St. Vith still holds.")
m21=M("21 Dec 1944")
MR[5]=dict(asOf="2400 hrs, 20 Dec 1944",map=m21,line=LINES[5],lineSources=[m21,C+", pp. 423 to 427"],
 moves=[mv("2pz","advance",(5.80,50.10),1,[C+", pp. 314 to 320 (Noville taken; the Ourthe crossings)",m21])],
 tonight="Montgomery takes the north. The Bulge pushes toward the Ourthe.")
m22=M("22 Dec 1944")
MR[6]=dict(asOf="2400 hrs, 21 Dec 1944",map=m22,line=LINES[6],lineSources=[m22,C+", pp. 407 to 413"],
 set=[st("3ad",(5.52,50.293),[m22]),st("84id",(5.354,50.30),[m22,C+", p. 321"])],
 moves=[mv("106id","leave",None,1,[C+", pp. 407 to 413",m22],why="Its last regiment fights on under the 7th Armored; the division leaves the table."),
        mv("18vg","advance",(6.11,50.28),2,[C+", pp. 407 to 413 (St. Vith falls in the night)",m22])],
 shifts=[sh("28id",(5.70,49.90),[m22])],
 tonight="St. Vith is lost. Its defenders hold a shrinking horseshoe.")
m23=M("23 Dec 1944")
MR[7]=dict(asOf="2400 hrs, 22 Dec 1944",map=m23,line=LINES[7],lineSources=[m23,C+", pp. 468 to 470 (the ring around Bastogne; the map still shows the road west open)"],
 pockets=[POCKET7],
 moves=[mv("4ad","arrive",(5.765,49.80),1,[C+", pp. 525 to 530 (the 4th Armored attacks north from Arlon)",m23],enters="south"),
        mv("iii","arrive",(5.95,49.80),2,[C+", ch. XIX (III Corps attacks north)",m23],enters="south"),
        mv("26vg","advance",(5.84,49.92),3,[C+", pp. 468 to 470",m23])],
 shifts=[sh("101ab",(5.715,50.005),[C+", p. 468",m23]),sh("28id",(5.61,49.83),[m23]),sh("18vg",(6.17,50.28),[m23])],
 tonight="Bastogne is surrounded. Help starts north from Arlon.")
m24=M("24 Dec 1944")
MR[8]=dict(asOf="2400 hrs, 23 Dec 1944",map=m24,line=LINES[8],lineSources=[m24,C+", pp. 468 to 472"],
 pockets=[POCKET7],
 moves=[mv("tc","air_mission",None,1,[C+", pp. 468 to 471 (the first resupply drop, 23 Dec)",m24],target=[5.715,50.005],enters="west",label="Supply Drop"),
        mv("7ad","leave",None,2,[C+", pp. 413 to 422",m24],why="Out of the St. Vith salient through the 82nd Airborne's lines to regroup."),
        mv("2pz","advance",(5.47,50.215),3,[C+", ch. XVIII (the 2d Panzer heads for the Meuse)",m24])],
 shifts=[sh("3ad",(5.60,50.33),[m24]),sh("82ab",(5.75,50.36),[m24]),sh("6pa",(5.95,50.37),[m24,C+", pp. 365 to 367 (Peiper's men slip out of La Gleize)"]),sh("4ad",(5.70,49.82),[m24,C+", p. 530"]),sh("28id",(5.50,49.82),[m24])],
 tonight="Supplies fall into Bastogne. The St. Vith defenders are out.")
