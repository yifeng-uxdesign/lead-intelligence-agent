# ICP sources verification: INCOMPLETE (network blocked)

Date: 2026-11-15. Status: **no source page could be opened in this session.** Nothing below is a finding about what a source says.

## What happened
- WebFetch failed with `getaddrinfo ENOTFOUND` for all six hosts tried: www.poweredbysearch.com, www.flighted.co, callingly.com, visionary-marketing.co.uk, blog.abmatic.ai, www.g2.com. The remaining listed hosts were not tried with WebFetch, because the tool said to stop after repeated failures.
- curl through the session proxy returned `CONNECT tunnel failed, response 403` (policy denial) for the host root of every listed source (including the poweredbysearch /learn/ path, pipeline.zoominfo.com, autobound.ai, leadhaste.com, wonderchat.io, voiceflow.com, kickscale.com, workato.com), for hbr.org, and for the Internet Archive. Per the proxy README, policy denials are not retried or bypassed.
- Fix needed: these hosts must be added to the environment's allowed network hosts, then this task rerun.

## Claim status in ICP_DRAFT.md
All claims: **NOT CHECKED** (not CONFIRMED, CORRECTED or UNSUPPORTED). Counts: 0 confirmed, 0 corrected, 0 unsupported.

## One lead, from a search summary only (not an opened source)
A web search (titles and snippets only) indicates the HBR article exists: "The Short Life of Online Sales Leads", Harvard Business Review, March 2011 (vol. 89, issue 3), by James B. Oldroyd, Kristina McElheran and David Elkington (listed at https://scholarsarchive.byu.edu/facpub/9711). Secondary snippets disagree on the sample (2,241 companies; other snippets say 1.25 million leads or 15,000 leads) and on the headline figure (an average response of 42 hours is the most quoted). One snippet says the 100x/21x multipliers are wrongly pinned on HBR. I did not open the article, so the "2,241" origin and every number here are **unverified**.

## Independent evidence
None found or opened (Gartner, Forrester, G2, HubSpot, academic). The HBR article, if confirmed, would be the closest to independent (academic authors).

## Suggested ICP_DRAFT.md changes
None yet that this session can support. Do not change the draft on the basis of this file.
