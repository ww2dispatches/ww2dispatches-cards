# WW2 Dispatches: Film Library

What film we already have, exactly where the usable shots are, and where to look for more. **The Wednesday research run checks this doc before every film hunt** (Research doc), the Thursday video runs (noon and evening) use its times to cut, and Claude in the Project uses it to cut `needs brian` Living Cards from Source Film. The rules for turning film into videos are in the Videos doc.

Every film here has a full index in its own Project doc under `claude/film-index/` (sequence by sequence, best shots with exact times, dates it can serve, and what not to use). Copies of the indexes are also in Brian's WW2 Dispatches\Film Library folder. This doc is the summary and the calendar.

## How to use it
1. **Find the date** in the Calendar below. It names the film, the shot, and the time.
2. **Open that film's index** for the exact cut times, the opening frame, and the cautions.
3. **Get the film:**
   * **Cloud copy (NARA):** download the reel MP4 and upload it to `footage/` on Cloudflare R2 with `python3 renderer/media.py put footage/<file>` (Research doc, "Securing the film"). Any scheduled run can do this; a Project chat, which can't reach R2, commits it to the videos repo's `inbox/` and the next run's media sweep moves it (Videos doc, "Where videos live").
   * **Source Film only** (Desert Victory, Tarawa, New Britain, and every Soviet film): mark the day `needs brian` and name the file and times, so the cut in the Project takes minutes.
   * Where both exist, the NARA reel is the working copy. The Source Film copy is the same film, sometimes sharper, for a final cut in the Project when it matters (a Flash day).
4. **Mind the timeline.** Each index says which copy its times use (the Source Film file, or the NARA reel, "R3 01:01" meaning Reel 3 at 1 min 1 s). Times in another copy of the same film will drift.
5. **Sound:** these films carry narration and score over almost everything, so **every clip runs silent by default.** The few natural sound stretches are listed per film; they were found with spectrograms, so listen before keeping any sound (Videos doc, Living Cards).
6. **Caption honestly:** say whose camera it was when it isn't American ("Soviet film of the Ladoga ice road", "Japanese Navy film of the launch"), and say so when the film is from a few days around the event (the Aachen rule). Never caption a composite or generic shot as one dated event.
7. **Lens:** the daily 2:30 p.m. Axis card and its film (Research doc, "Picking the events" and the 7 p.m. video order) lean on this library, and so does any Eastern Front story. Soviet films serve the Eastern Front; captured Japanese film, the German side pack, the German military packs (Cologne, Brest, the Ruhr prisoners, German leaders in custody, the U-boat surrenders, the Me 262 jets), Trophies of Great Battles, and the Me 262 film serve Axis lens cards.

