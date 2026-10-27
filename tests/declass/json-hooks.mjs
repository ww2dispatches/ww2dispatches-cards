// Lets plain node import the server's JSON data files the way Cloudflare's bundler does.
export async function load(url, context, next) {
  if (url.endsWith('.json')) return next(url, { ...context, importAttributes: { type: 'json' } });
  return next(url, context);
}
