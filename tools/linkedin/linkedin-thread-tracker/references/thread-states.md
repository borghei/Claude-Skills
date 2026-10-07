# Thread States

How `scripts/thread_tracker.py` turns a log into a list of things to do. The
model is deliberately small: every thread is in exactly one of nine states,
and the state depends on only two facts — **who spoke last** and **how long
ago**.

## 1. The model

A thread starts when the user logs a comment. After that it is a sequence of
turns, each recorded as an event with `who` set to `author` (the person whose
post it is), `other` (anyone else), or `me`.

```text
                     nobody has replied
  comment logged ──► WATCHING ──(watch-days)──► QUIET ──(dead-days)──► DEAD
                        │
              someone replies
                        ▼
                    YOUR-TURN ──(reply-due-hours)──► OVERDUE ──(lapsed-days)──► LAPSED
                        │
                  the user answers
                        ▼
                    AWAITING ──(settle-days)──► SETTLED
                        │
              they reply again ──► back to YOUR-TURN

  any state ──(closed by hand)──► CLOSED
```

There is no state for "the author reacted". Reactions are not turns; a thread
with a reaction and no words is still `watching`.

## 2. How each state is derived

| State | Last turn by | Time since last turn | Default |
|-------|--------------|----------------------|---------|
| `watching` | nobody | up to `--watch-days` | 4 days |
| `quiet` | nobody | over `--watch-days`, up to `--dead-days` | 4–14 days |
| `dead` | nobody | over `--dead-days` | 14 days |
| `your-turn` | author or other | up to `--reply-due-hours` | 24 hours |
| `overdue` | author or other | over `--reply-due-hours`, up to `--lapsed-days` | 1–5 days |
| `lapsed` | author or other | over `--lapsed-days` | 5 days |
| `awaiting` | me | up to `--settle-days` | 4 days |
| `settled` | me | over `--settle-days` | 4 days |
| `closed` | — | a `closed` entry exists | — |

"Time since last turn" is measured to `--as-of`, which defaults to the present
moment in UTC. Pass `--as-of` explicitly whenever the output will be compared,
shared, or checked into a routine; without it, two runs a minute apart can
disagree at a threshold boundary.

## 3. Why these numbers, and why they are only defaults

Every threshold is a **heuristic**. None is derived from how the product
ranks, surfaces, or times anything. Published figures about engagement
windows and reply timing are not reproduced here: they cannot be verified
from outside, they change, and a habit built on a stale figure is worse than
one built on courtesy.

What the defaults encode instead:

| Threshold | Default | Reasoning |
|-----------|---------|-----------|
| `--reply-due-hours` | 24 | Someone asked the user something in public. A day is a normal time to keep a person waiting; more starts to look like indifference |
| `--lapsed-days` | 5 | Past a working week, a public reply reads as an afterthought and notifies people who have forgotten the post |
| `--watch-days` | 4 | A judgement call: checking for longer costs attention for diminishing return. Calibrate it against the user's own median wait (§5) once there is enough data |
| `--settle-days` | 4 | If the other person has not come back within the same window, the exchange has ended naturally |
| `--dead-days` | 14 | After two weeks nobody is reading the post. The thread is kept until then only so the weekly review can see it |
| round cap | 2 | After the user's second answer, the tracker advises that the next one be a closing line. Long two-person exchanges under someone else's post wear on the host |

### Tuning

| If… | Change |
|-----|--------|
| The user checks twice a week, not daily | `--reply-due-hours 72`; otherwise everything is always overdue |
| The user's field moves slowly (academia, public sector) | Raise `--watch-days` and `--settle-days` to 7 |
| The log is very active and the report is long | Lower `--dead-days` to 10 and close weekly |
| Priority contacts answer late but reliably | Keep defaults and judge `quiet` priority threads by hand before giving up |

The tracker refuses thresholds that are out of order — for example a reply
window longer than the lapse window — because the states would overlap.

## 4. The report

### Ordering

Rows are sorted by state in urgency order (`overdue`, `your-turn`, `lapsed`,
then the rest), then priority tier first, then longest idle first. The first
line of the report is therefore always the thing most worth doing.

`--actionable` trims the report to the three states that need the user. Use
it for the daily check; use the full report for the weekly review.

### Fields worth reading

