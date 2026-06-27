# Multicam Podcast Editor Skill

Codex skill for editing multicam podcast/interview recordings into synced longform masters and short-form social clips.

## What It Covers

- camera intake and scratch-audio sync against a studio audio clock
- active-speaker camera selection for host, guest, wide, and reaction angles
- longform edit-plan generation and sync-safe rendering
- dialogue bus audio targets for longform and shorts
- HyperFrames social clip packaging with speaker-aware vertical crops, two-speaker stacks, word-cued captions, and QC
- output validation with ffprobe, loudness, black/freeze checks, sync proof, contact sheets, and cleanup rules

## Install

Copy the skill folder into your Codex skills directory:

```powershell
Copy-Item -Recurse .\multicam-podcast-editor "$env:USERPROFILE\.codex\skills\multicam-podcast-editor"
```

Restart Codex or start a new session so the skill is discoverable.

## Use

Ask Codex to use the skill for a real podcast project:

```text
Use $multicam-podcast-editor to ingest these camera/audio files, sync the cameras, build a speaker-aware edit plan, render the longform master, pull short clips, and QC the outputs.
```

Keep raw media out of this repo. The skill expects project media to live in the working project folder.
