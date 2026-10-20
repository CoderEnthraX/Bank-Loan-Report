# Model & effort routing (always apply)

You orchestrate work. For every sub-agent or workflow agent you launch, pick the cheapest
model and effort that will NOT reduce the quality of the final result. Accuracy beats savings:
when unsure, go one tier up, never down.

## Step 1: Classify each piece of work before launching it

| Tier | Kind of work | Model | Effort |
|---|---|---|---|
| T1 Mechanical | Search/grep, listing files, reading or extracting data, cropping images, renaming, formatting, copying, simple scripts with an exact spec | haiku | low |
| T2 Routine | Ordinary coding with a clear spec, code review / compile checks, re-running or reproducing a known result, summarising, writing docs/READMEs | sonnet | medium |
| T3 Verification | Adversarial checks of a finding, test design, parity checks between two implementations, statistics on a claimed result | sonnet | high |
| T4 Hard reasoning | Reverse-engineering unknown rules, new algorithms, debugging with no clear cause, architecture/design decisions, anything where being wrong changes the final deliverable | opus (session model) | high or xhigh |
| T5 Critical | The single deciding step of a long project, final synthesis of many results, problems that already failed at T4 | opus | max |

Rules:
- Any agent whose output decides what goes into the deliverable (rules, logic, numbers the
  user relies on) is at least T4. Never downgrade it to save tokens.
- Checking work may be T2/T3 only if I (the main session) also verify the result myself, or a
  second independent agent agrees.
- If a cheaper agent's answer looks wrong, thin or uncertain, re-run that step one tier higher
  rather than accepting it.
- Mixed tasks: split them, so the mechanical parts go to haiku and the thinking parts stay on opus.

## Step 2: Choose how to run it

- Small task (< ~15 minutes of work, one file or one question): do it yourself, no sub-agents.
- Independent pieces of work: run them in parallel, each with its own model/effort from the table.
- Large or multi-phase projects (research, reverse-engineering, audits, migrations): use a
  workflow. If Ultracode is off and the task is clearly large, tell me in one line that
  Ultracode (or "use a workflow") would help, and how many agents it would roughly take.

## Step 3: Keep token use lean

- Give agents short, specific prompts: the goal, the exact files/paths, what's already
  ruled out and the output format. Don't paste long context they don't need.
- Every long-running agent writes progress to a checkpoint file after each step and reads it
  on start, so a usage-limit stop never forces a restart from zero.
- Agents read only the parts of files/images they need (crop images, use offset/limit).
- Don't re-run finished agents. Resume workflows from cache.

## Step 4: Be transparent

- When you launch agents, state in one line which model/effort each one got and why.
- In the final summary, say which steps ran on cheaper models and how their results were checked.
- Never claim results a cheaper agent produced without checking them.
