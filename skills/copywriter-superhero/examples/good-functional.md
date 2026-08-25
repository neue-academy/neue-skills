# Good functional — passing example

Three functional forms: a terms excerpt, a data-retention table, and a transactional email,
plus release notes. Zero persuasion. Precision first, navigability second, readability
third, brevity last.

```bash
python3 skills/copywriter-superhero/scripts/score_copy.py \
  skills/copywriter-superhero/examples/good-functional.md --regime functional
```

This regime loads the plain-language table on top of the buzzword table, blocks passive
voice and buried verbs, and enforces a reading-grade ceiling. Hedges are not scored, because
"may" and "must" are load-bearing words in a contract.

> **Drafted, not advised.** A qualified lawyer reviews anything in this regime before it
> goes live. Where their wording conflicts with a rule here, their wording wins.

---

## Part one — terms of service, section 4

### 4. Cancelling your plan

**4.1** You may cancel at any time from Settings → Billing, or by emailing
billing@example.com. We end your plan within one business day of your request.

**4.2** We charge you for the current month. We do not charge you again after that. We do
not refund part of a month, with one exception: if you cancel within 14 days of your first
payment, we refund that payment in full.

**4.3** You keep access until the end of the month you have paid for. After that, you can
sign in for 90 days to export your data. We delete your projects 90 days after your plan
ends.

**4.4** If we end your plan, we tell you why, in writing, at least 30 days first. We refund
any month you have paid for and not used. We may end your plan sooner in two cases only:
you have not paid for 60 days, or you have used the service to attack another customer.

**4.5** Ending your plan does not cancel an invoice you already owe us.

---

## Part two — data retention

We keep each category of data for the period below, then delete it.

| Data | Why we keep it | How long | Who else sees it |
|---|---|---|---|
| Name, email | To sign you in and contact you about your account | Until you close your account, then 30 days | Nobody outside our company |
| Payment card | To take payment. We never store the full number | Our payment processor keeps it. We keep the last 4 digits for 7 years | Stripe, as our processor |
| Invoices | UK tax law requires it | 7 years from the invoice date | Our accountant, HMRC on request |
| Project files | To give you the service | Until you delete them, then 90 days in backups | Nobody outside our company |
| Support emails | To answer you and check our own work | 3 years | Nobody outside our company |
| Server logs | To find faults and abuse | 90 days | Nobody outside our company |

You can ask us for a copy of all of it, or ask us to delete it, at privacy@example.com. We
answer within 30 days. If you think we have got this wrong, you can complain to the ICO at
ico.org.uk/concerns.

---

## Part three — transactional email

**Subject:** Your card was declined — invoice 4471, £95

Your payment of £95 for invoice 4471 did not go through on 4 March. Your bank declined the
card ending 4412.

We try again on 7 March and 11 March. Nothing changes about your account before then.

If it fails on 11 March, we pause your plan. Your projects stay where they are, and you keep
30 days to fix the card and carry on.

To fix it now: Settings → Billing → Update card. It takes about a minute.

If your bank told you why it declined the card, forward that message to
billing@example.com and we will tell you what to change.

---

## Part four — release notes, v4.2.0

### Breaking

- **The `/v1/export` endpoint closes on 1 June 2026.** Move to `/v2/export`, which returns
  the same fields plus `render_id`. Migration guide: docs.example.com/v2-export.

### Added

- Search now matches partial words. Typing "grang" finds "Grange Road".
- You can export a project as CSV from the project menu.

### Changed

- Renders now queue one per seat instead of one per account, so two people on the same team
  no longer wait for each other.
- Invoice emails now carry the invoice PDF as an attachment.

### Fixed

- Fixed a bug where deleting a folder left its files in search results for up to an hour.
- Fixed a crash when a project name contained an emoji.

---

## Why this passes

**Second person, present tense, active voice.** "We end your plan within one business day"
names the actor and the deadline. The same clause in standard drafting — "the Subscriber's
plan shall be terminated by the Company" — binds identically and reads worse.

**Real deadlines, never standards of effort.** 14 days, 30 days, 60 days, 90 days, 7 years,
4 March, 11 March. Nothing says "promptly" or "using reasonable efforts", because both move
the argument from the document to a court.

**One obligation per sentence.** Clause 4.2 could be one 60-word sentence. It is four short
ones, and each states a single rule that can be disputed on its own.

**The rule comes first, the exception second.** A reader who stops halfway through 4.2 stops
on the correct default.

**The retention table beats prose.** Six categories with four attributes each is 24 facts.
As paragraphs it is unreadable; as a table a reader finds their row in seconds.

**The transactional email leads with the fact and says what happens if you do nothing.**
That last part is the field most often left out and most often needed.

**Release notes are written from the user's side.** "Search now matches partial words", not
"Refactored the search indexer". Breaking changes come first, with the migration inline.

Full rulebook: [../references/functional-and-legal.md](../references/functional-and-legal.md).
