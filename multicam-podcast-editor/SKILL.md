---
name: multicam-podcast-editor
description: Produce polished real-footage multicam podcast and interview edits from multiple camera angles, isolated speaker audio, camera scratch audio, and transcripts. Use when Codex needs to ingest completed podcast studio recordings, sync cameras to a studio audio clock, select camera angles by active speaker, render longform masters, create Shorts/Reels clips with captions or HyperFrames overlays, master voice-led audio, run FFmpeg QC, and maintain a production ledger.
---

# Multicam Podcast Editor

## Core Rule

Treat studio audio / transcript time as the master clock.

1. Sync every camera to the studio clock from camera scratch audio.
2. Choose the edit on the studio timeline.
3. Choose the camera by active speaker and editorial intent.
4. Convert studio source time into camera seek time only after the camera is selected.
5. Verify audio/video sync on encoded outputs, not just on source probes.

Never cut by raw camera file time alone.

## Required Inputs

- Completed camera files, not `.crdownload` or partial files.
- Camera scratch audio, ideally embedded in each camera file.
- Studio mix or dialogue bus.
- Isolated speaker tracks when available.
- Transcript with segments or word timestamps.

If isolated speaker tracks are unavailable, use diarization or transcript speaker labels, then verify manually.

## Workflow

1. Read `references/intake-sync.md` for source intake, probing, hard-link/copy decisions, and sync.
2. Read `references/active-speaker-editing.md` before creating the edit plan.
3. Read `references/audio-mastering.md` before rendering final audio.
4. Read `references/qc-ledger.md` before approving any output.
5. Read `references/social-clips-hyperframes.md` when producing Shorts/Reels, captions, lower thirds, title cards, HyperFrames packages, or optional Remotion social templates.

## Decision Rules

- Use FFmpeg/FFprobe for source probing, extraction, rendering, and QC.
- Use the studio mix for transcript and sync reference.
- Use isolated speaker tracks for the final dialogue bus when possible.
- When two isolated speaker tracks are available, run `scripts/analyze_podcast_flow.py` after transcription to classify active speaker, find intro candidates, and flag interruption/filler candidates for manual editorial review.
- Build a machine-readable edit plan before rendering longform.
- Preserve the real footage; do not use AI-generated video for documentary/podcast source replacement unless the user explicitly asks.
- HyperFrames is optional for the core multicam edit. Use it for deterministic graphics, captions, quote cards, lower thirds, title cards, motion packages, and polished social output.
- Remotion is optional and should not replace sync, camera cutting, audio mastering, or QC. Use it only as a programmable React renderer for reusable branded short-form templates when that is more useful than HyperFrames.
- For social clips, make a diligent speaker-on-screen pass: active speaker close-up is preferred, two-speaker split-screen is preferred when context or interviewer/guest credibility matters, and wide/reaction angles are used only when they improve the moment.
- Keep only accepted finals and reusable project assets after approval. Delete superseded renders, temporary base clips, leftover render work folders, extracted frames, and duplicated handoff copies once a clean final folder exists.

## Camera Selection

- Active speaker close-up is the default.
- Use wide/two-shot for mixed speech, short back-and-forth, laughs, interruptions, and geography resets.
- Use listener/reaction shots only when the reaction adds meaning.
- For Shorts/Reels from interviews, prefer a vertical two-speaker stack when the user wants both interviewer and guest present or when the hook depends on conversational context.
- Avoid cutting on every word. Prefer thought boundaries, pauses, hand gesture beats, and speaker changes.
- When a chosen camera cannot cover the source time, choose the next best angle that can cover it.

## Audio Targets

- Longform podcast/video: around -16 LUFS integrated, true peak below -1.5 dBFS/dBTP.
- Short-form social: around -14 LUFS integrated, true peak below -1.5 dBFS/dBTP.
- The voice is the lead instrument. Music/SFX must never compete with dialogue.
- Always measure the encoded output, not only the pre-encode filter graph.

## Required QC Before Approval

- FFprobe duration, resolution, fps, codecs, audio sample rate.
- Loudness and true peak on the encoded output.
- Blackdetect and freezedetect.
- Representative frame inspection.
- Sync proof around at least one host-speaking and one guest-speaking moment.
- For shorts, verify the visible speaker(s), caption timing, title safe margins, face/mouth occlusion, and source sharpness from early/mid/late frames or a contact sheet.
- Ledger update with accepted, rejected, and superseded outputs.
- A clean final delivery folder containing only accepted deliverables.

## Output Expectations

For a full project, produce:

- `ASSET_LEDGER.md`: source inventory, sync offsets, derived files, render statuses.
- `SYNC_LEDGER.md`: camera roles, audio roles, offsets, mapping convention, sync proof path.
- `EDIT_DECISIONS.md`: edit-plan logic, accepted/rejected outputs, QC notes.
- `CLIP_CANDIDATES.md`: ranked clip candidates with status.
- `MEMORY.md`: concise continuation state for future resumes.

## Critical Failure Modes

- Reversed offset sign: verify with scratch-audio residuals before rendering final outputs.
- `.crdownload` intake: never treat incomplete downloads as source.
- Wrong camera on speaker: active speaker must drive angle selection.
- Loudness pass with true-peak failure after AAC encode: reject and re-render audio with true-peak control.
- Caption hook interpolation in PowerShell: quote `$` text safely and inspect the generated subtitle file or frames.
