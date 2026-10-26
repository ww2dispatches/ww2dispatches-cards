// The game catalog, written by renderer/catalog.py on every weekly run and bundled with the
// server code (never served as a file). Nothing here is shown or handed out before it posts:
// a dispatch card at its post time, its film at the noon video, a Name This card only once its
// answer is public (when the next Name This posts).
import data from '../_data/catalog.json';
import { gameDay } from './time.js';

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

// Every envelope time: one per distinct dispatch post time, oldest first.
export const SLOT_TIMES = [...new Set(CARDS.filter(c => c.kind === 'dispatch').map(c => c.postAt))].sort();

// Archive pools for envelopes. Weekday archive pulls: dispatches posted in the last 90 days.
// Deep archive (Sunday morning, priority, commemorative): everything posted, Name This included.
// Flash cards never sit in the ordinary pools: they come only from their commemorative file and
// from the separate 1 in 200 Flash roll on every archive slot (Roadmap, Flash cards plan).
export function archivePool(t, days = 90) {
  const since = iso(new Date(t.getTime() - days * DAY_MS));
  return CARDS.filter(c => c.kind === 'dispatch' && !c.flash && released(c, t) && c.postAt >= since);
}
export const deepPool = t => postedCards(t).filter(c => !c.flash);
export const flashPool = t => CARDS.filter(c => c.flash && released(c, t));

// The Flash cards a commemorative file hands out: this year's Flash card for the file's date (and the
// next day's too, so the 1 and 2 September file carries both), posted and released by the moment it is
// opened. Each date gets a new Flash card every year, so the newest posted one for each event date wins.
export function flashForFile(fileDay, t) {
  // Only the 1 and 2 September file carries two days (bug sweep, 26 Oct 2026).
  const md = fileDay.slice(5), next = md === '09-01' ? nextDay(fileDay).slice(5) : null;
  const out = new Map();
  for (const c of flashPool(t).sort((a, b) => a.postAt.localeCompare(b.postAt))) {
    const emd = c.date.slice(5);
    if (emd === md || emd === next) out.set(emd, c);
  }
  return [...out.values()];
}
function nextDay(day) { const d = new Date(day + 'T12:00:00Z'); d.setUTCDate(d.getUTCDate() + 1); return d.toISOString().slice(0, 10); }

// "Today's cards" (never requestable): released during the current Eastern game day, or still in their
// 24 hour daily envelope.
export function isTodayCard(card, t) {
  const rel = Date.parse(card.kind === 'namethis' ? card.answerAt : card.postAt);
  return gameDay(new Date(rel)) === gameDay(t) || t.getTime() - rel < DAY_MS;
}

// What the dossier grid needs for each card.
export function summary(card, t) {
  const s = {
    kind: card.kind, id: card.id, num: card.num, series: card.series, seriesName: card.seriesName,
    short: card.short, title: card.title, date: card.date, place: card.place, era: card.era,
    format: card.format, postAt: card.postAt, img: card.img, hasFilm: filmReleased(card, t), flash: Boolean(card.flash),
    subjects: card.subjects, theater: card.theater, nations: card.nations, who: card.who, happened: card.happened, branch: card.branch,
  };
  s.today = isTodayCard(card, t); // today's cards can never be requested
  if (s.hasFilm) Object.assign(s, { filmMp4: card.film.mp4, filmPoster: card.film.poster, filmSound: card.film.sound });
  if (card.kind === 'namethis') Object.assign(s, { answer: card.answer, clue: card.clue, imgPuzzle: card.imgPuzzle });
  return s;
}

// Everything the card view needs; the film only once the noon video has posted.
export function detail(card, t) {
  return { ...card, film: filmReleased(card, t) ? card.film : null };
}
