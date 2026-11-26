# Day by Day captions for The Bulge (written 26 Nov 2026). No dashes anywhere.
COLE="https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-{}.html"
MAC="https://www.ibiblio.org/hyperwar/USA/USA-E-Last/USA-E-Last-2.html"
def c(ch,pp): return f"Cole, The Ardennes: Battle of the Bulge (CMH), {pp}: "+COLE.format(ch)
M=lambda pp: f"MacDonald, The Last Offensive (CMH), ch. II, {pp}: "+MAC
D={}
def day(n,series,place,subtitle,body,threads,sources,somber=False):
    D[n]=dict(series=series,place=place,subtitle=subtitle,body=body,threads=threads,sources=sources,**({"somber":True} if somber else {}))

day(1,"battle","Skyline Drive, Luxembourg","The 28th holds Skyline Drive",
"""At 5:30 this morning German guns open along the Ardennes, the quietest front in the West.

On the Skyline Drive, the ridge road above the Our River, the 110th Infantry of the 28th Division holds a chain of village strongpoints, about a rifle company in each. The phone lines are cut in the first minutes. By noon German infantry is across the road at Holzthum and Consthum. At dusk the garrison at Marnach goes silent.

The 28th came here from the Hürtgen Forest to rest.

How to read the table: olive blocks are American, khaki British, charcoal German. The red grease pencil line is the front each night. Black dashes are air missions. One block covers about 10 km.""",
"""At 5:30 a.m. German guns open along the quiet Ardennes front.

On the Skyline Drive above the Our River, the 28th Division's 110th Infantry holds a chain of villages, a rifle company in each. Phone lines die in minutes. By dusk Marnach has gone silent.

On the table: olive is American, khaki British, charcoal German. The red line is each night's front. One block is about 10 km.""",
[c(8,"pp. 179 to 186"),"Cirillo, Ardennes Alsace (CMH Pub 72 26): https://purl.fdlp.gov/GPO/LPS32986"])

day(2,"battle","Baugnez, near Malmedy, Belgium","Prisoners shot at Baugnez crossroads",
"""Between noon and one o'clock, on the road south of Malmedy, a German armored column led by Joachim Peiper runs into a truck convoy of Battery B, 285th Field Artillery Observation Battalion, at the Baugnez crossroads.

The convoy is shot up. The Americans who surrender are gathered in a field beside the road. About two hours later they are shot down with machine guns and pistols. A few survive by lying still among the dead.

More than 80 Americans are killed there.

By night Peiper's column is waiting outside Stavelot.""",
"""Early afternoon, south of Malmedy. Joachim Peiper's armored column overruns a convoy of Battery B, 285th Field Artillery Observation Battalion, at the Baugnez crossroads.

The Americans who surrender are gathered in a field. About two hours later they are machine gunned. A few survive by lying still among the dead.

More than 80 are killed.""",
[c(11,"pp. 260 to 262"),"National WWII Museum, The Malmedy Massacre: https://www.nationalww2museum.org/war/articles/malmedy-massacre"],somber=True)

day(3,"battle","Bastogne, Belgium","The 101st races into Bastogne",
"""Two days ago the 101st Airborne was resting at Camp Mourmelon in France. Last night the orders came.

Today its men ride 107 miles north in open trucks, through rain, snow flurries and darkness, against a stream of vehicles heading the other way. Many have no winter clothing. Their destination is a road junction town in Belgium called Bastogne.

They arrive tonight. German armor is a few miles to the east.

Farther north, American engineers blow the bridge over the Lienne at Habiemont as Peiper's tanks come into sight. His dash for the Meuse is blocked.""",
"""The 101st Airborne was resting in France. Today its men ride 107 miles north in open trucks, through rain and dark, many without winter clothing, to a road junction town called Bastogne.

They arrive tonight. German armor is a few miles east.

Up north, engineers blow the Habiemont bridge in front of Peiper's tanks.""",
[c(13,"p. 309 (the 107 mile move from Mourmelon)"),c(15,"p. 343 (Habiemont)"),"Mitchell, The 101st Airborne Division's Defense of Bastogne (Combat Studies Institute, 1986): https://ibiblio.org/hyperwar/USA/CSI/CSI-Bastogne/MITCHELL.asp.html"])

