// The game catalog, written by renderer/catalog.py on every weekly run and bundled with the
// server code (never served as a file). Nothing here is shown or handed out before it posts:
// a dispatch card at its post time, its film at the noon video, a Name This card only once its
// answer is public (when the next Name This posts).
import data from '../_data/catalog.json';

const CARDS = data.cards;
const BY_ID = new Map(CARDS.map(c => [c.id, c]));
const DAY_MS = 86400000;

// The server's clock. A fake time is allowed only on a local or test copy (ALLOW_FAKE_NOW = "1"),
// so the live site can never be asked to read ahead.
export function now(env, request) {
  if (env.ALLOW_FAKE_NOW === '1') {
    const fake = request.headers.get('x-declass-now');
    if (fake && !Number.isNaN(Date.parse(fake))) return new Date(fake);
  }
  return new Date();
}

const iso = t => t.toISOString().replace(/\.\d{3}Z$/, 'Z');

export function released(card, t) {
  const at = iso(t);
  if (card.kind === 'namethis') return Boolean(card.answerAt) && card.answerAt <= at;
  return card.postAt <= at;
}

export const filmReleased = (card, t) => Boolean(card.film) && card.film.postAt <= iso(t);

export function findCard(id, t) {
  const card = BY_ID.get(id);
  return card && released(card, t) ? card : null;
}

export const postedCards = t => CARDS.filter(c => released(c, t));

// The dispatch card that posts at exactly this slot time (an envelope's guaranteed card).
export const slotCards = slotIso => CARDS.filter(c => c.kind === 'dispatch' && c.postAt === slotIso);

// Archive pools for envelopes. Weekday archive pulls: dispatches posted in the last 90 days.
// Deep archive (Sunday morning, priority, commemorative): everything posted, Name This included.
export function archivePool(t, days = 90) {
  const since = iso(new Date(t.getTime() - days * DAY_MS));
  return CARDS.filter(c => c.kind === 'dispatch' && released(c, t) && c.postAt >= since);
}
export const deepPool = t => postedCards(t);

// What the dossier grid needs for each card.
export function summary(card, t) {
  const s = {
    kind: card.kind, id: card.id, num: card.num, series: card.series, seriesName: card.seriesName,
    short: card.short, title: card.title, date: card.date, place: card.place, era: card.era,
    format: card.format, postAt: card.postAt, img: card.img, hasFilm: filmReleased(card, t),
    subjects: card.subjects, theater: card.theater, nations: card.nations,
  };
  if (card.kind === 'namethis') Object.assign(s, { answer: card.answer, clue: card.clue, imgPuzzle: card.imgPuzzle });
  return s;
}

// Everything the card view needs; the film only once the noon video has posted.
export function detail(card, t) {
  return { ...card, film: filmReleased(card, t) ? card.film : null };
}
