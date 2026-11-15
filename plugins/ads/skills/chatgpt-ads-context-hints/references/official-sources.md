# Official sources and platform boundaries

Primary sources opened and checked October 14, 2026. Read [research-notes.md](research-notes.md) for the practical distinctions. Recheck current documentation and live account fields before applying dated facts.

| Source | What it establishes |
| --- | --- |
| [Write Context Hints](https://help.openai.com/en/articles/20001521-write-context-hints-for-chatgpt-ads) | Specific, relevant, accurate business/use-case details; a landing fact may add value when connected to a need; business context versus delivery commands. |
| [Create Ad Groups](https://help.openai.com/en/articles/20001211-create-ad-groups-for-chatgpt-ads) | Coherent group themes; separate groups when messaging or destinations need to differ. |
| [Create Ads](https://help.openai.com/en/articles/20001212-create-ads-for-chatgpt-ads) | Clear public value, distinct creative angles and accurate landing-page continuity alongside hints. |
| [Targeting](https://developers.openai.com/ads/campaign-targeting#context-hints) | Group-level relevance, not exact-match targeting; 2,000-entry ceiling, full-list replacement and saved-list readback. |
| [Ad Groups API](https://developers.openai.com/ads/api-reference/ad-groups) | Optional string-array field; descriptions or keywords supported. Short keyword examples are valid syntax, not proof of best performance. |
| [Published Ads OpenAPI schema](https://developers.openai.com/ads/openapi.json) | CreateAdGroupBody and UpdateAdGroupBody have maxItems 2000; reviewed string item schema states no per-hint min/max length. |
| [Bulk schema checklist](https://help.openai.com/en/articles/20001218-bulk-upload-campaign-schema-checklist) | Ad-group workbook hint cells are full JSON lists, not a merged append. This is outside the kit's ad-only CSV. |
| [Ads in ChatGPT](https://help.openai.com/en/articles/20001047-ads-in-chatgpt) | Hints, ad text, destination and other context are multiple relevance inputs; advertiser hints do not control assistant answers. |
| [Official best-practices webinar](https://webinar.openai.com/on-demand/067e119c-9315-4087-8006-8f4dfb236b65) | September 24 campaign-structure and measurement advice; not a hint-length, count or keyword formula. |
| [Talkpal advertiser case](https://ads.openai.com/customers/talkpal) | September 22 reported use of intent-focused groups and needs-based hints; does not isolate causal hint lift. |
| [Advertiser FAQ](https://help.openai.com/en/articles/20001220-frequently-asked-questions) | No general advertiser/industry/campaign-type performance benchmark established. |
| [Ad policies](https://openai.com/policies/ad-policies/) | Truthful capabilities/pricing/outcomes and consistent destinations; restrictions on sensitive placements and content. |

Official writing advice is not a guarantee of auction eligibility, impressions or conversions. Published API semantics do not establish every account's live UI capabilities. Examples and reported customer results do not establish a universally optimal strategy.