day(4,"battle","Schnee Eifel, Germany","Two regiments surrender on the Eifel",
"""Cut off since the 17th on a wooded ridge just inside Germany, the 422nd and 423rd Infantry of the green 106th Division try to fight their way out toward Schönberg.

They are short of ammunition, food and water, and German artillery has the range. This afternoon both regiments surrender. Thousands of Americans walk into captivity, one of the largest surrenders of American troops in the war.

At Verdun, Eisenhower meets his generals. Patton says he can turn his Third Army north and attack in three days.""",
"""Cut off on the Schnee Eifel since the 17th, the 106th Division's 422nd and 423rd Infantry try to break out toward Schönberg.

Low on ammunition, food and water, both regiments surrender this afternoon. Thousands of Americans go into captivity.

At Verdun, Patton tells Eisenhower he can attack north in three days.""",
[c(7,"pp. 161 to 172 (Cannae in the Schnee Eifel)"),c(20,"pp. 486 to 488 (Verdun)"),"National WWII Museum, The Fall of the Golden Lions: https://www.nationalww2museum.org/war/articles/fall-golden-lions"])

day(5,"state","Versailles, France","Ike hands Monty the northern armies",
"""The German breakthrough has cut Omar Bradley's 12th Army Group in two, and his headquarters in Luxembourg City cannot easily reach the armies north of the Bulge.

Eisenhower decides: the First and Ninth Armies, everything north of the break, go under Field Marshal Montgomery. Bradley keeps Patton's Third Army in the south.

Bradley protests. The decision stands.

This afternoon Montgomery drives to the First Army's headquarters to take charge of the northern battle.""",
"""The German breakthrough has split Bradley's 12th Army Group.

Eisenhower decides: the First and Ninth Armies, everything north of the break, go under Montgomery. Bradley keeps Patton in the south. Bradley protests. The decision stands.

Montgomery takes charge of the northern battle this afternoon.""",
[c(17,"pp. 423 to 426"),"Eisenhower Presidential Library, Battle of the Bulge documents: https://www.eisenhowerlibrary.gov/index%2Ephp/node/1216"])

day(6,"battle","St. Vith, Belgium","St. Vith falls in the night",
"""For five days the crossroads town of St. Vith has blocked the routes the German northern armies need. The 7th Armored and what is left of the 106th hold it from a horseshoe of woods and villages.

Tonight German tanks and infantry break into the town. The defenders fall back west toward the Salm River and Vielsalm.

Tomorrow Montgomery will decide they have done enough. "They can come back with all honor," he will say.""",
"""For five days St. Vith has blocked the roads the Germans need. The 7th Armored and the 106th's survivors hold it from a horseshoe of woods.

Tonight German tanks break into the town. The defenders fall back toward the Salm River.

Tomorrow Montgomery will let them go: "They can come back with all honor." """,
[c(17,"pp. 407 to 413"),"Cirillo, Ardennes Alsace (CMH Pub 72 26): https://purl.fdlp.gov/GPO/LPS32986"])

day(7,"battle","Bastogne, Belgium","A one word answer from Bastogne",
"""Late morning. Four Germans under a white flag walk up to an American outpost southeast of Bastogne. They carry a typed demand: surrender the encircled town within two hours, or be destroyed by artillery.

The note reaches Brig. Gen. Anthony McAuliffe, acting commander of the 101st Airborne. His reply is typed on a single sheet: "To the German Commander. N U T S! The American Commander."

Col. Joseph Harper of the 327th Glider Infantry hands it over. Asked what it means, he tells them to go to hell.

South of the town, the 4th Armored starts north from Arlon.""",
"""Late morning. Four Germans under a white flag bring a typed demand to an outpost at Bastogne: surrender the encircled town in two hours, or face annihilation.

McAuliffe's reply fits on one sheet: "To the German Commander. N U T S! The American Commander."

South of the town, the 4th Armored starts north.""",
[c(19,"p. 468"),"Mitchell, The 101st Airborne Division's Defense of Bastogne (Combat Studies Institute, 1986): https://ibiblio.org/hyperwar/USA/CSI/CSI-Bastogne/MITCHELL.asp.html"])

day(8,"battle","Bastogne, Belgium","Clear skies, and the drops begin",
"""After a week of fog and low cloud, a cold high pressure front moves in over the Ardennes. The morning is bright and clear.

Pathfinders parachute into Bastogne. Then the C 47s of IX Troop Carrier Command come over in waves and drop ammunition, food and medical supplies on colored parachutes into the snow inside the perimeter.

All day, fighter bombers attack German columns on the roads.

Up north, the St. Vith defenders finish crossing back through the 82nd Airborne's lines.""",
"""After a week of fog, the sky over the Ardennes clears.

Pathfinders jump into Bastogne. Then C 47s come over in waves, dropping ammunition, food and medical supplies on colored parachutes into the snow inside the perimeter.

All day, fighter bombers hunt German columns on the roads.""",
[c(19,"pp. 468 to 471"),"U.S. Army, Air Borne to the Airborne: https://www.army.mil/article/6753/Air_Borne_to_the_Airborne","Cirillo, Ardennes Alsace (CMH Pub 72 26): https://purl.fdlp.gov/GPO/LPS32986"])

