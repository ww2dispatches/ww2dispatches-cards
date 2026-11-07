# Theme tags

Every dispatch JSON in `dispatches/` and every Name This JSON in `namethis/` carries a `themes` block, so the Wednesday analytics review can tell what a post was about, not just its series. The Thursday cards run tags each new dispatch, the Saturday Name This run tags each Name This card, and the Friday video run adds the `video` part after looking at the finished video's first frame.

Declass also reads `who`, `story`, and `branch` for the Subject filter in All cards (renderer/catalog.py carries them into the game catalog, `story` as `happened`, and site/declass/declass.js maps each value to a player facing label), so a new value here needs a label added there.

**Use only the values listed here, spelled exactly as written.** A new value can be added only by the Wednesday review, which adds it to this file and says so in its summary. `renderer/analytics.py` flags any value that is not on this list.

```json
"themes": {
  "who": ["women", "African Americans"],
  "story": ["first or barrier broken"],
  "photo": "group",
  "theater": "home front",
  "branch": ["women's services"],
  "nations": ["US"],
  "video": {"kind": "Living Card", "opening": "combat or firing", "sound": "period sound"}
}
```

## who (one or more, or an empty list)
Who the post centers on.
leaders · soldiers and sailors · airmen · civilians · children · women · African Americans · Japanese Americans · Native Americans · Jewish people · other groups

With "other groups", add a `note` naming the group (for example "note": "Nisei soldiers").

## story (one, sometimes two)
combat · first or barrier broken · turning point · survival or rescue · invention or machine · decision or diplomacy · everyday life · loss or atrocity

## photo (one)
What the card's photo shows.
combat or action · a face or portrait · people in action · a group · a machine · a place or scene · a document or poster

## theater (one)
Western Europe · Eastern Front · Mediterranean and North Africa · Atlantic · Pacific · China Burma India · home front · worldwide

"worldwide" is for conferences, diplomacy, and trials that belong to no front. Naval stories at sea go under the ocean (Atlantic or Pacific). The era (road to war, the war, or the aftermath) is worked out from the event date, so it is not a tag.

## branch (any, or an empty list)
Army · Navy · Marines · Army Air Forces · Coast Guard · women's services · civilian agency

The branch of whatever force the story follows, on either side (a German U-boat story is Navy). British, Soviet, and other forces use the nearest equivalent (the RAF is Army Air Forces).

## nations (one or more)
US · Britain · Soviet Union · France · China · Germany · Japan · Italy

Any other nation is written by name (for example "Philippines", "Poland", "Canada").

## lens (one)
Whose side of the war the card is told from, for the Declass Campaigns decks (Campaigns Sides and Decks doc).
us · commonwealth · soviet · other_allied · axis_germany · axis_japan · axis_italy · civilian_neutral

Pick the side the card's subject belongs to, not the side that wins: a U-boat crew's story is axis_germany, Kearny's sailors are us. British, Canadian, Australian, Indian, and other Commonwealth forces are commonwealth; Free French, Polish, Chinese, Dutch, and other Allied forces are other_allied. Civilians are civilian_neutral when the card is about them as civilians (the Blitz, Hamburg, a neutral country); a nation's home front program (rationing, war bonds, the draft) takes that nation's lens. Added 7 Nov 2026 by Brian's decision (Campaigns chat). The research run sets it on every new dispatch; the Campaigns backfill adds it to the older ones.

## video (Living Cards and Story Cards only)
* **kind:** Living Card · Story Card
* **opening:** what the first two seconds show, from the finished video, never from memory: combat or firing · motion · people still · a face · a machine · a place or scene · a map or text card · dark or unclear
* **sound:** period sound · silent · narration · music

"music" was added by the 3 Nov 2026 review for No. 039 (Manila Bay), the one video with a music bed, by Brian's exception of 28 Oct 2026; the Videos doc's no music rule still stands.