## On hand
**American and British films**
| Film | Covers | Copies | Times use | Index |
|---|---|---|---|---|
| **The Battle of Russia** (1943, U.S. War Department, Why We Fight 5, 2 parts) | Eastern Front 1941 to Feb 1943: 22 June 1941, scorched earth, partisans, Moscow counteroffensive, liberated towns, Leningrad siege and ice road, Stalingrad, Paulus and the prisoners | Source Film (Part 1 and Part 2 webm) and NARA 111-OF-5 (naId 36071, 8 reels) | Source Film, Part 1 or Part 2 | `claude/film-index/battle-of-russia.md` |
| **The Battle of China** (1944, U.S. War Department, Why We Fight 6) | Shanghai 1937, the Panay, Nanking, the trek west, Chungking bombing, the Burma Road, Flying Tigers, Changsha, the Hump, Madame Chiang to Congress | NARA 111-OF-6 (naId 36072, 7 reels) | NARA reel | `claude/film-index/battle-of-china.md` |
| **Know Your Enemy: Japan** (1945, U.S. War Department) | Japanese actuality: Hirohito, the 1940 Kigen 2600 celebration, the Diet, war industry, troops in China, the Bataan and Corregidor surrenders (Japanese film) | NARA 111-OF-10 (naId 36076, 2 reels) | NARA reel | `claude/film-index/know-your-enemy-japan.md` |
| **The Battle of Midway** (1942, U.S. Navy, John Ford, color) | The 4 June 1942 raid on Midway Island, filmed from the island; PBYs and B-17s; rescue and funeral | Source Film (80-MN-1433.wmv) and NARA naId 12870 | Source Film | `claude/film-index/battle-of-midway.md` |
| **Lexington at Coral Sea** (1942, U.S. Navy, silent) | USS Lexington burning, 8 May 1942, long shots | NARA naId 80274 (**Restricted, Possibly**; check before use) | NARA file | `claude/film-index/lexington-coral-sea.md` |
| **Doolittle Raid launch** (1942, U.S. Navy, silent) | Task Force 16 at sea and the B-25 launch from the Hornet, 18 Apr 1942 | NARA naId 81418 | NARA file | `claude/film-index/doolittle-raid-takeoff.md` |
| **Attack! The Battle for New Britain** (1944, U.S. War Department) | Arawe 15 Dec 1943 and Cape Gloucester 26 Dec 1943; the USS Brownson sinking | **Source Film only** (.ogv) | Source Film | `claude/film-index/attack-new-britain.md` |
| **With the Marines at Tarawa** (1944, USMC, color) | Betio, 20 to 23 Nov 1943 | **Source Film only** (full webm for final cuts, 480p for indexing; same timeline) | Source Film | `claude/film-index/marines-at-tarawa.md` |
| **Brought to Action** (1945, OSS and U.S. Navy, B&W) and **Over the Hump** (reel 3) | Leyte landings and Leyte Gulf, 20 to 26 Oct 1944; CBI 1944 | NARA naId 35899 (3 reels) | NARA reel | `claude/film-index/brought-to-action.md` |
| **Iwo Jima flag raising** (1945, USMC, Genaust's color film, silent) | The second flag raising on Suribachi, 23 Feb 1945 | NARA naId 76433 (Unrestricted) | NARA file | `claude/film-index/iwo-jima-flag-raising.md` |
| **Desert Victory** (1943, British Ministry of Information) | El Alamein and the pursuit to Tripoli, Aug 1942 to Jan 1943 | **Source Film only** (480p webm) | Source Film | `claude/film-index/desert-victory.md` |
| **Tunisian Victory** (1944, U.S. Signal Corps and British AFPU) | Torch to the Axis surrender in Tunisia, Nov 1942 to May 1943; Casablanca | NARA 111-M-1012 (naId 35846, 8 reels) and Source Film | NARA reel | `claude/film-index/tunisian-victory.md` |
| **The Memphis Belle** (1944, USAAF, William Wyler, color) | 8th Air Force bombers over Europe, 1943 | NARA 330-DVIC-26134 (naId 4523496) and Source Film | NARA file | `claude/film-index/memphis-belle.md` |
| **The True Glory** (1945, U.S. OWI and British MOI) | D Day to the fall of Germany, 1944 to 1945 | NARA 111-M-1211 (naId 4597331, 9 reels) and Source Film | NARA reel | `claude/film-index/true-glory.md` |
| **Why We Fight 4: The Battle of Britain** (1943) | Dunkirk to the Blitz: Home Guard, Hurricanes scrambling, RAF gun camera, 15 Sep, Coventry, St Paul's | NARA 111-OF-4 (naId 36070, 6 reels) | NARA reel | `claude/film-index/battle-of-britain.md` (about a third German film, flagged) |
| **The Enemy Strikes** (1945, Army) and two **Signal Corps Bulge reels** | Battle of the Bulge: withdrawal, skies clear, winter line; Malmedy area and the Bastogne "Battered Bastards" sign | NARA 111-M-1130 (naId 35885); 111-ADC-9670, 111-ADC-3167 | NARA file | `claude/film-index/the-enemy-strikes.md`, `bulge-signal-corps-reels.md` |
| **Pearl Harbor damage** (Navy, Dec 1941) | Aftermath from boats: Arizona's collapsed superstructure, cage mast battleships, a capsized hull | NARA 428-NPC-16003 (naId 80259) | NARA file | `claude/film-index/pearl-harbor-damage.md` |
| **Anzio invasion** (Navy, 22 Jan 1944) and **Cassino** (Signal Corps, Mar 1944) | Shingle landings and bombardment; the abbey and town before the March bombing | NARA 428-NPC-1606; 111-ADC-813 | NARA file | `claude/film-index/anzio-invasion.md`, `cassino-1944.md` |
| **Yalta Conference** (5 reels) and **Potsdam Conference** (4 reels) | The Big Three seated, Livadia; Truman, Churchill, Stalin at Potsdam, Truman's Berlin flag raising speech with live sound | NARA 111-ADC-9700 to 9702, 3249, 428-NPC-7634; 111-ADC-9854, 9857, 9859, 9860 | NARA file | `claude/film-index/yalta-conference.md`, `potsdam-conference.md` (much is Paramount newsreel, rights caution) |
| **U-505 capture** (Navy, 4 Jun 1944) | The boarded U-boat, German prisoners on USS Pillsbury, the interior | NARA 428-NPC-7980, 428-NPC-12746 | NARA file | `claude/film-index/u-505-capture.md` |
| **Okinawa action** (6th Marine Division, 12 to 13 May 1945) | Edge of Naha, Shermans, white phosphorus | NARA 428-NPC-13037, 13038 | NARA file | `claude/film-index/okinawa-action.md` |
| **San Francisco, 1945** (UN conference) | 25 Apr opening, 25 Jun vote, 26 Jun Charter signing, Truman | NARA 111-OF-30 (naId 36088) | NARA reel | `claude/film-index/san-francisco-1945.md` |
| **Missouri surrender** (Navy, 2 Sep 1945) | Japanese delegation boards, Shigemitsu, MacArthur, the signings (no flyover) | NARA 428-NPC-14504 (naId 79766) | NARA file | `claude/film-index/missouri-surrender.md` |
| **Tarawa Navy reels** | Color camera original behind With the Marines at Tarawa, plus Betio under bombardment and amtrac 67; a cloud copy for Tarawa | NARA 428-NPC-12205 (15768 is a rehearsal) | NARA file | `claude/film-index/tarawa-navy-reels.md` |
| **Wake raid and Santa Cruz** (Navy) | Oct 1943 Wake bombardment; Hornet survivors, Oct 1942 | NARA 428-NPC-13397 | NARA file | `claude/film-index/wake-santa-cruz-reel.md` |

**Axis lens: the enemy on film without enemy newsreel**
| Film | Covers | Copies | Times use | Index |
|---|---|---|---|---|
| **Captured Japanese film** (Nippon Eigasha newsreels and Navy film, 1937 to 1943, 8 reels) | Pearl Harbor from the carriers, 8 Dec in Tokyo, Guam and Wake, Lae, the Andamans, Colombo, the China war | NARA only (428-NPC reels and two Universal outtakes) | NARA reel | `claude/film-index/japanese-captured-film.md` |
| **German side, Allied cameras** (8 NARA reels) | Reims surrender with Jodl (111-ADC-9759); Wismar and the Karlshorst surrender with Keitel (111-ADC-1919); Nuremberg: the 1948 film (111-M-7596, 8 reels), the judgment roll with live courtroom sound (111-ADC-10021), Göring on the stand (208-UN-202); U-570 as HMS Graph (428-NPC-16294); two Welt im Film reels | NARA only | NARA file | `claude/film-index/german-side-allied-film.md` (part 1) and `german-side-allied-film-2.md` (Wismar, Karlshorst, U-570, World in Film 43, leads) |
| **Trophies of Great Battles** (1943, Soviet, color) | Captured German weapons in Gorky Park: Tiger, Ferdinand, Bf 109, Nebelwerfer, Flak | Source Film | Source Film | `claude/film-index/trophies-of-great-battles.md` |
| **Nine War Gods** (captured Japanese newsreel, 1942) | Portraits of the nine midget submarine crewmen of 7 Dec; the capture of Hong Kong | NARA 428-NPC-10134 (naId 78848) | NARA file | `claude/film-index/nine-war-gods.md` |
| **The Me 262** (1945, Soviet evaluation film) | The German jet fighter in detail and in flight | Source Film | Source Film | `claude/film-index/me-262-soviet-film.md` |
| **Cologne, March 1945** (5 Signal Corps reels) | Pulheim to Cologne 5 Mar, German soldiers surrendering with hands up, captured officers, M26 Pershings passing white flags, the cathedral spires, Neuss under Military Government; German prisoners with a war dog, 6 Mar. **The cathedral tank duel is not in any of them.** | NARA 111-ADC-1955, 3508, 9703; 9704, 3535 | NARA file | `claude/film-index/cologne-march-1945.md`, `cologne-captured-1945.md` |
| **Surrender of Brest** (Signal Corps, 18 Sep 1944) | A German paratroop colonel with the Knight's Cross surrenders face to face, hundreds of prisoners, the fortress and abandoned German stores | NARA 111-ADC-2350 | NARA file | `claude/film-index/brest-surrender.md` |
| **Seine crossing and Aachen** (Signal Corps, Aug and Oct 1944) | German ammunition truck exploding, Montereau crossing under fire, Brest refugees; Aachen street fighting 15 Oct, Nazi newspaper sign, German prisoners (one stretch graphic) | NARA 111-ADC-2245; 111-ADC-2655 | NARA file | `claude/film-index/seine-crossing-august-1944.md`, `aachen-fall.md` |
| **German prisoners, 1945** (3 Signal Corps reels) | Ruhr pocket: a German column driving itself into captivity, thousands in a field, three generals; German horse cavalry and wagons, a Red Cross nurse with boy soldiers; Roetgen boy soldiers, Feb 1945 | NARA 111-ADC-3341, 4204, 3281 | NARA file | `claude/film-index/german-prisoners-1945.md` |
| **Tunisia 1943, Tiger wrecks in Italy, Remagen** (Signal Corps) | Captured 88 and Axis prisoners, Eisenhower (Feb 1943); two knocked out Tiger I tanks, turret 33 (late Jun 1944); Remagen bridge 9 Mar 1945, "Cross the Rhine with dry feet", Churchill at Julich | NARA 111-ADC-1954; 1326; 3612 | NARA file | `claude/film-index/tunisia-tank-action-1943.md`, `massa-marittima-german-wrecks.md`, `remagen-bridgehead.md` |
| **Reims surrender** (Signal Corps, 7 May 1945) | Jodl signing, Bedell Smith, Susloparov, the pens; **Eisenhower's victory statement with live sound** | NARA 111-ADC-9759 | NARA file | `claude/film-index/german-surrender-reims.md` (fuller than the GS pack entry) |
| **German leaders in custody** (3 Signal Corps reels, May 1945) | Goering at Kitzbuhel and Seventh Army, then at his press conference; Kesselring laughing with Maxwell Taylor; the Zell am See contact convoy | NARA 111-ADC-4420, 9795, 4326 | NARA file | `claude/film-index/german-leaders-captured-1945.md` (Mauthausen stretch in 4326, never) |
| **Luftwaffe's end and the V-2** | Me 262 jets abandoned at Innsbruck on VE Day, engine and cannon open, German explosive motorboats; USAAF gun camera Fighter Kills Sep to Dec 1944 (Fw 190, Bf 109, Me 163, Me 262; two German camera stretches flagged); a V-2 launch at White Sands in color, 1946 | NARA 111-ADC-4524; 111-ADC-10508; 428-NPC-10804 | NARA file | `claude/film-index/luftwaffe-jets-innsbruck.md`, `fighter-kills-eto.md`, `v2-tests-white-sands.md` |
| **U-boat surrenders, May 1945** (5 Navy reels) | U-858 off Cape May and her crew landed at Fort Miles, 14 May; U-873 under the U.S. flag over the black flag off the Azores, 11 May; U-805's crew at Portsmouth, 15 May; an unidentified boat from the air | NARA 428-NPC-12592, 12132, 12102; 7860, 7853 | NARA file | `claude/film-index/u-boat-surrenders-may-1945.md`, `u-boat-surrender-azores.md` |
| **Siegfried Line** (Navy camera, slated 22 Sep 1944) | Low aerials along the dragon's teeth, a shell pocked pillbox, bunkers, wire | NARA 428-NPC-13442 | NARA file | `claude/film-index/siegfried-line-navy-reel.md` |

**Soviet films (Eastern Front; all Commons PD-Russia-1996)**
| Film | Covers | Copies | Times use | Index |
|---|---|---|---|---|
| **Leningrad Fights** (1942) | 22 June 1941 to spring 1942: militia, the blockade, the starvation winter, the ice road, trams again | Source Film (480p) | Source Film | `claude/film-index/leningrad-fights.md` |
| **Red Square parade, 7 Nov 1941** | The parade held with the front near Moscow | Source Film (.ogv) | Source Film | `claude/film-index/red-square-parade-1941.md` |
| **Victory in Right Bank Ukraine** (1945) | Dnieper 1943, Kyiv, Korsun, Uman, Odessa, Lviv | Source Film (480p) | Source Film | `claude/film-index/victory-right-bank-ukraine.md` |
| **The Battle for Sevastopol** (1944) | Crimea, Apr to May 1944 | Source Film (**reference only**: a 2013 IHF transfer with a © card, burned in subtitles and a logo; picture only, cropped, and only if no other copy turns up) | Source Film | `claude/film-index/battle-for-sevastopol.md` |
| **Berlin** (1945) | Oder barrage 16 Apr 1945 to Karlshorst and Victory Day | Source Film | Source Film | `claude/film-index/berlin-1945.md` |
| **Victory Parade, 24 Jun 1945** | Red Square parade, Zhukov and Rokossovsky | Source Film (poor B&W copy, 384x288, ЦСДФ watermark and a TV logo to crop; the original was color, find a better copy) | Source Film | `claude/film-index/victory-parade-1945.md` |
| **Defeat of the German Armies near Moscow** (1942, Oscar winner as Moscow Strikes Back) | Moscow besieged Oct 1941, the 6 Dec counteroffensive, Istra, Klin, Kalinin, Volokolamsk, Mozhaisk | Source Film (240p for indexing, 480p for final cuts; same timeline) | Source Film | `claude/film-index/moscow-1942.md` |
| **Stalingrad** (1943, text by Vasily Grossman, read by Levitan) | 23 Aug 1942 bombing, street fighting, Volga crossings, Uranus, Kalach, Operation Ring, Paulus, the surrender | Source Film (240p for indexing, 480p for final cuts; same timeline) | Source Film | `claude/film-index/stalingrad-1943.md` |

## Calendar
Usable shots by calendar day across every film on hand. "Verify" means the film doesn't state the day and it comes from the general record. Ranges marked "any date" can serve any day in that span. Full times and cautions are in each index. Short names: BoR (Battle of Russia), BoC (Battle of China), KYEJ (Know Your Enemy: Japan), LF (Leningrad Fights), MOS (Defeat near Moscow), STG (Stalingrad), RBU (Victory in Right Bank Ukraine), GS (German side pack).

**January**
* **22 Jan 1944, Anzio landings:** Anzio reel 00:10:30 to 00:10:50 (cruiser and landing craft), 00:09:56 to 00:10:08, 00:08:11 to 00:08:28.
* 17 Jan 1944, First Battle of Cassino opens: Cassino reel 00:00:18 to 00:00:29 (the abbey, early 1944).
* 16 to 18 Jan 1945, Houffalize link up; Bastogne returned to the Belgians, the "Battered Bastards" sign (filmed 18 Jan): Bulge Signal Corps reel 111-ADC-3167 00:06:55 to 00:06:59.
* 1 Jan 1943, Moscow New Year in wartime: BoR Part 2 00:39:04 to 00:40:22.
* 10 Jan 1943 onward, final assault on the Stalingrad pocket: BoR Part 2 00:40:22 to 00:42:12; Operation Ring, STG 00:52:25 to 00:54:50 (Katyusha salvo 00:53:28).
* 8 Jan 1943, the ultimatum to Paulus; trumpeter and envoys: STG 00:52:06 to 00:52:18.
* 20 Jan 1942, Mozhaisk retaken: MOS 01:05:09 to 01:07:30.
* 26 Jan 1943, the Stalingrad pocket split (verify): STG 01:02:02 to 01:02:50.
* 14 to 24 Jan 1943, Casablanca Conference: Tunisian Victory R5 04:28 to 06:09.
* 18 Jan 1943, Operation Iskra; first Tiger captured near Leningrad (verify): Trophies 00:07:00 to 00:07:45.
* 23 Jan 1943, Eighth Army enters Tripoli (verify): Desert Victory 00:57:24 to 00:59:15.
* 24 Jan to 17 Feb 1944, Korsun Cherkassy pocket (verify): RBU 00:22:09 to 00:24:20.
* 26 Jan 1942 and after, GIs arrive in Britain: True Glory R1 00:06:06 to 00:06:48.
* 27 Jan 1943, first USAAF heavy bomber raid on Germany (generic bombers): Memphis Belle 00:12:45 to 00:14:15.
* 27 Jan 1944, Leningrad siege lifted: LF best shots 1 to 4 as a looking back post; BoR Part 2 00:18:21 to 00:20:20.
* 31 Jan 1943 (Stalingrad Flash day from 2027), Paulus surrenders: BoR Part 2 00:42:59 to 00:43:55; STG 01:06:38 to 01:07:58 (Paulus and Schmidt before Soviet officers, posed after the capture; say so).
* 12 Jan, 28 Jan, 4 Feb 1945, Ledo Road opens through to China: Brought to Action R3 01:58 to 02:17; BoC R7 04:06 to 04:22.

**February**
* 4 to 11 Feb 1945, Yalta: the seated Big Three, 111-ADC-9701 00:04:03 to 00:04:18 and 00:03:01 to 00:03:17; Roosevelt close up 111-ADC-9700 00:00:26 (Paramount newsreel camera, rights caution; see the index).
* 15 to 18 Feb 1944, Cassino (the abbey before and the town assaults, not the bombing itself): Cassino reel 00:00:43 to 00:00:52, 00:06:24 to 00:06:42.
* 3 Feb 1945, boy soldiers taken prisoner at Roetgen (Axis lens, Home Front angle): German prisoners 1945, 111-ADC-3281 04:14 to 04:21 (a very young prisoner staring into the lens), 03:34 to 03:50.
* 2 Feb 1943, Stalingrad ends; ruins, prisoner columns: STG 01:07:58 to 01:08:18 (POW columns), 01:13:42 to 01:13:56 (lone prisoner on the Volga ice), 01:03:05 to 01:03:37 (the silence); BoR Part 2 00:42:12 to 00:44:43.
* 4 Feb 1943, victory rally in Stalingrad (verify): STG 01:11:00 to 01:13:28.
* 3 Feb to 3 Mar 1945, Battle of Manila (aerial of the ruined city only): KYEJ R2 27:30 to 27:40.
* 4 to 11 Feb 1945, Yalta: True Glory R8 00:04:45 to 00:04:56.
* 8 Feb 1945, Reichswald: True Glory R8 00:05:12 to 00:06:45.
* 8 Feb 1946, Soviet case opens at Nuremberg: GS, Nuremberg 1948 film R4 00:06:28 to 00:07:40.
* 18 Feb 1943, Madame Chiang addresses Congress, in her own voice: BoC R7 07:04 to 07:19.
* 18 Feb 1938 onward, bombing of Chungking: BoC R5 02:56 to 03:19, 03:44 to 03:58, 04:10 to 04:50.
* **19 Feb 1945 (Iwo Jima Flash day):** Iwo Jima reel 00:01:05 to 00:01:20 (LSTs on the beach, filmed from Suribachi on D+4; say so) and 00:01:29 to 00:01:41, flag raising as the payoff at 00:01:41.
* 19 Feb 1942, Darwin raid (generic, Japanese side): Japanese film naId 2521264 00:03:03 to 00:05:35.
* 19 to 25 Feb 1943, Kasserine Pass: no battle footage on hand. For "Tunisia that month": Tunisia tank reel 111-ADC-1954, captured 88 00:01:15 to 00:01:24, Axis prisoner column 00:03:51 to 00:04:10, Eisenhower 00:06:36 to 00:07:12.
* **23 Feb 1945, the flag raising on Suribachi, color:** Iwo Jima reel 00:01:41.0 to 00:02:16 (Genaust's film of the second flag; the first flag is not on film).
* 26 Feb 1943, Wilhelmshaven (composite; verify): Memphis Belle 00:18:30 to 00:23:40.

**March**
* 6 Mar 1943, Medenine: Tunisian Victory R5 09:00 to 09:12.
* 3 Mar 1945, Churchill visits Julich with Montgomery and Brooke: Remagen reel 111-ADC-3612 00:07:45 to 00:08:30. 3 to 6 Mar, U.S. Ninth Army meets the British near Geldern: same reel 00:10:03 to 00:10:20, 00:12:39 to 00:12:57.
* 5 Mar 1945, 3rd Armored drives from Pulheim to Cologne; German soldiers walk in with hands up: Cologne 111-ADC-1955 04:36 to 04:51, 05:03 to 05:17; two captured German officers, 111-ADC-3508 05:15 to 05:22.
* **6 Mar 1945, Cologne:** True Glory R8 00:07:12 to 00:07:30; armor toward the cathedral, Cologne captured 111-ADC-9704 06:15 to 06:30 (best cathedral shot); German prisoners in greatcoats with a war dog, 111-ADC-3535 01:24 to 01:37. The Pershing versus Panther duel is not on any reel we have.
* **7 Mar 1945 (Remagen Flash day from 2027):** True Glory R8 00:08:30 to 00:09:07; the "Cross the Rhine with dry feet" sign on the bridge tower, Remagen reel 111-ADC-3612 00:03:50 to 00:04:06 and infantry onto the bridge 00:03:39 to 00:03:50 (filmed 9 Mar; say so).
* 8 to 16 Mar 1945, German air attacks on the Remagen bridge: quad .50s firing, 111-ADC-3612 00:03:06 to 00:03:20 (no German plane is in frame).
* 17 Mar 1945, Ludendorff bridge collapses: the bridge on 9 Mar as a "days before" image, 111-ADC-3612 00:01:48 to 00:01:56.
* 8 Mar 1942, Japanese landings at Lae and Salamaua: Japanese film naId 2521264 00:00:15 to 00:02:45.
* 10 Mar 1944, Uman taken (verify): RBU 00:24:20 to 00:25:20.
* 13 to 22 Mar 1946, Göring on the stand at Nuremberg: GS 208-UN-202 00:00:21 to 00:02:20 (live exchange with Jackson 00:00:58 to 00:01:41, may keep its sound; United News, second choice after the Army film); GS 1948 film R7 00:01:12 to 00:02:10.
* 15 Mar 1945, With the Marines at Tarawa wins the Academy Award (verify): Tarawa title cards 00:00:08 to 00:00:29 or any best shot.
* 20 to 28 Mar 1943, Mareth Line: Tunisian Victory R6 00:57 to 01:30, 03:39 to 04:30.
* 23 Mar 1942, Andamans occupied: Japanese film naId 2521264 00:05:55 to 00:07:05.
* 23 to 24 Mar 1945, Rhine crossings and Varsity: True Glory R8 00:09:09 to 00:10:27.
* 26 Mar 1945, Iwo Jima secured: Iwo Jima reel 00:01:47 to 00:02:02.

**April**
* 25 Apr 1945, UN conference opens in San Francisco: San Francisco 1945 R1 04:37 to 04:56.
* 12 to 14 Apr 1945, mourning Roosevelt (somber): San Francisco 1945 R1 03:30 to 04:16.
* 5 Apr 1942, Colombo raid: Japanese film naId 2521264 00:07:33 to 00:10:35.
* 7 Apr 1943, U.S. and Eighth Army link up: Tunisian Victory R6 07:18 to 07:28.
* 8 Apr 1944, Crimean offensive opens (Sevastopol, reference only): 00:07:30 to 00:08:30.
* 9 to 10 Apr 1942, Bataan surrender and the march, Japanese film: KYEJ R2 25:58 to 27:06 (label Japanese film).
* 10 Apr 1944, Odessa liberated: RBU 00:27:49 to 00:28:15.
* 12 Apr 1945, freed POWs hear of Roosevelt's death: True Glory R9 00:01:00 to 00:01:12.
* 15 Apr 1942, Leningrad trams run again (verify): LF 01:05:00 to 01:06:45; BoR Part 2 00:26:16 to 00:26:34.
* 15 Apr 1945, Belsen (somber only): True Glory R9 00:02:00 to 00:03:36.
* 16 Apr 1945, the Oder barrage, **natural battle sound 00:15:00 to 00:16:57** (listen first): Berlin 00:12:45 to 00:13:50, 00:15:06 to 00:18:00.
* 11 to 18 Apr 1945, the Ruhr pocket surrenders (Axis lens): a German column of half tracks, trucks and Kübelwagens drives itself into captivity, German prisoners 1945, 111-ADC-3341 03:34 to 03:53; thousands in a field 06:38 to 07:21; three generals 08:19 to 08:47 (names are the shot card's, verify).
* 16 Apr 1945, German generals and troops taken near Müden (place per card, verify): 111-ADC-4204, horse cavalry and farm wagons 01:57 to 02:07, a German Red Cross nurse with boy soldiers 02:28 to 02:39, generals 04:54 to 05:03.
* 16 Apr 1946, first V-2 fired at White Sands: V-2 reel 428-NPC-10804 00:03:47 to 00:03:59, corkscrew trail 00:04:14 to 00:04:33 (a 1946 launch, exact flight not identified).
* **18 Apr 1942 (Doolittle Flash day from 2027):** Doolittle reel 00:07:55 to 00:07:59, 00:08:00 to 00:08:14, best 00:09:06 to 00:09:19 (B-25s overhead; the Hornet takeoffs themselves are specks in rain).
* 19 Apr 1945, Seelow Heights: Berlin 00:18:12 to 00:20:45.
* 20 Apr 1943, Enfidaville: Tunisian Victory R6 08:03 to 08:54.
* 21 Apr 1942, last day of the Ladoga ice road (sources differ, verify): LF 01:01:00 to 01:02:15.
* 21 Apr 1945, Soviets reach Berlin: Berlin 00:22:35 to 00:24:00.
* 23 Apr to 3 May 1943, Hill 609 (day shots only): Tunisian Victory R7 04:09 to 04:57, 06:33 to 06:48.
* 25 Apr 1945, Berlin encircled: Berlin 00:24:45 to 00:28:22. Elbe link up: True Glory R9 00:04:30 to 00:05:14.
* 29 Apr, Emperor's birthday: KYEJ R1 06:40 to 07:02, 08:36 to 08:46 (Hirohito on his white horse); Japanese film UN-UN-4901x3 00:02:50 to 00:05:10 (status flagged).
* 30 Apr 1945, Reichstag stormed (real shelling only; the flag scenes are restaged): Berlin 00:39:51 to 00:40:24.

**May**
* 12 to 13 May 1945, Marines at the edge of Naha, Okinawa (dated by camera slates): Okinawa reels R1 00:33 to 00:50, R1 06:41 to 07:22, R2 07:05 to 07:18.
* 2 May 1945, Berlin garrison surrenders: Berlin 00:41:20 to 00:43:15.
* 4 May 1945, Lueneburg Heath (not named): True Glory R9 00:05:15 to 00:05:36.
* 6 May 1942, Corregidor surrender, Japanese film (some shots may be restaged by Japanese cameramen): KYEJ R2 25:18 to 25:58.
* 6 May 1943, final offensive in Tunisia: Tunisian Victory R7 07:06 to 08:54, R8 00:06 to 02:00.
* **7 May 1945, Reims, Jodl signs:** GS 111-ADC-9759, Jodl at 00:00:59; fuller index in `german-surrender-reims.md`: Jodl signs 01:01 to 01:20, his face 01:45 to 02:03, Bedell Smith 02:06 to 02:20, the pens 06:12 to 06:30. Same day, Montgomery and Rokossovsky at Wismar: GS 111-ADC-1919 00:00:08 to 00:03:15.
* 7 May 1943, Tunis and Bizerte fall: Tunisian Victory R8 03:04 to 03:22.
* 7 May 1944, Sapun Gora stormed (Sevastopol, reference only): 00:23:41 to 00:30:09.
* **7 to 8 May 1945 (VE Day Flash day):** True Glory R9 00:06:30 to 00:07:21; Eisenhower's own statement with live sound, GS 111-ADC-9759 00:03:27 to 00:04:39; **Keitel signing at Karlshorst**, GS 111-ADC-1919 00:05:27 to 00:08:50 (Keitel 00:06:15) and Berlin 00:56:45 to 01:00:00.
* **8 May 1942, Coral Sea, Lexington lost:** Lexington reel 00:00:41 to 00:00:53 (check the rights flag first).
* 8 May 1945, the Luftwaffe's end: Me 262 jets abandoned at Innsbruck on VE Day, 111-ADC-4524 00:00:30 to 00:00:47, 00:01:47 to 00:01:59.
* 8 to 9 May 1945, Goering gives himself up to the 36th Division and is brought to Seventh Army: German leaders 111-ADC-4420 00:42 to 00:51 (Kitzbuhel), 02:33 to 02:54 (big close up and decorations).
* 9 to 10 May 1945, Kesselring in U.S. custody, laughing with Maxwell Taylor at Berchtesgaden: 111-ADC-9795 03:45 to 03:59 (first choice), 111-ADC-4326 05:58 to 06:16.
* 11 May 1945, U-873 surrenders off the Azores (per Coast Guard records), the U.S. flag over the black flag: U-boat Azores reel 428-NPC-7860 00:06:32 to 00:06:38, 00:06:39 to 00:06:57.
* 11 May 1945, Goering's press conference (NARA says 15 May, verify): 111-ADC-9795 01:42 to 02:00, 00:57 to 01:12.
* 9 May 1945, Soviet Victory Day: Berlin 01:01:15 to 01:02:44; GS 111-ADC-1919 00:06:15.
* 9 and 12 May 1944, Sevastopol liberated; last Germans surrender at Chersonese (reference only): 00:30:42 to 00:31:30, 00:34:00 to 00:36:59.
* 13 May 1943, Axis surrender in Tunisia: Tunisian Victory R8 02:57 to 04:54.
* **14 May 1945, U-858 surrenders off Cape May; crew landed at Fort Miles:** 428-NPC-12592 00:00:49 to 00:01:08 (running pass, crew on deck), 00:05:52 to 00:05:57 (two German officers close); hands raised under the U.S. flag, 428-NPC-12132 00:02:36 to 00:02:49.
* 15 May 1945, U-805's crew brought into Portsmouth (per the Navy record and the tug's number): 428-NPC-7853 00:03:36 to 00:03:49, officers at the rail 00:00:40 to 00:00:46, ashore 00:06:06 to 00:06:24.
* 13 May 1946, Mauthausen trial verdicts: GS World in Film 43 00:01:57 to 00:02:57 (Welt im Film, clear first).
* 17 May 1943, the Belle's 25th mission: Memphis Belle 00:34:30 to 00:36:39.
* 17 May 1944, Myitkyina airfield taken: Brought to Action R3 02:40 to 02:56, 04:00 to 05:22.
* Late May 1943, the King and Queen visit the 91st (verify): Memphis Belle 00:36:58 to 00:38:15.

**June**
* **4 Jun 1944, U-505 captured:** U-505 reel 00:05:01 (conning tower awash), 00:10:08 (German prisoners on USS Pillsbury's bow), 00:07:15.
* 4 Jun 1940, Dunkirk ends: Battle of Britain R1 06:20 to 06:46, 07:01 to 07:12.
* 25 to 26 Jun 1945, UN Charter approved and signed; Truman: San Francisco 1945 R2 03:10 to 04:38.
* 3 Jun 1942, Midway patrol planes and B-17s: Battle of Midway 00:01:00 to 00:01:19, 00:03:40 to 00:04:25.
* **4 Jun 1942 (Midway Flash day), color:** Battle of Midway 00:06:10 to 00:09:31.
* 5 Jun 1944, Eisenhower with the 101st: True Glory R2 00:09:15 to 00:09:30.
* 5 to 15 Jun 1942, rescue and funerals on Midway: Battle of Midway 00:13:15 to 00:16:27.
* **6 Jun 1944 (D Day Flash day):** True Glory R3 00:00:54 to 00:05:30 and 00:08:12 to 00:08:55; embarkation R2 00:06:29 to 00:07:01.
* 9 Jun 1938, Yellow River dikes breached: BoC R6 03:28 to 03:40, 04:10 to 04:26.
* 10 Jun 1944, Oradour (somber): True Glory R4 00:06:03 to 00:06:33.
* 15 Jun 1944, first B-29 raid from China (airfield building): BoC R7 05:56 to 06:20.
* 19 Jun 1944, the Channel storm and Mulberry: True Glory R4 00:02:27 to 00:03:24.
* **22 Jun 1941, Barbarossa:** Leningrad rallies, LF 00:03:25 to 00:05:40; Soviet crowds hear the news, BoR Part 1 00:29:52 to 00:31:20; "what the invaders brought", Trophies 00:01:20 to 00:07:47 (any 22 Jun).
* 22 Jun 1943, the trophy exhibition opens in Gorky Park (verify): Trophies 00:00:40 to 00:01:18.
* 24 Jun 1945, Victory Parade on Red Square: Victory Parade 00:10:35 to 00:11:28, 00:34:17 to 00:35:16 (crop the logos).
* 26 Jun 1944, Cherbourg falls: True Glory R4 00:04:48 to 00:05:24.
* Late Jun 1944, Allied advance in southern Tuscany; two knocked out Tiger I tanks (turret 33): Massa Marittima reel 111-ADC-1326 00:00:30 to 00:01:00, 00:01:42 to 00:02:18 (NARA's 1 Jun date is a catalog date; say late June).

**July**
* **17 Jul 1945, Potsdam opens:** Potsdam 111-ADC-9854 00:02:12 (Big Three seated), 00:03:42 (Churchill and Stalin), 00:06:39 (Churchill greets Truman).
* 20 Jul 1945, Truman raises the flag over Berlin, **his own voice, no music** 111-ADC-9857 00:00:50 to 00:02:47.
* 23 Jul 1940, Home Guard named: Battle of Britain R1 08:08 to 08:50.
* 3 Jul 1941, scorched earth: BoR Part 1 00:31:57 to 00:32:56.
* 23 Jul 1942 and summer 1942, Stalingrad and the Don steppe defense (Soviet shots only): STG 00:06:00 to 00:12:40.
* 5 Jul 1943, Kursk opens; Tiger and Ferdinand (captured examples): Trophies 00:06:40 to 00:07:45.
* 7 Jul 1937, Marco Polo Bridge (the bridge itself is on no film we have): Japanese troops in north China, BoC R2 06:54 to 07:22; KYEJ R1 04:40 to 04:56; Japanese film naId 80623 00:04:25 to 00:09:35. All labeled Japanese film.
* July 1941, Leningrad people's militia and the Luga line (verify): LF 00:05:40 to 00:06:45, 00:10:46 to 00:11:58.
* 9 and 18 Jul 1944, Caen: True Glory R4 00:07:21 to 00:09:54.
* 13 Jul 1944, Lviv Sandomierz offensive (verify): RBU 00:44:20 to 00:48:50.
* 18 Jul 1942, Me 262 first flight on jet power (verify): Me 262 film 00:08:14 to 00:08:45; captured jets at Innsbruck 111-ADC-4524 00:00:30 to 00:00:47 (label May 1945).
* 18 to 19 Jul 1944, St Lo: True Glory R5 00:00:33 to 00:01:36.
* 21 Jul 1944, Guam liberated (occupation background): Japanese film naId 80619 00:04:05 to 00:07:09.
* 22 and 27 Jul 1944, Brody pocket; Lviv liberated: RBU 00:50:53 to 00:51:42, 00:52:28 to 00:54:45.
* 25 Jul 1944, Cobra: True Glory R5 00:01:39 to 00:02:03. Same day, first Me 262 combat (verify): Me 262 film 00:09:43 to 00:09:52.
* 26 Jul 1946, Jackson's summation at Nuremberg: GS 1948 film R8 00:00:08 to 00:02:28.
* Partisans, any date from Jul 1941 (likely posed): BoR Part 1 00:32:56 to 00:34:05.

**August**
* 13 Aug 1940, Eagle Day (verify; the film opens the battle on 8 Aug): Battle of Britain R2 04:05 to 04:35 (Hurricanes scramble), R2 05:47 to 06:03 (gun camera).
* 20 Aug 1940, "The Few": Battle of Britain R6 06:09 to 06:33.
* 24 Aug to 6 Sep 1940, airfields under attack: Battle of Britain R3 02:14 to 03:21, R3 04:38 to 05:01.
* 1 Aug 1944, Patton's Third Army active: True Glory R5 00:01:39 to 00:02:03.
* 4 Aug 1944, Rennes: True Glory R5 00:02:04 to 00:03:00.
* 7 Aug 1944, Mortain: True Glory R5 00:03:27 to 00:04:51.
* 12 to 21 Aug 1944, Falaise pocket: True Glory R5 00:05:48 to 00:07:42, R6 00:00:18 to 00:02:18.
* 13 Aug 1937, Battle of Shanghai begins: BoC R3 00:20 to 00:45, R3 03:40 to 04:27 (effects only), R1 01:12 to 01:22. **Never caption the R3 06:14 to 06:38 casualties as a Japanese raid** (14 Aug 1937 carnage came from stray Chinese bombs).
* 13 to 15 Aug 1942, Churchill in Egypt: Desert Victory 00:06:55 to 00:08:25.
* 18 Aug 1941, Dnieper dam blown (verify): BoR Part 1 00:32:12 to 00:32:35.
* **23 Aug 1942, the great bombing of Stalingrad, natural sound 00:14:47 to 00:17:56 (no voice or music; listen first):** STG 00:14:55 to 00:18:08; firemen at a burning block 00:15:54 to 00:16:14; the Barmaley fountain and a man carrying a double bass through the ruins 00:21:37 to 00:21:51.
* 23 to 25 Aug 1942, Germans reach the Volga; tractor works fights: STG 00:18:40 to 00:20:15.
* 25 Aug 1944, Paris liberated: True Glory R6 00:04:33 to 00:06:00.
* 24 Aug 1944, Brest refugees at Ploudalmezeau (Home Front): Seine reel 111-ADC-2245, see index. 25 Aug 1944, the 10th Infantry crosses the Seine at Montereau under fire, shell spouts in the river: 00:04:48 to 00:04:50, raft with antitank gun 00:05:21 to 00:05:35; a German ammunition truck explodes at Maison Rouge 00:00:22 to 00:00:40.
* 27 Aug 1941, U-570 surrenders to an RAF Hudson: GS 428-NPC-16294 00:01:18, 00:04:12 (the boat later in British service as HMS Graph; say so).
* 31 Aug 1946, final statements at Nuremberg: GS 1948 film R7 00:03:12 to 00:07:41.
* 31 Aug to 7 Sep 1942, Alam el Halfa: Desert Victory 00:11:40 to 00:12:15.
* Aug to Nov 1937, Shanghai refugees: BoC R3 04:10 to 05:16.

**September**
* **2 Sep 1945, Japan surrenders aboard USS Missouri:** Missouri reel 00:01:44 to 00:02:45 (delegation boards, Shigemitsu, MacArthur), signings 00:02:51 to 00:03:42.
* 7 Sep 1940, the Blitz begins: Battle of Britain R3 06:08 to 06:39, R4 00:06 to 01:35.
* **15 Sep 1940 (Battle of Britain Day):** Battle of Britain R4 03:36 to 04:27, R4 06:42 to 06:51.
* 3 Sep 1944, Brussels: True Glory R6 00:06:54 to 00:07:30.
* 8 Sep 1941, Leningrad blockade closes; Badayev warehouses fire (verify): LF 00:16:40 to 00:18:10; BoR Part 2 00:14:27 to 00:17:48.
* 11 to 12 Sep 1944, first Allied troops into Germany: True Glory R6 00:07:30 to 00:07:45.
* 11 to 22 Sep 1944, the Americans reach the Siegfried Line: Siegfried Line reel 428-NPC-13442 00:00:57 to 00:01:12 (low aerial along the dragon's teeth), 00:03:26 to 00:03:41 (shell pocked pillbox); slated 22 Sep.
* **18 Sep 1944, Brest surrenders:** Brest reel 111-ADC-2350 00:05:14 to 00:05:34 (the German paratroop colonel surrenders with a salute), 00:01:21 to 00:01:36 (German officers shake hands), 00:09:09 to 00:09:27 (hundreds of prisoners).
* 17 Sep 1944, Market Garden: True Glory R7 00:01:24 to 00:03:06.
* 17 Sep 1945, Belsen trial opens: GS World in Film 43 00:04:48 to 00:05:44 (Welt im Film, clear first).
* 18 Sep 1931, Mukden Incident: KYEJ R2 23:54 to 24:24, caution only; a headline works better.
* 22 Sep 1943 onward, Dnieper crossings (verify): RBU 00:05:29 to 00:07:00.
* **30 Sep to 1 Oct 1946, the Nuremberg judgment, live courtroom sound:** GS 111-ADC-10021 (whole roll; call it "judgment day", not sentencing).
* 12 to 15 Sep 1942, Chuikov's 62nd Army holds the city; Rodimtsev's guards cross (verify): STG 00:22:34 to 00:24:40.
* Sep to Nov 1942, Stalingrad street and factory fighting: STG 00:27:48 to 00:29:30, 00:31:04 to 00:32:05; BoR Part 2 00:33:30 to 00:34:45, 00:35:35 to 00:36:37. Pavlov's House and Mamayev Kurgan are on no film we have.

**October**
* 5 to 6 Oct 1943, the Navy raid on Wake (likely; verify): Wake reel 00:02:10 to 00:02:34.
* 7 Oct 1944, first Me 262s shot down by USAAF fighters (as November gun camera, never as that kill): Fighter Kills 111-ADC-10508 00:02:31 to 00:02:39.
* **15 to 21 Oct 1944, Aachen:** Aachen reel 111-ADC-2655 00:02:45 to 00:03:03 (tanks firing down a smoke filled street), 00:05:48 to 00:05:57 (tank destroyer in the rubble), 00:01:00 to 00:01:09 (shot up Nazi newspaper sign). Filmed 15 Oct, mid battle; for the 21 Oct surrender say so.
* 26 to 27 Oct 1942, Santa Cruz; Hornet survivors moved by breeches buoy: Wake and Santa Cruz reel 00:02:52 to 00:05:46.
* 24 Oct 1945, UN Day (Charter in force), signing footage labeled June 1945: San Francisco 1945 R2 03:51 to 04:03.
* 1 Oct 1946, Nuremberg verdicts: GS 1948 film R8 00:05:04 to 00:05:56, 00:09:28 to 00:10:04; GS 111-ADC-10021.
* 3 Oct 1944, Kommando Nowotny formed (verify): Me 262 film 00:07:47 to 00:08:00.
* Oct 1941 to Jul 1942, Sevastopol siege: BoR Part 1 00:28:25 to 00:28:57.
* 2 Oct 1941, Operation Typhoon; Moscow defenses (verify): MOS 00:01:00 to 00:05:55.
* 19 to 20 Oct 1941, state of siege in Moscow; barricades and balloons: MOS 00:01:36 to 00:04:00.
* Oct to Dec 1941, defense of Moscow: BoR Part 2 00:01:05 to 00:01:19; Red Square parade 00:00:19 (infantry), 00:05:00 (tanks).
* 15 to 16 Oct 1946, Göring's suicide; the executions (no bodies, ever): GS 1948 film R8 00:10:04 to 00:10:40 only.
* **20 Oct 1944, Leyte landing:** Brought to Action R1 03:50 to 04:22 (check faces before naming MacArthur).
* 21 to 22 Oct 1943, Azad Hind, Rani of Jhansi Regiment: Japanese film UN-UN-4901x3 00:10:00 to 00:12:05 (status flagged).
* 22 Oct to 7 Nov 1942, Torch convoys: Tunisian Victory R1 00:45 to 02:24.
* 23 Oct 1942, El Alamein barrage, **natural gun sound**: Desert Victory 00:27:07 to 00:29:31 (flashes and tracer only).
* 24 Oct 1942, Shermans in action: Desert Victory 00:30:20 to 00:30:57.
* 24 Oct 1944, Sibuyan Sea; Princeton burning: Brought to Action R1 06:46 to 07:07, R2 04:30 to 04:47.
* **25 Oct 1944 (Leyte Gulf Flash day from 2027):** Samar from an escort carrier, Brought to Action R2 00:06 to 01:34; strike camera film of Japanese carriers bombed off Cape Engano, R2 06:50 to 08:05.
* 25 Oct 1943, Dnipropetrovsk (verify): RBU 00:07:20 to 00:09:28.
* 26 Oct 1942, Hornet lost at Santa Cruz (Hornet portrait only): Doolittle reel 00:07:17 to 00:07:31.
* 26 Oct 1944, end of Leyte Gulf; burial at sea: Brought to Action R2 08:25 to 08:43, 09:09 to 10:09.
* 26 to 27 Oct 1942, Kidney Ridge: Desert Victory 00:34:45 to 00:36:30.
* 28 Oct to 1 Nov 1942, the Australian push: Desert Victory 00:36:30 to 00:38:27.

**November**
* 14 Nov 1940, Coventry: Battle of Britain R5 07:02 to 08:30.
* 20 Nov 1943, Tarawa cloud copy (when Source Film is out of reach): Tarawa Navy reel 428-NPC-12205 07:12 to 08:05 (Betio under bombardment), 08:28 to 09:45 (run in), 10:53 to 11:07 (amtrac 67).
* 1 Nov 1944, Walcheren: True Glory R7 00:03:51 to 00:04:27.
* 2, 26 and 27 Nov 1944, big fighter battles over Germany (USAAF gun camera, November 1944): Fighter Kills 111-ADC-10508 00:06:09 to 00:06:27 (Fw 190 at point blank range), 00:05:17 to 00:05:21, 00:04:00 to 00:04:18 (train strafed).
* 2 Nov 1942, Supercharge (natural tank battle sound at 00:44:54): Desert Victory 00:42:19 to 00:48:40.
* 3 and 6 Nov 1943, Kyiv offensive; Kyiv liberated: RBU 00:09:30 to 00:11:50, 00:11:50 to 00:13:50.
* 4 Nov 1942, Rommel's retreat: Desert Victory 00:49:48 to 00:52:53.
* 5 Nov 1937, Hangchow Bay landing (Japanese film): BoC R3 02:58 to 03:22.
* 5 Nov 1942, Eisenhower at Gibraltar: Tunisian Victory R2 04:30 to 04:36.
* **7 Nov 1941, the Red Square parade with the front near Moscow:** Red Square parade, whole film, best 00:06:08 and 00:00:19. Stalin's speech, LF 00:28:08 to 00:29:28 and MOS 00:05:55 to 00:07:26 (re-filmed, caution).
* 8 Nov 1942, Torch landings: Tunisian Victory R3 01:01 to 01:32.
* 10 Nov, Marine Corps birthday: Iwo Jima reel 00:01:47 to 00:02:02.
* 10 to 11 Nov 1940, Kigen 2600 celebration in Tokyo: KYEJ R1 09:10 to 11:46.
* 13 Nov 1942, Tobruk retaken: Desert Victory 00:54:15 to 00:54:42.
* 17 to 25 Nov 1942, Medjez el Bab: Tunisian Victory R3 06:39 to 07:24.
* 15 to 16 Nov 1941, second German drive on Moscow (verify): MOS 00:12:32 to 00:16:47.
* **19 Nov 1942, Operation Uranus:** STG 00:41:46 to 00:44:48 (barrage 00:41:57, T-34s with riders 00:43:27). 22 to 23 Nov, Kalach and the Don bridge, STG 00:48:20 to 00:49:00 (the link up embrace 00:49:00 to 00:49:28 is staged); BoR Part 2 00:38:39 to 00:39:04.
* Nov 1942 to Jan 1943, the Stalingrad airlift fails (abandoned Ju 52s): STG 00:50:45 to 00:51:45, 01:08:54 to 01:09:20.
* 19 Nov 1943, eve of Tarawa: Tarawa 00:01:19 to 00:02:43.
* **20 Nov 1943 (Tarawa Flash day), color:** Tarawa 00:03:05 to 00:06:40 (bombardment, run in, the seawall). D+1 21 Nov 00:10:45 to 00:11:24; any battle day 00:06:17 to 00:09:45 (B&W).
* 20 Nov 1945, Nuremberg trial opens: GS 1948 film R1 00:02:00, 00:04:48. 21 Nov, Jackson's opening with his own sound: R1 00:03:16 to 00:08:23.
* 20 Nov 1941, Leningrad's lowest bread ration (verify): LF 00:33:02, 00:33:56.
* 20 Nov 1942, Benghazi (verify): Desert Victory 00:54:42 to 00:55:40.
* 22 Nov 1941, the Road of Life opens on Ladoga: LF 00:41:22 to 00:43:28; BoR Part 2 00:22:28 to 00:24:50.
* 22 to 26 Nov 1943, Cairo Conference: BoC R7 03:20 to 03:40.
* 23 to 24 Nov 1943, Tarawa secured, flag raised; relief troops: Tarawa 00:18:08 to 00:19:08, 00:17:48 to 00:18:08.
* 26 Nov to 6 Dec 1941, the Pearl Harbor strike force at sea: Japanese film naId 81567 00:03:17 to 00:03:54.
* 28 Nov 1944, first ship into Antwerp: True Glory R7 00:04:30 to 00:04:45.
* 28 Nov to 1 Dec 1943, Tehran: True Glory R2 00:03:27 to 00:03:39.

**December**
* **7 Dec 1941, Pearl Harbor, aftermath** (with the Japanese launch film): Pearl Harbor damage 00:03:33 to 00:03:47 (Arizona, not named by NARA), 00:03:50 to 00:04:10, 00:01:26 to 00:01:40. Nine War Gods portraits 00:00:28 to 00:01:13 (captured Japanese film).
* 8 to 25 Dec 1941, Hong Kong attacked, landed on, surrenders (Japanese film): Nine War Gods 00:04:04 to 00:07:13.
* **16 Dec 1944, the Bulge:** The Enemy Strikes 06:30 to 06:58 (withdrawal, supplies), 08:12 to 08:51 (winter line); the attack itself is German film only.
* 23 Dec 1944, skies clear over the Bulge: The Enemy Strikes 07:54 to 08:10 (natural sound 08:00 to 08:30); Bulge Signal Corps reel 111-ADC-9670 07:20 to 07:39; December gun camera, a German pilot bails out over snow, Fighter Kills 111-ADC-10508 00:08:25 to 00:08:38, Bf 109 fireball 00:07:58 to 00:08:03.
* 29 Dec 1940, the London fire raid (verify): Battle of Britain R6 01:42 to 04:28, St Paul's in smoke R6 04:22 to 04:28.
* 13 Dec 1939, Battle of the River Plate: **no free film** (all commercial newsreel). Make it a Story Card from public domain Graf Spee photos (AWM has them).
* 4 Dec 1945, Shawcross opens the British case at Nuremberg: GS 1948 film R3 00:05:08 to 00:05:36.
* **5 to 6 Dec 1941, Moscow counteroffensive:** the gun line firing across the snow with **natural sound 00:22:34 to 00:24:02** (listen first), MOS 00:22:34; cavalry charge 00:28:00 to 00:28:30; paratroopers 00:29:24 to 00:30:20; BoR Part 2 00:02:50 to 00:05:46; Red Square parade 00:00:40 as a lead in.
* 11 to 13 Dec 1941, Istra retaken; Sovinformburo announces the German defeat: MOS 00:50:30 to 00:52:00; aerial of abandoned German columns 00:57:49 to 00:58:05.
* 15 to 16 Dec 1941, Klin (Tchaikovsky's house) and Kalinin retaken: MOS 00:52:02 to 00:53:15, 01:00:27 to 01:03:45.
* 20 Dec 1941, Volokolamsk retaken: MOS 01:03:45 to 01:04:22 (the gallows after it are somber).
* **7 Dec 1941 (Pearl Harbor Flash day), Japanese Navy film from the carriers:** naId 81567, the launch 00:05:15 to 00:05:33.
* 8 Dec 1941 (Japan time), Tokyo announces war: Japanese film naId 77701 00:01:01 to 00:06:35.
* 10 Dec 1941, Guam falls: Japanese film naId 80619 00:04:20 to 00:06:05.
* 12 Dec 1937, USS Panay sunk: BoC R3 07:10 to 07:39.
* 13 Dec 1937, Nanking falls (Japanese film): BoC R4 00:50 to 01:12. Massacre: Magee's film R4 02:16 to 03:00, somber only; **the staged reenactments are never used.**
* 13 Dec 1941, news of Moscow reaches Leningrad: LF 00:41:08 to 00:41:20.
* 13 to 15 Dec 1943, Arawe convoy and landing: New Britain 00:16:00 to 00:25:40.
* 16 Dec 1941 onward, liberated towns: BoR Part 2 00:05:46 to 00:07:50.
* **16 Dec 1944 (Bulge Flash day):** True Glory R8 00:00:18 to 00:00:53.
* 20 Dec 1941, Flying Tigers' first combat: BoC R5 06:40 to 06:57.
* 20 to 26 Dec 1944, Bastogne: True Glory R8 00:01:24 to 00:03:36.
* 23 Dec 1941, Wake falls: Japanese film naId 80619 00:07:25 to 00:09:03.
* 24 Dec 1941 to 15 Jan 1942, Third Battle of Changsha: BoC R7 02:04 to 02:36.
* 24 Dec 1943, Eisenhower named Supreme Commander: True Glory R2 00:03:39 to 00:04:18.
* 24 to 26 Dec 1942, Tunisian mud; Christmas at the front: Tunisian Victory R4 00:18 to 00:45, 08:00 to 09:03.
* 24 to 25 Dec 1943, Christmas in the Marine staging area: New Britain 00:29:40 to 00:31:45.
* **26 Dec 1943, Cape Gloucester:** New Britain 00:32:08 to 00:40:00; LSTs 00:43:56 to 00:47:00; USS Brownson sunk 00:49:30 to 00:50:45.
* Dec 1941 to Feb 1942, Leningrad starvation winter: LF 00:31:45 to 00:38:45; BoR Part 2 00:18:21 to 00:20:20.

**Any date**
* 8th Air Force bombers, 1943 to 1945: Memphis Belle (generic).
* Pacific carrier and fleet operations, 1942 (label it so): Doolittle reel 00:04:42 to 00:07:05.
* Southwest Pacific jungle fighting and supply: New Britain (index).
* Midway island life: Battle of Midway 00:02:20 to 00:03:40.
* Battle of the Atlantic: True Glory R1 00:04:57 to 00:05:45; U-570 as HMS Graph (GS 428-NPC-16294).
* Blueprint, German weapons: Trophies (Bf 109 00:03:20, Nebelwerfer 00:04:00, Flak 00:04:45, MG 34 00:10:12); Me 262 film 00:00:50 to 00:01:05, 00:04:20 to 00:05:43.
* Home Front, Soviet reconstruction 1944: RBU 00:31:00 to 00:37:20.
* China: the trek west BoC R4 05:34 to 07:30; recruits R5 04:50 to 06:40; the Burma Road R6 00:32 to 02:50; the Hump R7 04:52 to 05:18 and Brought to Action R3.
* Japan at home: KYEJ (the Diet R2 01:12 to 01:26; war industry R2 05:24 to 06:00, 21:30 to 22:16).
* Nuremberg defendants as a "then" image for Jodl or Keitel stories: GS 111-ADC-9759 00:00:59 to 00:01:16; 111-ADC-1919 00:06:15 to 00:07:21.
* Blitz, any date Sep 1940 to May 1941: Battle of Britain R4 00:45 to 01:35, R5 00:50 to 02:11, R6 04:30 to 05:09.
* Blueprint, U-boat interior (Type IXC): U-505 interior reel 00:00:18, 00:04:18. Type IX casing and tower close: 428-NPC-12592 00:10:35 to 00:10:53, 428-NPC-12132 00:02:51 to 00:03:00.
* Blueprint, the Me 262 and its Jumo engine: Innsbruck 111-ADC-4524 00:00:58 to 00:01:08, 00:02:09 to 00:02:15. The Me 163 in American gun sights: 111-ADC-10508 00:01:03 to 00:01:08, 00:03:21 to 00:03:38.
* Blueprint, the V-2 and its engine (as "the same rocket, fired in New Mexico"): 428-NPC-10804 00:00:06 to 00:00:17, 00:02:36 to 00:02:53.
* Blueprint, the Westwall: Siegfried Line reel 00:02:33 to 00:02:50, 00:04:52 to 00:05:10.
* Axis lens, German prisoners in Allied hands (any 1944 to 1945 date, labeled with place and date): German prisoners 1945, Brest, Cologne 3535, U-boat crews.
* Memorial and Remembrance days: True Glory R9 00:07:24 to 00:07:47.

## Inside these films: never use
Each index lists exact times. The rules in short:
* **Captured German or Italian film inside an Allied or Soviet documentary.** Most of The Battle of Russia's 1941 invasion combat, Rommel and Hitler in Desert Victory, Kesselring and Rommel in Tunisian Victory, the German shots in The True Glory, and the Nazi era film shown as evidence in the Nuremberg film. Soviet documentaries splice German newsreel in too; their indexes flag it.
* **Staged and reconstructed shots.** The Pinewood close ups in the Alamein barrage. Tunisian Victory's reenactments. Most of Ford's Midway carrier sequence. The Nanking atrocity reenactments in The Battle of China. The Reichstag flag scenes in Berlin. Brought to Action's staged Japanese officers, the reconstructed submarine attack, and its studio inserts. Japanese feature film in Know Your Enemy: Japan (samurai dramas, studio soldiers, miniatures). Posed inserts in Attack! (documents, watches, journals).
* **Feature film clips.** The Battle of Russia's history section (Part 1 00:02:00 to 00:06:43).
* **Graphic material.** Bodies are never shown (Nuremberg evidence film, the Iwo Jima reel 00:02:57 to 00:03:14, the atrocity stretches listed in each index). Camp and massacre film only on a somber dispatch, with care.
* **German camera inside an Allied reel:** Fighter Kills 111-ADC-10508 00:02:40 to 00:02:49 and 00:03:39 to 00:03:53 (and 00:02:54 to 00:03:20, unclear); the Hitler snapshot in 111-ADC-9795 05:06 to 05:26. Mauthausen bodies in 111-ADC-4326 07:15 to 07:53, never.
* **Third party additions.** The IHF Sevastopol copy (©, subtitles, logo); the TV logo and watermark on the Victory Parade copy. Crop, or find a better copy.
* **Added sound.** Midway, Memphis Belle, the Japanese reels, the Iwo Jima, Doolittle and Lexington reels have no location sound; every clip is picture only.

## Where to look next
**Sources we use**
* **NARA catalog** (moving images; downloads work from Claude's workspace). Search: `https://catalog.archives.gov/proxy/records/search?q=<words>&typeOfMaterials=Moving%20Images&rows=25`; a record's `digitalObjects[].objectUrl` is the file. Best series: 111-ADC (Signal Corps combat film, with shot cards), 428-NPC (Navy, including captured Japanese film), 111-M and 111-OF (finished Army films and Why We Fight), 342-USAF, 330-DVIC, 208 (OWI).
* **Wikimedia Commons** (Brian downloads; Claude can't). Use the 480p transcode for anything over 400 MB, or a 240p copy for indexing.
* **Australian War Memorial** collection, for viewing and leads; prefer a NARA copy of the same reel.

* **Polygoon (Dutch newsreel) on Open Beelden** (openbeelden.nl; Brian downloads, Claude can't). Added 13 Nov 2026 as the clean source for German forces in the Netherlands: the May 1940 invasion, the occupation, and the German surrender and prisoner columns of 1945. Each clip's page offers HD MP4 downloads. Many are also on Commons.

**Dutch film, rights basis:** Open Beelden marks Polygoon clips **Public Domain Mark 1.0** (copying, editing and commercial use without permission). **Check each clip's own page.** Commons copies carry an older CC BY-SA 3.0 NL tag, so take the Open Beelden copy and credit it anyway: "Polygoon-Profilti / Netherlands Institute for Sound and Vision". From mid 1940 Polygoon worked under German censorship: caption with context, picture only. It is Dutch film, not German newsreel, so it fits the 1 Nov decision. **Never use the Dutch Nazi party's own reels on Commons ("Spiegel der beweging", NSB film service).** Brian ruled them out on 13 Nov 2026.

**Japanese film, rights basis:** Japanese films released under an organization's name before 1953 are public domain in Japan, so in the U.S. too. NARA marks the 428-NPC Japanese reels' use status "Undetermined" because it doesn't rule on foreign works. The two Universal Newsreel outtake reels (UN-UN-4901x2 and x3) are flagged "Restricted, Possibly", so check them first.

**Soviet film, rights basis:** Commons files tagged **PD-Russia-1996** (a studio film made 1929 to 1946) are public domain in Russia and the U.S. **Only that tag counts**; a plain "PD-Russia" tag does not. Treat all Soviet narration as propaganda; facts come only from the fact sheet. **Never use "Tragedy in the Katyn Forest" (1944)** except as an example of propaganda.

**Leads not yet indexed**
* **Polygoon, first clips to index** (13 Nov 2026; full list with links in `claude/film-index/german-footage-sources-2026-11-13.md`): German motorized troops enter Amsterdam and The Hague, mid May 1940 (Open Beelden media 793168, 5 min); the press tour of the IJssel and Grebbeberg battle sites led by a German officer, 22 May 1940 (media 794577, 2 min); German prisoner columns marching to Den Helder, May 1945; the liberations of Enschede, Groningen and Amsterdam, Apr to May 1945. None indexed yet, so no Calendar entries until Brian saves them to Source Film.
* **More from the 13 Nov sweep** (same doc): Allied camera reels to view (Namsos 1940, 428-NPC-16337; Aircraft Recognition training films, 111-TF-1-3684 on the Ju 88; three Universal outtakes; War Pictorial News 210; A Defeated People, 111-OF-28). The doc also lists Allied made films that reuse German footage (Universal Newsreel 1939 to 1941, Why We Fight 2 and 3, Your Job in Germany, The Nazi Plan) and raw captured German reels at NARA. Those stay out under the 1 Nov decision unless Brian changes it.
* **German military round two:** `claude/film-index/german-military-allied-film-leads.md` lists 20 more Signal Corps and Navy reels found on 6 Nov 2026 (a knocked out Tiger at Marticina, Kurtscheid prisoners, Varsity, the Caserta surrender, the Elbe meeting, Eschweiler, the V-1 battery, the Ludendorff collapse, Ramcke's surrender, Prinz Eugen at Bikini, Nuremberg rushes).
* **The Cologne cathedral tank duel** (Jim Bates, 6 Mar 1945): checked and not in 111-ADC-1955, 3508, 9703, 9704 or 3535. Try 111-ADC-3530 (naId 17333) next.
* **Waiting in Source Film:** nine films Brian saved on 5 Nov 2026 (Orel 1943, the Moscow prisoner march, Nikolaev, Christmas Under Fire, and four AWM films: Tobruk 1941, Balikpapan, the Tokyo surrender, Yamashita's surrender). See `claude/film-index/pending-source-film.md`.
* **To the Shores of Iwo Jima** (80-MN-5124, naId 13089, 4.3 GB): indexing was started on 5 Nov 2026 and stopped before it finished. Run again before 19 Feb.
* **More found 5 Nov 2026:** `claude/film-index/leads-2026-11-05.md` (NARA, unindexed: Hiroshima and Nagasaki surveys, Saipan, Peleliu, Sicily, Salerno, Guadalcanal, the bombing of London, Fighting Lady reels, Japanese Relocation, Normandy Navy reels) and `claude/film-index/commonwealth-sources.md` (Australian War Memorial public domain actuality and British Crown films).
* **Göring at Nuremberg, Signal Corps rushes:** 111-ADC-5808 (naId 19606, 13 Mar 1946, first day of his testimony), 111-ADC-5806 and 111-ADC-5799. These would replace the United News reel for 13 to 22 Mar.
* **Victory Parade in color:** the 1945 release was shot in color; look for a PD-Russia-1996 color copy on Commons to replace the poor one.
* **A clean Sevastopol copy** (without the IHF additions).
* **Japanese, digitized at NARA:** 78848 (the "Nine War Gods", midget submarine crews of 7 Dec; index before 7 Dec), 75463 (Corregidor, Wainwright with his captors), 78849 (Celebes paratroop drop, 11 Jan 1942), 78842 (a kamikaze unit sortie), 78719 (captured U.S. airmen).
* **Why We Fight, the rest:** Prelude to War (naId 36067), The Nazis Strike (36068), Divide and Conquer (36069), War Comes to America (36073); Fury in the Pacific (111-ADC-9735 and 9736, naIds 23500 and 23501). The Nazis Strike and Divide and Conquer last (heavy German film).
* **Here Is Germany** (1945, NARA 111-OF-11, naId 36077): mostly captured German newsreel; low priority, only for its Allied shots.
* **Universal Newsreel** (NARA UN-UN) is free to use (deeded to the U.S. in 1974), but the 1978 vault fire destroyed most of 1941 to 1945. Surviving stories worth checking: Mussolini's death, the Nuremberg verdicts.
* **Commons, British PD-UKGov shorts:** Christmas Under Fire (1941), Newspaper Train (1942), The True Story of Lili Marlene (1944), the Tirpitz attack of 15 Sep 1944; New Zealand's Return from Crete (1941, PD-NZ).
* Italian, digitized but rights not established (do not use yet): Giornale di Guerra 267 (naId 44491) and six Giornale Luce issues.
* **Not available free anywhere checked:** Report from the Aleutians, Target for Tonight, Daitoa News #1 (naId 35995, a paid NARA order).

**Do not use as a source**
* **Brian's decision, 1 Nov 2026: stay clean on German film.** No Wochenschau in any form, including NARA's captured reels and the CC0 tagged copies on the Internet Archive (that tag is the uploader's, not a rights clearance). German side videos use Allied film of the German side (the GS pack) or become Story Cards built from Bundesarchiv photos (Research doc, photo rules).
* Italian newsreels until their status is established.
* Soviet film without the PD-Russia-1996 tag. The Katyn film never.
* Welt im Film reels (111-ADC-10054, 111-ADC-10089) until cleared; they are administered as a German archive holding.
* Commercial newsreels inside NARA: the Movietone "Pearl Harbor Attack" reel (428-NPC-419, ©1942 Movietonews) holds genuine 7 Dec footage but is not usable; Paramount News camera footage in the Yalta and Potsdam reels carries a rights caution.
* United News reels (208-UN) only as a second choice, when no Army or Navy film covers the moment (NARA marks 208-UN-202 Unrestricted, but its card carries a 1946 copyright line). British Pathé, Movietone, and colorized or remastered versions never.
* The 1942 Toho feature "The War at Sea from Hawaii to Malaya" (studio miniatures). NARA naId 81516 (a reconstruction, not Japanese film) and 77232 (simulated midget submarine).

## Adding a film
When research or a Project chat finds a film worth keeping (one that covers several dates):
1. Get a copy the workspace can read: a NARA MP4 (best, since every run can reach it), or Brian saves a Commons file into Source Film (under 400 MB for the transfer; a 240p or 480p transcode otherwise).
2. Transcribe the narration with timestamps (faster-whisper base.en) and make contact sheets with burned in timecode (one frame every 15 seconds, then denser sheets to pin the best shots).
3. Judge every sequence: actuality, staged or reconstructed, captured enemy film, feature film, maps. Never guess a place or date; say where each came from.
4. Write the index in the standard format as `claude/film-index/<slug>.md`, and copy it to Brian's Film Library folder.
5. Add the film to "On hand" and its dates to the Calendar here, and log it below.

## Changelog
* 13 Nov 2026: Added **Polygoon (Dutch newsreel) on Open Beelden** as a source, with its rights basis and first clips to index. Second source sweep for German military film written up in `claude/film-index/german-footage-sources-2026-11-13.md` (why Wochenschau circulates on social media, Allied made films that reuse German footage, captured German reels at NARA, new Allied camera leads). The 1 Nov decision is unchanged.
* 7 Nov 2026 (night): How to use it, item 7, now points to the daily 2:30 p.m. Axis card and the 7 p.m. video order instead of the retired Axis and Eastern Front floors. The Thursday video runs (noon and evening) both cut from this library.
* 6 Nov 2026 (later): Indexed 28 NARA reels showing the German military on Allied film as 17 index docs, with no German newsreel: Cologne (5 reels), Brest, the Seine crossing, Aachen, German prisoners 1945 (Ruhr pocket, Müden, Roetgen), Tunisia 1943, the Tiger wrecks near Massa Marittima, Remagen, the Reims surrender, German leaders in custody (Goering, Kesselring), the Innsbruck Me 262s, USAAF Fighter Kills gun camera, the White Sands V-2, five U-boat surrender reels (U-858, U-873, U-805), and the Siegfried Line. Added them to On hand, the Calendar and Any date. Round two leads in `german-military-allied-film-leads.md`.
* 6 Nov 2026: Cloud copies now go to `footage/` on Cloudflare R2 through `renderer/media.py` instead of the videos repo (Media Move doc). This doc now also has a copy in `docs/` in the cards repo, so the scheduled runs can read it; the film indexes stay Project only for now.
* 5 Nov 2026: Indexed 21 more NARA reels as 16 index docs: The Battle of Britain, The Enemy Strikes and two Bulge Signal Corps reels, Pearl Harbor damage, Nine War Gods, the Missouri surrender, Anzio, Cassino, Yalta (5 reels), Potsdam (4), U-505 (2), Okinawa (2), San Francisco 1945, two Tarawa Navy reels, the Wake and Santa Cruz reel, and the Movietone Pearl Harbor reel (not usable). Found the Australian War Memorial as a public domain Commonwealth source. River Plate has no free film. To the Shores of Iwo Jima still to finish.
* 1 Nov 2026 (later): Indexed 17 more: The Battle of China, Know Your Enemy: Japan, Brought to Action, the Iwo Jima flag raising (Genaust), the Doolittle launch, Lexington at Coral Sea, Attack! The Battle for New Britain, With the Marines at Tarawa, the German side pack (Reims, Karlshorst, Nuremberg, U-570), and eight Soviet films (Leningrad Fights, the 7 Nov 1941 parade, Right Bank Ukraine, Sevastopol, Berlin, the Victory Parade, Trophies of Great Battles, the Me 262). Calendar rebuilt with Eastern Front and Axis lens dates in every month. Sevastopol copy marked reference only. Then indexed Defeat of the German Armies near Moscow and Stalingrad from 240p copies (Stalingrad is the original Soviet release; its captured German stretches are flagged). German side index split into two docs.
* 1 Nov 2026: Library created. Indexed The Battle of Russia, The Battle of Midway, Desert Victory, Tunisian Victory, The Memphis Belle, The True Glory, and eight captured Japanese reels. Found and checked the Japanese Navy's own film of the Pearl Harbor launch (naId 81567).
