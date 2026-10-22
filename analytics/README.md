# analytics/

The Wednesday analytics review's working folder. The method and the weekly steps are in the Project's Analytics doc; this file covers the files and the snapshot format.

| File | What it is | Who writes it |
|---|---|---|
| `snapshots/YYYY-MM-DD.json` | That week's raw Buffer pull. Never edited after it is saved. | Wednesday review |
| `themes.md` | The fixed list of theme tag values. | Wednesday review only |
| `playbook.md` | The current lessons, read by the Thursday and Friday runs. | Wednesday review |
| `reviews/YYYY-MM-DD.md` | Each week's written review. | Wednesday review |
| `scoreboard.json` | Everything the Scoreboard page shows. | `renderer/analytics.py` |
| `scoreboard-template.html` | The Scoreboard page, with a placeholder for the data. | By hand (Claude) |
| `scoreboard-page.html` | The page with the data built in, published to the Scoreboard artifact. | `renderer/analytics.py` |

`log/performance-log.csv` (one row per post per platform) is also written by `renderer/analytics.py`. Never edit any generated file by hand.

## Pulling the snapshot
Use the Buffer connector's `execute_query` (organization 6ad05f69516ac0f2b606b889), covering every post sent in the last 14 days, so each post is caught again once it is 7 or more days old. Page with `after` until `hasNextPage` is false.

```graphql
query($org: OrganizationId!, $start: DateTime!, $end: DateTime!, $after: String) {
  posts(first: 50, after: $after, input: {organizationId: $org,
        filter: {status: [sent], dueAt: {start: $start, end: $end}},
        sort: [{field: dueAt, direction: asc}]}) {
    pageInfo { hasNextPage endCursor }
    edges { node { id channelService via sentAt externalLink metricsUpdatedAt
      assets { type ... on ImageAsset { image { altText } } ... on VideoAsset { video { durationMs } } }
      metrics { type value } } }
  }
}
```

## Snapshot format
One file per week. Copy the values exactly; keep only the first 60 characters of the alt text (it is used only to spot Name This posts that Typefully sent to X).

```json
{
  "pulled_at": "2026-10-28T19:50:00Z",
  "posts": [
    {"id": "<Buffer post id>", "service": "threads", "via": "buffer",
     "sent": "<sentAt>", "link": "<externalLink>", "updated": "<metricsUpdatedAt>",
     "dur": 0, "alt": "WW2 Dispatches card, Dispatch No. 007, Battle Lines.",
     "m": {"reactions": 20, "comments": 0, "views": 800, "quotes": 1, "reposts": 1}}
  ]
}
```

`dur` is the video's `durationMs` (0 for images). `m` holds every metric Buffer returned, by its `type`, leaving out `engagementRate`. A post whose `metrics` is null gets `"m": {}`.