day(9,"battle","Celles, Belgium","The tip of the Bulge nears the Meuse",
"""Christmas Eve. The point of the whole German offensive, the 2nd Panzer Division, is at Celles and Foy Notre Dame, about four miles from the Meuse at Dinant. Its tanks are nearly out of fuel.

The American 2nd Armored Division has come down from the north and found it. Tomorrow it will attack.

In Bastogne, German bombers hit the town after dark. One bomb falls on an aid station.

Along the Bulge, men on both sides spend the night in the snow.""",
"""Christmas Eve. The point of the German offensive, the 2nd Panzer Division, sits at Celles, about four miles from the Meuse. Its tanks are nearly dry.

The American 2nd Armored has found it and will attack tomorrow.

In Bastogne, German bombers hit the town after dark.""",
[c(18,"pp. 437 to 446 (Celles, four miles from the Meuse)"),"Cirillo, Ardennes Alsace (CMH Pub 72 26): https://purl.fdlp.gov/GPO/LPS32986"])

day(10,"battle","Bastogne, Belgium","Christmas morning attack at Bastogne",
"""In the dark before dawn on Christmas Day, German tanks and infantry attack Bastogne from the northwest, near Champs and Hemroulle.

Some tanks break through the line. Paratroopers, tank destroyers and artillery cut them off and destroy them inside the perimeter. By midmorning the attack has failed.

Near the Meuse, the 2nd Armored strikes the 2nd Panzer Division at Celles.

McAuliffe's Christmas message to his men begins with a question: "What's Merry about all this, you ask?" """,
"""Before dawn on Christmas Day, German tanks and infantry hit Bastogne from the northwest.

Some tanks break through. Paratroopers and tank destroyers trap and destroy them inside the perimeter. By midmorning it is over.

Near the Meuse, the 2nd Armored strikes the 2nd Panzer at Celles.""",
[c(19,"pp. 474 to 480"),"Warfare History Network, Christmas Day at Bastogne: https://warfarehistorynetwork.com/?p=36026"])

day(11,"battle","Assenois, near Bastogne, Belgium","Abrams breaks through to Bastogne",
"""Late afternoon. Lt. Col. Creighton Abrams decides not to wait for a slower route. His task force of the 4th Armored turns onto the road through Assenois, the shortest way into Bastogne.

At 4:35 p.m. artillery crashes onto the village. Lt. Charles Boggess's Shermans race in behind it, guns firing, and keep going. A little before five the lead tank reaches engineers of the 101st on the edge of the perimeter.

The siege is broken. The corridor is one road wide.""",
"""Late afternoon. Lt. Col. Creighton Abrams sends his 4th Armored task force down the road through Assenois, the shortest way into Bastogne.

Artillery hits the village at 4:35. Lt. Charles Boggess's Shermans race through behind it, and a little before five reach the 101st's lines.

The siege is broken.""",
[c(21,"pp. 553 to 555"),"HistoryNet, 4th Armored at Bastogne: https://historynet.com/firsthand-account-4th-armored-division-spearhead-at-bastogne-november-99-world-war-ii-feature/"])

day(12,"battle","Bastogne, Belgium","Ambulances roll out of Bastogne",
"""With the road from the south open, trucks bring ammunition, food and fuel into Bastogne. Going the other way are the wounded, hundreds of them, some of whom have waited days in cellars and a garage for a surgeon.

The corridor is still narrow, and German guns can reach it.

East of the town, the Germans pull back from the edge of the corridor, and III Corps pushes north across the Sure.""",
"""With the road from the south open, trucks roll into Bastogne with ammunition, food and fuel.

Going the other way are the wounded, hundreds of them, some after days in cellars waiting for a surgeon.

The corridor is still narrow and under German guns.""",
[c(21,"pp. 555 to 556"),c(24,"ch. XXIV"),"Mitchell, The 101st Airborne Division's Defense of Bastogne (Combat Studies Institute, 1986): https://ibiblio.org/hyperwar/USA/CSI/CSI-Bastogne/MITCHELL.asp.html"])

day(13,"state","Adlerhorst, Germany","Hitler orders a new attack in Alsace",
"""At his Adlerhorst headquarters, Hitler speaks to the division commanders who will open a new offensive in Alsace in three days. Its name is Nordwind.

He admits the Ardennes attack has not gone as he hoped. He insists the new blow can destroy American divisions while the Allies are tied down in the Bulge, and that the coalition against Germany can still break.

In the Ardennes, the survivors of his spearhead at Celles are falling back toward Rochefort.""",
"""At his Adlerhorst headquarters, Hitler briefs the commanders of a new offensive in Alsace, Nordwind, due in three days.

He admits the Ardennes has not gone as he hoped, but insists the new blow can still break the Allies.

At Celles, what is left of his spearhead falls back toward Rochefort.""",
["Clarke and Smith, Riviera to the Rhine (CMH), ch. XXVII: https://ibiblio.org/hyperwar/USA/USA-E-Riviera/USA-E-Riviera-27.html",c(22,"pp. 565 to 571 (the Celles pocket)")])

