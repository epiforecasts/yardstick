# Working with agents on this repository

Conventions for anyone, human or agent, opening issues or pull requests here. They exist so
that a reviewer can tell where a decision is a person's and where it is a model's, and where
contributions are invited, without reading every session that produced the work.

## Lines of inquiry

A line of inquiry (a question worth tracking on its own, such as a methods decision or a
recurring source of bugs) gets a parent issue. Issues and pull requests that belong to it are
opened as sub-issues of that parent, not as standalone items. This keeps a flat issue list from
hiding which items are routine steps and which are the question that matters.

## The `input wanted` label

Apply `input wanted` to an issue or pull request where outside contributions or opinions are
wanted, and remove it once that is no longer the case. Its absence is not a judgement on an
item, only silence on whether comment is wanted.

## The notebook

`NOTEBOOK.md` holds dated entries, newest first, each tagged with its line of inquiry (for
example `[corpus]`) and linked to the issues and pull requests it covers. An entry records the
reasoning the code doesn't show: what the work set out to do and why; what was done, in terms
of the question; what was tried and dropped; how the question changed; and what is still
uncertain. An entry is drafted after the line of inquiry's work (or a significant step in it)
is done, by an LLM if one did the drafting; a person then reviews and edits the text before it
is merged.

Entries are never edited once merged. If later work changes what an entry says, a new entry
records that and names the entry it supersedes.

The notebook is not a replacement for issues and pull requests, which keep the full detail; it
is where someone catching up starts.

## Intent lines

Every issue drafted by an LLM opens with a line or two of intent in a person's own words: why
this is worth opening, stated by the person who wants it done, not generated. The rest of the
issue can be drafted by the LLM. The intent line may be tidied for clean language, but stays
the person's own reasoning, not a rewrite of it, and leaves out any mention of other people.

Every pull request that does not close an issue opens the same way: a line or two from a person
on why the change is wanted. A pull request that closes an issue already has its intent in that
issue and does not need to repeat it.

Example:

> **Intent** (in the author's own words): the calibration counts in the README are stale since
> the exclusion rules changed.
>
> *The rest of this issue was drafted by an LLM.*

An automated check (`.github/workflows/pr-conventions.yml`) fails a pull request whose
description has neither an intent line nor a reference to an issue it closes. It checks for the
presence of either, not for whether an intent line reads as genuinely a person's own words; that
judgement is left to review.

## Attribution

Text an LLM drafted, in an issue, pull request, or comment, is either posted from the
`sbfnk-bot` account or says plainly that an LLM drafted it. Nobody should have to guess, from
the text alone, whether a person or a model wrote it.

A pull request names a person's decision only where that person overturned the agent: went
against what the agent proposed or did. Everywhere else, a decision is described without
naming who made it.

## Open problem

These conventions do not address unequal access to AI tools across contributors. Someone
without access to an agent can still open issues and pull requests in the usual way; they are
simply not expected to add an LLM-drafted notebook entry or sub-issue.
