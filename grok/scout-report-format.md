# Scout Report Format

Use this exact structure. Keep every label exactly as written, because Claude reads the report by these labels. Write OPEN in place of a slot you could not fill to the quality bar, with one line saying why. Use * for list items, never dashes.

## Template

```
# Grok Scout: Nov 1 to Nov 7

## Nov 1

### 8 AM Story
Event: 1942 | Battle Lines | what happened on this date, in one line
Why: one sentence on why it stops a scroller
Source 1: strong source link
Source 2: second strong source link (required if anything is surprising)
Photo 1: what it shows | from the day: yes or no | license | record number | exact page link
Photo 2: optional, same layout
Film: what it shows | record number | exact page link (or: none found)

### 5 PM Evening
Format: Photo of the Day, Quote of the Day, or Spec Sheet
Event: 1943 | Blueprint | what happened on this date, in one line
Why: one sentence
Source 1: link
Source 2: link
Photo 1: what it shows | from the day: yes or no | license | record number | exact page link
Quote: exact words | speaker | occasion | link to a page showing these exact words (Quote of the Day only)
Spec: label = value | source link (Spec Sheet only, one line per number, up to six, only numbers two sources agree on)

### Backup
Event: 1941 | Home Front | one line | photo page link

## Nov 2
(same layout, through the last date)

## Week check
Series: Battle Lines n, Home Front n, Blueprint n, Statecraft n
Spec Sheets: n
Open slots: list them, or none
Living card candidate: event and film link, or none

## Dropped
* Date | event | reason (wrong date, already covered, no usable photo, minor)
```

## Filled example (one date)

```
## Oct 26

### 8 AM Story
Event: 1942 | Battle Lines | At Santa Cruz, Japanese air attacks cripple USS Hornet and her crew abandon ship (she sank early on 27 Oct)
Why: The carrier that launched the Doolittle Raid is lost, leaving Enterprise as the only US carrier in the South Pacific.
Source 1: https://www.history.navy.mil/research/histories/ship-histories/danfs/h/hornet-vii.html
Source 2: second strong source link
Photo 1: Hornet's crew prepare to abandon ship, seen from USS Russell | from the day: yes | public domain, US Navy | 80 G 34110 | https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g/80-G-30000/80-G-34110.html
Film: none found

### 5 PM Evening
Format: Spec Sheet
Event: 1943 | Blueprint | Dornier Do 335 Pfeil makes its first flight
Why: A fighter with one propeller in front and one behind, the fastest German piston fighter of the war.
Source 1: https://airandspace.si.edu/collection-objects/dornier-do-335-0-pfeil-arrow/nasm_A19610129000
Source 2: second strong source link
Photo 1: Do 335 A 0 at the Smithsonian | from the day: no | CC0 | NASM | https://commons.wikimedia.org/wiki/File:Dornier_Do_335_A-0_Pfeil_(Arrow)_-_Unterseite.jpg
Spec: First flight = 26 October 1943 | source link
Spec: Engines = two Daimler Benz DB 603 | source link

### Backup
Event: 1944 | Battle Lines | Battle of Leyte Gulf ends with the Japanese fleet withdrawing | photo page link
```

## Self check (run before you finish)
* Every date has an 8 AM Story, a 5 PM Evening, and a Backup, or a clear OPEN with a reason.
* Every Event line is true for this exact calendar date.
* Every pick has two Source lines, and Wikipedia is never the only one.
* Every pick has a Photo 1 with a record number and an exact page link.
* Every pick has a Photo 1 with a record number and an exact page link on the archive itself (NARA, LOC, NHHC, IWM, Commons file page). A museum article image, a fan site like navsource, or a bare image file is not enough.
* A photo marked "rights status not evaluated" or "no known restrictions" is not cleared. Say so on the Photo line instead of calling it public domain.
* Variety: no event fills more than two slots in the week, and the two slots on one date are different events (except a Spec Sheet or Quote that adds something new). Never use the same event for two 8 AM Stories.
* "From the day: yes" only for photos taken on that exact date. Art made later is "from the day: no".
* Nothing repeats our live dispatch log or Covered Events.md.
* Every Spec number has a source link; every Quote is word for word on its linked page.
* The Week check counts are correct: count all 14 slots (8 AM and 5 PM) by series, and recount before saving. At least one Home Front, two Spec Sheets, and every series at least twice.
* No dashes anywhere in your own writing.