day(14,"battle","West of Bastogne, Belgium","Fresh armor comes up west of Bastogne",
"""The 11th Armored Division landed in France only weeks ago and has never been in battle. Tonight it moves up west of Bastogne, beside the 87th Infantry Division, to attack in the morning.

Patton wants Bastogne made safe and the narrow corridor widened, as a base for the drive north to Houffalize.

The Germans are bringing fresh divisions to Bastogne too. Both sides plan to attack at the same place, on the same morning.""",
"""The 11th Armored Division has never been in battle. Tonight it moves up west of Bastogne with the 87th Infantry Division to attack in the morning.

Patton wants the corridor widened as a base for the drive on Houffalize.

The Germans are bringing fresh divisions to the same ground.""",
[c(25,"pp. 646 to 648"),c(15,"p. 334"),"Cirillo, Ardennes Alsace (CMH Pub 72 26): https://purl.fdlp.gov/GPO/LPS32986"])

day(15,"battle","Lutrebois, Belgium","Two attacks collide at Lutrebois",
"""Patton attacks around Bastogne this morning. So do the Germans.

East of the corridor, at Lutrebois, German tanks and infantry strike for the road into Bastogne and run into the 35th Infantry Division and the 4th Armored. The woods and fields fill with burning German armor.

West of the town, the 11th Armored attacks at Chenogne in its first battle, straight into another German push, and loses heavily.

By night neither side has broken through.""",
"""Patton attacks around Bastogne this morning. So do the Germans.

At Lutrebois, German armor hits the 35th Division and the 4th Armored and is shot to pieces. West of town, the 11th Armored meets another German push at Chenogne and loses heavily.

Neither side breaks through.""",
[c(25,"pp. 641 to 648"),"Cirillo, Ardennes Alsace (CMH Pub 72 26): https://purl.fdlp.gov/GPO/LPS32986"])

day(16,"battle","Bastogne, Belgium","New Year's Eve in the foxholes",
"""The last night of 1944. Around Bastogne the ground is frozen too hard to dig, and men chip foxholes out of it with picks and charges.

The 6th Armored Division comes up on the east side of the corridor for an attack in the morning.

Near midnight, far to the south in Alsace, German troops begin Operation Nordwind, Hitler's second offensive of the winter.

The Bulge is sixteen days old.""",
"""The last night of 1944. Around Bastogne the ground is frozen too hard to dig.

The 6th Armored comes up east of the corridor for an attack in the morning.

Near midnight in Alsace, the Germans open Operation Nordwind, Hitler's second offensive of the winter.""",
[c(25,"pp. 645 to 648"),"MacDonald, The Last Offensive (CMH), ch. I: https://ibiblio.org/hyperwar/USA/USA-E-Last/USA-E-Last-1.html"])

day(17,"battle","Allied airfields, Belgium","The Luftwaffe's last great strike",
"""New Year's morning. More than 900 German fighters and fighter bombers take off at low level, under radio silence, for Allied airfields in Belgium, the Netherlands and France.

They catch rows of aircraft on the ground and destroy or damage hundreds. But the Luftwaffe loses some 300 aircraft and many of its last experienced pilots, some shot down by German flak crews who were never told the raid was coming.

The Allies can replace their planes. The Luftwaffe cannot replace its pilots.""",
"""New Year's morning. More than 900 German fighters streak in at low level against Allied airfields in Belgium, the Netherlands and France.

They wreck hundreds of planes on the ground. But the Luftwaffe loses about 300 aircraft and pilots it cannot replace, some to its own flak.""",
["History of War, Operation Bodenplatte: https://www.historyofwar.org/articles/operation_bodenplatte.html","Warhistoryonline, Operation Bodenplatte: https://www.warhistoryonline.com/world-war-ii/operation-luftwaffe-bodenplatte.html"])
D[17]["campaignsLine"]="Declass Campaigns opens today with Chapter 1, The Siege of Bastogne."

day(18,"home","United States","America's racetracks go dark",
"""Tomorrow every horse and dog track in the United States closes.

On December 23, with President Roosevelt's approval, War Mobilization Director James Byrnes asked the tracks to shut down by January 3 and stay closed until war conditions permit. The fighting in the Ardennes has shown the war is far from over.

Racing drew huge wartime crowds, and more than a billion dollars went through the betting windows in 1944. Byrnes wants the manpower, transport and materials for the war.""",
"""Tomorrow every racetrack in America closes.

On December 23, with the President's approval, War Mobilization Director James Byrnes asked tracks to shut by January 3 and stay closed until war conditions permit.

More than a billion dollars was bet at the tracks in 1944.""",
["Cumberland Sunday Times, 24 Dec 1944, p. 18: https://www.newspapers.com/newspage/1167190/","Equisearch, racing history, 23 Dec 1944: https://equisearch.com/articles/racing122403/"])

