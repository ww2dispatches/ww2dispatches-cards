# Color notes: The Bulge Flash card, 16 Dec 2026

Photo: NARA 208-AA-202B-4, German photo from captured film, held by the U.S. National Archives (NARA copy, 4284 x 5370). NARA dates it 16 Dec 1944 in the Belgian sector; the roll is generally placed at the Poteau crossroads about 18 Dec 1944. Method A (scripted grade, `colorize-2026-12-16-the-bulge.py`), C2 Kodachrome look.

## Period colors and sources
* **Halftrack (German Sd.Kfz. 251, not American as NARA's caption says):** from Feb 1943 German vehicles carried a Dunkelgelb (RAL 7028) base, with olive green (RAL 6003) and red brown (RAL 8017) patches applied in the field. From late 1944 vehicles also left the factory in red primer or olive base, so the exact scheme on this vehicle can't be confirmed; the grade keeps a muted dark yellow ground with darker olive brown mottles, following the patches visible in the photo. Sources: miniatures.de German camouflage timeline; armorama datasheet of Inspektorate orders (18 Feb 1943 Dunkelgelb with 6003 and 8017).
* **Pointing man's coat:** a Kradmantel, the German motorcyclist's coat of grey green rubberized fabric with a field grey wool collar (IWM catalogue 30100753). Graded grey green, low saturation.
* **Seated soldier's smock:** a Waffen-SS camouflage smock. The pattern (plane tree, oak leaf or blurred edge) can't be read from the photo, so it is graded as a muted brown green, no invented pattern colors.
* **Helmets:** field grey, kept neutral grey green.
* **Gloves:** knitted wool, neutral grey.
* **Sky:** overcast, near white with a faint cool grey (the opening days were low cloud and fog).
* **Ground:** mud and dead winter grass, muted brown.
* **Skin:** natural, warm, kept below Kodachrome saturation so faces don't go orange.

## Hero accent
The warm dark yellow of the halftrack, the one saturated color, set against the cool grey green coat and the white sky. It frames the pointing arm.

## Grades
* **Warm (recommended):** saturation 1.22, warm shift 1.03 / 1.00 / 0.96, S curve 1.08, grain 0.012.
* **Quiet:** saturation 1.12, warm shift 1.015 / 1.00 / 0.985, same curve and grain.

## Fidelity
The original luminance is restored in Lab after coloring (with only the global 1.08 S curve), and only the color channels are smoothed. Nothing is added, removed or reshaped.
* Warm: luminance mean absolute difference 0.0081 against the curved original, SSIM 0.942 (0.914 against the raw original, the difference being the global S curve and grain).
* Quiet: 0.0080, SSIM 0.942 (0.914 raw).
* Visual check at 100 percent on both faces, the pointing glove, the helmets, and the halftrack edges: no structural change. A slight grey cast remains on the halftrack just under the pointing wrist (color only).

## Credit
"A German soldier in the Ardennes offensive, December 1944. German photo, captured, U.S. National Archives (208-AA-202B-4). Colorized by WW2 Dispatches."