| Field | Meaning |
|-------|---------|
| `last_from` | Who took the last turn: the author, a named other commenter, or the user |
| `idle_hours` | Hours since that turn |
| `due_by` | When the reply is due, for `your-turn` and later states |
| `rounds` | How many times the user has answered in this thread |
| `advice` | The recommended action, including the closing-line prompt once the round cap is reached |
| `close_now` | Thread ids in `settled` or `dead`, ready to close |

### The gate

`--fail-on-overdue` exits `1` when any thread is `overdue`. It is meant for a
morning routine or a scheduled check on the user's own machine — a nudge that
a person is waiting. It does not fire on `lapsed`; by then the question is
judgement, not urgency.

## 5. Reading the metrics

Metrics cover comments logged within `--window-days` (default 30).

| Metric | What it is | How to read it |
|--------|-----------|----------------|
| `author_reply_rate_pct` | Share of logged comments where the post's author replied at least once | The headline, but dominated by who the user chooses to comment on |
| `priority_author_reply_rate_pct` | The same, for priority-tier threads only | The number that matters. These authors were chosen for who they are, not for how chatty they are |
| `any_reply_rate_pct` | Share where anyone replied | Shows whether comments start conversations among readers even when the author stays silent |
| `median_hours_to_author_reply` | Median time from the comment to the author's first reply | Tells the user how long `watching` should really last for their network. If it is 30 hours, a 4-day watch window is generous; if it is 90, widen it |
| `replies_you_left_unanswered` | Threads currently `lapsed` | Should be zero. Each one is a person who answered and heard nothing back |

### Cautions

1. **Small numbers.** Under roughly twenty comments in the window, one reply
   moves the rate by five points or more. Do not draw conclusions; keep
   logging.
2. **Selection.** The rate reflects whose posts were chosen as much as how
   good the comments were. Comparing this month to last is only fair if the
   mix of authors was similar.
3. **No benchmark.** There is no trustworthy external figure for what a
   "good" reply rate is. Compare the user to their own previous months, and
   priority to standard.
4. **Incomplete logging inflates the rate.** If only comments that got
   replies are logged after the fact, the rate approaches 100% and means
   nothing. Log at posting time.
5. **Unrecorded replies deflate it.** A reply the user saw and never logged
   counts as silence.

## 6. What the tracker cannot know

- **Anything not in the log.** It reads one file. It has never seen the post,
  the thread, or a notification.
- **Reactions**, profile views, connection requests, or messages that
  followed a comment. If these matter, mention them in a `note` or in the
  closing reason.
- **Deleted or edited comments.** If the author removed their reply, or the
  post is gone, close the thread by hand with that reason.
- **Whether a reply needs an answer.** "Thanks, that's helpful" and "How did
  you measure that?" both produce `your-turn`. The note tells the user which
  it is; the tool does not read it.
- **Whether the two people are connected**, which decides whether a direct
  message is even possible. That is a product matter to verify at the time.
- **Tone.** A hostile reply is recorded like any other. Whether to answer it
  is a judgement for the user, with `linkedin-reply-manager`'s help.

## 7. Worked example

From `assets/sample_thread_log.json` at `2026-10-07T09:00:00+00:00`:

| Thread | Facts | State | Why |
|--------|-------|-------|-----|
| T-002 | Author replied 49.5 h ago, no answer | `overdue` | Over 24 h, under 5 days |
| T-001 | Author replied 13.3 h ago | `your-turn` | Inside the 24 h window |
| T-011 | Author replied 2 h ago; user has answered twice | `your-turn` | Advice adds "make it a closing line" — round cap reached |
| T-009 | Another commenter replied 13 h ago | `your-turn` | Addressed by name in the advice |
| T-003 | Author replied 10 days ago, no answer | `lapsed` | Past 5 days; message or close |
| T-004 | No reply, 18 h old | `watching` | Inside 4 days |
| T-005 | User answered last, 3.7 days ago | `awaiting` | Inside 4 days |
| T-006 | No reply, 6.9 days old | `quiet` | Past 4 days, under 14 |
| T-008 | User answered last, 7.9 days ago | `settled` | Past 4 days; close |
| T-007 | No reply, 19 days old | `dead` | Past 14 days; close |
| T-010 | Closed by hand | `closed` | Continued by direct message |

Metrics for the same run: eleven comments, the author replied to seven
(63.6%), every priority-tier author replied, the median wait for an author
was six hours, and one reply was never answered. With eleven comments, the
rates are anecdotes; the unanswered reply is the finding.