day(19,"battle","Hotton and Manhay, Belgium","First Army strikes from the north",
"""Before dawn, in snow and fog, the First Army's VII Corps attacks south from the line between Hotton and Manhay, toward Houffalize. The 2nd and 3rd Armored Divisions lead, with infantry following to mop up.

The aim is to meet Patton's Third Army coming up from Bastogne and cut the Bulge in two.

The roads are glazed with ice. Tanks slide off hillsides and block the roads behind them. The day's gains are small.""",
"""Before dawn, in snow and fog, the First Army's VII Corps attacks south toward Houffalize, the 2nd and 3rd Armored leading.

The goal: meet Patton coming up from Bastogne and cut the Bulge in two.

Roads are ice. Tanks slide off hillsides. Gains are small.""",
[M("pp. 26 to 31"),"Winston Churchill on the Ardennes counteroffensive, International Churchill Society: https://winstonchurchill.org/?p=59388"])

day(20,"battle","Flamierge, near Bastogne, Belgium","A green division at Dead Man's Ridge",
"""The 17th Airborne Division arrived from England at Christmas. This morning, in its first battle, it attacks west of Bastogne toward Flamierge, in a snowstorm, across open fields.

German tanks and infantry counterattack. The paratroopers are pinned on the open slope and lose heavily before they are pulled back.

They will call the high ground near Flamierge Dead Man's Ridge.""",
"""The 17th Airborne arrived from England at Christmas. Today, in its first battle, it attacks toward Flamierge west of Bastogne, in a snowstorm, across open ground.

German tanks counterattack. The paratroopers lose heavily.

They will call it Dead Man's Ridge.""",
["Liberation Route Europe, Monument to the 17th Airborne Division, Flamierge: https://www.europeremembers.com/pois/1157/monument-to-the-17th-u-s-airborne-division",M("pp. 37 to 39")])

day(21,"battle","Bure, Belgium","British paratroopers hold Bure",
"""Since the 3rd, the British 6th Airborne Division has fought for Bure, a village near the western tip of the Bulge, against German infantry and Tiger tanks in the streets.

The 13th Parachute Battalion took the village and then held it through counterattack after counterattack, often house by house.

Today the fight for Bure ends with the village in British hands. It has cost the battalion dearly.""",
"""Since the 3rd, Britain's 6th Airborne Division has fought for Bure, near the western tip of the Bulge, against infantry and Tiger tanks in the streets.

The 13th Parachute Battalion held on through counterattack after counterattack.

Today Bure is in British hands, at a heavy price.""",
["Airborne Assault museum, Battle of Bure: https://paradata.org.uk/node/11280","Royal British Legion Brussels, The British and the Battle of the Ardennes: https://branches.britishlegion.org.uk/branches/brussels-branch/history/the-british-and-the-battle-of-the-ardennes/"])

day(22,"state","London","Churchill asks Stalin for help",
"""Winston Churchill sends a personal message to Joseph Stalin. "The battle in the West is very heavy," he writes.

He asks whether the Allies can count on a major Russian offensive on the Vistula front, or somewhere else, during January. Eisenhower needs to know as he plans his next moves.

Stalin will answer tomorrow.""",
"""Churchill cables Stalin: "The battle in the West is very heavy."

He asks whether the Allies can count on a major Russian offensive on the Vistula front during January. Eisenhower needs to know.

Stalin will answer tomorrow.""",
["UK Parliament, Hansard, 14 Dec 1954 (the 6 Jan 1945 telegram): https://api.parliament.uk/historic-hansard/commons/1954/dec/14/prime-minister-and-marshal-stalin","Churchill Archive, Cambridge, telegram of 6 Jan 1945: https://archivesearch.lib.cam.ac.uk/repositories/9/archival_objects/1416405"])

day(23,"state","Zonhoven, Belgium","Montgomery meets the press",
"""At his headquarters at Zonhoven, Field Marshal Montgomery talks to war correspondents for an hour about the battle in the Ardennes.

"I salute the brave fighting man of America," he says. But he also tells how he took charge in the north and brought British troops into the fight, and many listeners hear a claim that he saved the battle.

American generals are furious, Bradley most of all. German radio will soon broadcast a twisted version of the talk that makes it worse.

At the front, the road from La Roche to Vielsalm is cut.""",
"""At Zonhoven, Montgomery talks to reporters for an hour about the Ardennes.

"I salute the brave fighting man of America," he says, but many hear a claim that he saved the battle. American generals are furious.

At the front, the La Roche to Vielsalm road is cut.""",
["The National Archives (UK), How Nazi fake news split Allied commanders in 1945: https://blog.nationalarchives.gov.uk/how-nazi-fake-news-split-allied-commanders-in-1945","Weapons and Warfare, Montgomery's press conference: https://weaponsandwarfare.com/?p=19791"])

