# Learning Record Entries — copy into learning-record.json

## New item
```json
{"id": "C<n>", "concept": "<one testable idea, phrased as a claim>", "module": "M<n>",
 "state": "new", "introduced": "YYYY-MM-DD", "evidence": "", "reviews": []}
```
Promote to `learning` only with evidence: an action the learner performed
("rewrote the caption correctly"), never an exposure ("covered in lesson 4").

## Review result (append to the item's reviews)
```json
{"date": "YYYY-MM-DD", "result": "recalled|partial|failed"}
```
- recalled: correct from memory, no hints, normal speed
- partial: correct with a hint, or core right and a detail wrong
- failed: could not produce it, or produced the wrong model

## Misconception
```json
{"id": "X<n>", "belief": "<the wrong model in the learner's words>",
 "correction": "<the replacement model>", "status": "open",
 "found": "YYYY-MM-DD", "recheck": "YYYY-MM-DD", "item": "C<n>"}
```
Set `recheck` 2-5 days out. Mark `corrected` only after a recheck on a new surface succeeds.

## Session
```json
{"n": <n>, "date": "YYYY-MM-DD", "module": "M<n>", "lesson": "lessons/NNNN-slug.md", "notes": ""}
```
