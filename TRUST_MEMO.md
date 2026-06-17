# Trust Memo — TalkToData

**To:** The CEO
**From:** Founding Engineer, TalkToData
**Re:** Can you trust the numbers? Should it run unsupervised?

---

## The recommendation: keep the human in the loop — but make the loop one glance

TalkToData should **not** run fully unsupervised. It should answer instantly and
always show its work, so that acting on a number takes one extra glance, not a
three-day wait. We have not made the language model perfect — that is not
possible. What we have done is make its mistakes **catchable**. That distinction
is the whole product.

Concretely, every answer is returned with the exact SQL that produced it and a
review note. Destructive queries (`DROP`, `DELETE`, `UPDATE`, …) are blocked
outright, and queries that reference tables we don't have are rejected before
they ever run. So "supervision" here is not a data analyst re-doing the work —
it is you, or any manager, reading one line of SQL before acting on a number that
drives a real decision.

## A real example of "valid but wrong" from our own testing

We asked: **"What is the average order value for repeat customers?"**

On one run the model produced the faithful query — it joined to the customers
table and filtered to repeat customers — and returned **₹5,123.86**. On other
runs, against the very same question, it produced this instead:

```sql
SELECT AVG(total_amount) FROM orders
```

This runs without any error and returns a clean **₹5,067.18**. But it is the
average of **all** orders — it silently ignored "repeat customers" entirely: no
join, no filter. The number is **wrong, and only about 1% away from the right
one** — close enough that nobody would catch it by looking at the number alone.
If a restock or targeting decision rode on it, we'd be acting on the wrong data
and never know. The same model gives the right query on some runs and this wrong
one on others; that non-determinism is exactly why a single answer cannot be
trusted blindly — and exactly why we show the SQL.

## Two kinds of questions I would never let it answer without a human checking

1. **Questions with an implicit filter or segment** — "repeat customers," "last
   week," "active users," "returning buyers." The danger is precisely the example
   above: the model can drop the filter or the join and still return a fluent,
   valid, believable number. The wrongness is invisible in the result and only
   visible in the SQL.

2. **Questions over an ambiguous business definition or a multi-table metric** —
   "which product gets returned most often," or anything involving "revenue."
   A return is recorded against an *order*, and an order contains several
   products, so "the returned product" is genuinely undefined; "revenue" is not a
   stored column but a computation (`quantity × price`). Here even *correct-looking*
   SQL may faithfully answer a *different* question than the one you meant. A human
   reading the query is the only thing that catches a reasonable-but-wrong
   interpretation.

## How my understanding of "trust" changed

Before building this, I would have said trust meant accuracy — get the number
right. After building it, I think that is the wrong target, because a learned
model will sometimes be confidently wrong and there is no way to make that never
happen. Trust is not "the machine is always right." Trust is **"when the machine
is wrong, I can see it before I act."** That reframing is why the SQL viewer is
not decoration and the guardrails are not extras — they *are* the product. The
machine writes the query in seconds; the human still decides whether to trust the
answer. That is what turns an impressive demo into something a company can
actually run on.