day(24,"battle","Ardennes, Belgium","Hitler lets the tip pull back",
"""Hitler at last allows a withdrawal, but only a short one: out of the far western tip of the Bulge to a line on a great loop of the Ourthe River, about five miles west of Houffalize.

His generals asked to go back farther. He refuses.

He also orders the SS panzer divisions out of the line, into reserve near St. Vith. It is his first, unspoken admission that the Ardennes offensive has failed.""",
"""Hitler allows a short withdrawal: out of the western tip of the Bulge to a loop of the Ourthe, about five miles west of Houffalize.

His generals wanted more. He refuses.

He also pulls the SS panzer divisions into reserve near St. Vith. It is his first, unspoken admission of failure.""",
[M("pp. 31 to 32"),"Cirillo, Ardennes Alsace (CMH Pub 72 26): https://purl.fdlp.gov/GPO/LPS32986"])

day(25,"battle","Southeast of Bastogne, Belgium","Patton renews the drive north",
"""After a pause to bring up a new division, Patton's Third Army attacks again around Bastogne.

Southeast of the town, the veteran 90th Infantry Division, moved in under strict secrecy, attacks northeast through the 26th Division's lines and takes the German 5th Parachute Division by surprise. The 6th Armored attacks toward it from the other side.

A snowstorm sweeps the battlefield. The Germans fight for every village.""",
"""Third Army attacks again around Bastogne.

Southeast of the town, the 90th Division, brought in under strict secrecy, strikes northeast and catches the German 5th Parachute Division by surprise.

A snowstorm sweeps the field. Every village is a fight.""",
[M("pp. 39 to 40"),"Cirillo, Ardennes Alsace (CMH Pub 72 26): https://purl.fdlp.gov/GPO/LPS32986"])

day(26,"battle","St. Hubert and Tillet, Belgium","The Germans begin to slip away",
"""Under Hitler's order of the 8th, the Germans begin to leave the western end of the Bulge. There is no rout. They go slowly, behind rear guards, roadblocks and fields of mines, counterattacking wherever a position is about to fall.

Tonight the 87th Infantry Division finally fights its way into Tillet, a crossroads it has attacked for days.

Tomorrow the Americans will find St. Hubert empty.""",
"""Under Hitler's order, the Germans begin to leave the western end of the Bulge, slowly, behind rear guards, roadblocks and mines.

Tonight the 87th Division finally fights its way into Tillet.

Tomorrow the Americans will find St. Hubert empty.""",
[M("pp. 39 to 40"),"Cirillo, Ardennes Alsace (CMH Pub 72 26): https://purl.fdlp.gov/GPO/LPS32986"])

day(27,"battle","La Roche, Belgium","Highlanders enter La Roche",
"""At six this morning the 1st Battalion, Black Watch, of the 51st Highland Division moves past the roadblocks into La Roche, the old town in the Ourthe valley.

There is little German resistance. By eleven o'clock the town is free.

An American armored patrol meets the Highlanders by the bridge. Much of La Roche lies in ruins after weeks of bombing and shelling.""",
"""At 6 a.m. the 1st Black Watch of the 51st Highland Division moves into La Roche, in the Ourthe valley.

Resistance is light. By 11 the town is free, and an American patrol meets the Highlanders at the bridge.

Much of La Roche lies in ruins.""",
["Liberation Route Europe, British 51st Highland Division Memorial: https://italy.liberationroute.com/pois/1886/british-51st-highland-division-memorial","Liberation Route Europe, British M 10 Achilles Memorial, La Roche: https://liberationroute.com/pois/1867/british-m-10-achilles-memorial"])
D[27]["campaignsLine"]="Declass Campaigns opens Chapter 2 today: Hatten and Rittershoffen."

day(28,"state","Vistula River, Poland","The Soviets strike on the Vistula",
"""Far to the east, the Red Army opens its winter offensive. Marshal Ivan Konev's 1st Ukrainian Front attacks out of its bridgehead on the Vistula after a massive barrage.

Stalin had told the Allies the attack would come no later than the second half of January. It comes early.

For Hitler, the divisions he poured into the Ardennes are now needed in the East.""",
"""Far to the east, the Red Army opens its winter offensive. Konev's 1st Ukrainian Front attacks out of its Vistula bridgehead after a huge barrage.

Stalin told the Allies it would come no later than the second half of January. It comes early.""",
["U.S. State Department, FRUS, Malta and Yalta, Soviet account of the January offensive: https://history.state.gov/historicaldocuments/frus1945Malta/d330","Churchill Archive, Cambridge, Stalin's reply of 7 Jan 1945: https://archivesearch.lib.cam.ac.uk/repositories/9/archival_objects/1416421"])

day(29,"battle","Foy, Belgium","Paratroopers take Foy",
"""North of Bastogne, the village of Foy sits on the road to Noville and Houffalize. The 101st Airborne has faced it from the woods for weeks.

Today its paratroopers attack across the snow and take the village house by house.

The Germans want it back. They are already gathering infantry and tanks to counterattack.""",
"""North of Bastogne, Foy sits on the road to Noville and Houffalize. The 101st has faced it from the woods for weeks.

Today the paratroopers attack across the snow and take it house by house.

The Germans are already gathering to counterattack.""",
[M("pp. 40 to 41"),"Cirillo, Ardennes Alsace (CMH Pub 72 26): https://purl.fdlp.gov/GPO/LPS32986"])

day(30,"battle","Houffalize, Belgium","Two armies close on Houffalize",
"""From the north, the First Army's armor has cut the last good road out of Houffalize toward St. Vith. Tonight its men can see the flashes of the Third Army's guns to the south.

From the south, the Third Army pushes up the road from Bastogne.

Only a few miles of snow, forest and German rear guards now separate the two armies.""",
"""From the north, First Army armor has cut the last good road out of Houffalize. Its men can see the flashes of the Third Army's guns to the south.

Only a few miles of snow and German rear guards now separate the two armies.""",
[M("pp. 40 to 42"),"Cirillo, Ardennes Alsace (CMH Pub 72 26): https://purl.fdlp.gov/GPO/LPS32986"])
NARA="U.S. National Archives"
P={
1:("bu-01.jpg","Soldiers of the First Army, cut off from their regiment in the German drive, regroup in Bastogne, 19 December 1944. U.S. Army Signal Corps photo (111-SC-329951), "+NARA+". Public domain."),
2:("bu-02.jpg","German troops advance during the Battle of the Bulge, December 1944. German photo, captured, "+NARA+" (111-SC-341618)."),
3:("bu-03.jpg","A machine gunner of the 10th Armored Division stands guard in his camouflaged half track in Bastogne, 27 December 1944. U.S. Army Signal Corps photo (111-SC-204297), "+NARA+". Public domain."),
4:("bu-04.jpg","American prisoners of war marched along a road during the Battle of the Bulge, December 1944. German photo, captured, "+NARA+" (111-SC-341630)."),
5:("bu-05.jpg","General Bernard Montgomery and General Dwight D. Eisenhower in Normandy, 26 July 1944. U.S. Army Signal Corps photo (111-SC-192193), "+NARA+". Public domain."),
6:("bu-06.jpg","7th Armored Division Shermans near St. Vith, Belgium, January 1945. U.S. Army Signal Corps photo (111-SC-199467), "+NARA+". Public domain."),
7:("bu-07.jpg","Brig. Gen. Anthony C. McAuliffe at Bastogne, Belgium, 5 January 1945. U.S. Army photo, Harry S. Truman Library (63-518), "+NARA+". Public domain."),
8:("bu-08.jpg","Pathfinders of the 101st Airborne Division, dropped by parachute, set up radar equipment near Bastogne to guide the supply planes, 23 December 1944. U.S. Army Signal Corps photo (111-SC-222396), "+NARA+". Public domain."),
9:("bu-09.jpg","An American infantryman inspects a German 170 mm gun knocked out near Buissonville, Belgium, at the western tip of the Bulge, 29 December 1944. U.S. Army Signal Corps photo (111-SC-198339), "+NARA+". Public domain."),
10:("bu-10.jpg","Men of the 101st Airborne Division sing Silent Night at a midnight Christmas service in besieged Bastogne, 24 to 25 December 1944. U.S. Army Signal Corps photo (111-SC-200856), "+NARA+". Public domain."),
11:("bu-11.jpg","Lt. Col. Creighton Abrams, right, with men of his 4th Armored Division tank battalion and his Sherman, Thunderbolt VI, winter 1944 to 1945. U.S. Army Air Forces photo (342-FH-3A05217), "+NARA+". Public domain."),
12:("bu-12.jpg","Bomb damage in Bastogne after the siege, 26 December 1944. U.S. Army Signal Corps photo (111-SC-200481), "+NARA+". Public domain."),
13:("bu-13.jpg","Adolf Hitler. Photo from the Heinrich Hoffmann collection, captured German records, "+NARA+" (242-HF-0207-A)."),
14:("bu-14.jpg","An outpost on the road to Bastogne, 30 December 1944. U.S. Army photo (331-CA-6C-45-5241), "+NARA+". Public domain."),
15:("bu-15.jpg","Infantrymen attached to the 4th Armored Division fire on German troops in the drive to relieve Bastogne, 27 December 1944. U.S. Army Signal Corps photo (111-SC-199295), "+NARA+". Public domain."),
16:("bu-16.jpg","Troops of the 6th Armored Division change the track on a tank near Bastogne, January 1945. U.S. Army Signal Corps photo (111-SC-339198), "+NARA+". Public domain."),
17:("bu-17.jpg","A Ninth Air Force P 38 comes in to land at a forward airfield in Belgium, winter 1944 to 1945. U.S. Army Air Forces photo (342-FH-3A05252), "+NARA+". Public domain."),
19:("bu-19.jpg","3rd Armored Division tanks wait on a snow covered road in Belgium, 7 January 1945. U.S. Army Signal Corps photo (111-SC-334034), "+NARA+". Public domain."),
20:("bu-20.jpg","Troops of the 17th Airborne Division move up over snow covered roads near Houffalize, Belgium, 21 January 1945. U.S. Army Signal Corps photo (111-SC-253918), "+NARA+". Public domain."),
23:("bu-23.jpg","General Bernard Montgomery boards a warship off the Normandy coast, 8 June 1944. U.S. Army Signal Corps photo (111-SC-190370), "+NARA+". Public domain."),
24:("bu-24.jpg","German troops in Belgium during the Battle of the Bulge. German photo, captured, "+NARA+" (111-SC-198252)."),
25:("bu-25.jpg","An American soldier keeps watch while his buddy sleeps, Houffalize sector, Belgium, 16 January 1945. U.S. Army Signal Corps photo (111-SC-411912), "+NARA+". Public domain."),
26:("bu-26.jpg","Infantrymen of the 87th Division enter St. Hubert, Belgium, right after the Germans left, January 1945. U.S. Army Signal Corps photo (111-SC-199207), "+NARA+". Public domain."),
27:("bu-27.jpg","Ruins of La Roche, Belgium, after the battle, early 1945. U.S. Army Air Forces photo (342-FH-3A05383), "+NARA+". Public domain."),
29:("bu-29.jpg","S/Sgt. Harold J. Sloan of the 101st Airborne Division fills his canteen cup with snow in the Belgian forest, 11 January 1945. U.S. Army Signal Corps photo (111-SC-198702), "+NARA+". Public domain."),
30:("bu-30.jpg","Shell damage in Houffalize, Belgium, January 1945. U.S. Army Signal Corps photo (111-SC-199265), "+NARA+". Public domain."),
}
TIER={k:("yellow" if "captured" in v[1] else "green") for k,v in P.items()}
TEXT={}
for n,d in D.items():
    foot=f"Campaign Series: The Bulge · Day by Day · Day {n} of 30"
    t=dict(series=d["series"],place=d["place"],subtitle=d["subtitle"],body=d["body"].strip(),threads=d["threads"].strip()+"\n\n"+foot,footer=foot,
           hashtags="#OnThisDay #WW2 #BattleOfTheBulge",hashtags_xf="#OTD #WW2 #BattleOfTheBulge",sources=d["sources"],
           bookLine="Follow the whole campaign, day by day: ww2dispatches.com/campaign-series/bulge-1944",bookLineIG="The whole campaign, day by day: link in bio.")
    if d.get("somber"): t["somber"]=True
    if d.get("campaignsLine"): t["campaignsLine"]=d["campaignsLine"]
    if n in P:
        t["photo"]="photos/campaign/"+P[n][0]; t["photoCredit"]=P[n][1]; t["photoNote"]="tier "+TIER[n]
        t["alt"]=f"WW2 Dispatches Campaign Series, The Bulge, Day {n}. "+P[n][1]; t["focusX"]=50; t["focusY"]=50
    else:
        t["photo"]=None; t["photoNote"]="TO CHOOSE"
    TEXT[n]=t

TEXT[11].update(zoom=112,focusX=72,focusY=60); TEXT[17].update(zoom=125,focusY=62); TEXT[27].update(zoom=140,focusX=45,focusY=68)
P2={18:("bu-18.jpg","James F. Byrnes, who as Director of War Mobilization asked the nation's racetracks to close, about 1941 to 1942. Harris and Ewing photo, Library of Congress (cph.3c32232). Public domain."),
22:("bu-22.jpg","Stalin, Roosevelt and Churchill at the Tehran Conference, November 1943. U.S. Army Signal Corps photo, Library of Congress (cph.3c35324). Public domain.")}
for n,(f,c) in P2.items():
    TEXT[n].update(photo="photos/campaign/"+f,photoCredit=c,photoNote="tier green",alt=f"WW2 Dispatches Campaign Series, The Bulge, Day {n}. "+c,focusX=50,focusY=40,zoom=(110 if n==18 else 100))
