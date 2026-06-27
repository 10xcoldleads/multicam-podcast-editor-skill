# QC And Ledger

## Objective QC

Run before approving any output.

Probe:

```powershell
ffprobe -v error -show_entries stream=index,codec_type,codec_name,width,height,r_frame_rate,duration -show_entries format=duration,size,bit_rate -of json "render.mp4"
```

Black frames:

```powershell
ffmpeg -hide_banner -nostats -i "render.mp4" -vf blackdetect=d=0.3:pix_th=0.10 -an -f null - 2>&1
```

Freeze frames:

```powershell
ffmpeg -hide_banner -nostats -i "render.mp4" -vf freezedetect=n=-60dB:d=1.5 -an -f null - 2>&1
```

Loudness:

```powershell
ffmpeg -hide_banner -nostats -i "render.mp4" -filter_complex ebur128=peak=true -f null - 2>&1
```

Sync drift:

- Build camera-scratch reference audio for several output timeline windows by replaying the edit plan against the selected camera scratch tracks.
- Extract rendered audio for the same output timeline windows.
- Correlate scratch-audio envelopes against rendered-audio envelopes.
- Check at least early, middle, and late windows. Treat lag above roughly 0.20s as a rejection unless manually inspected and justified.

Frames:

```powershell
ffmpeg -hide_banner -y -ss 00:20:00 -i "render.mp4" -frames:v 1 -update 1 "qc_frame_20m.jpg"
```

Inspect representative frames for crop, text, face visibility, nonblank output, and visual plausibility.

## Social Clip QC

For each final short, record:

- output folder and clean handoff folder
- clip start/end on the studio transcript timeline
- chosen visual layout: active-speaker crop, wide/two-shot, or two-speaker stack
- whether the speaker visible at hook/middle/end matches the active speaker
- caption source: word-level transcript, ASS, manual, or HyperFrames
- caption timing notes: no visible lag, no overlap, no face/mouth obstruction
- HyperFrames lint/inspect result when used
- final media QC result

Create or update a contact sheet from final MP4s. Do not approve from draft frames.

## Freeze Flags

Podcast listener shots can trigger false freeze positives. Do not automatically reject. Extract the flagged frame and inspect:

- natural still listener/reaction: acceptable
- frozen render / repeated frame artifact: reject

## Approval Standard

An output is not accepted until:

- sync mapping has been verified
- output-window sync lag has been checked after final render
- active speaker camera logic matches the conversation
- shorts show the active speaker or a justified two-speaker layout
- encoded audio passes loudness and true peak
- black/freeze checks have been run
- representative frames are visually inspected
- rejected/superseded versions are clearly labeled

## Cleanup Standard

After accepted finals are copied to a clean handoff folder:

- delete temporary base clips that can be regenerated
- delete `.video_only.mp4` files after audio muxing
- delete HyperFrames `work-*` render folders and extracted frame caches
- delete superseded render folders such as older v1/v2 social batches
- keep raw sources, transcripts, edit scripts, ledgers, final masters, and accepted delivery folders

Before deleting duplicates outside the project workspace, verify a project copy exists and byte sizes match.

## Ledger Files

Maintain these files in the project:

- `ASSET_LEDGER.md`: raw sources, probes, derived files, accepted/rejected renders
- `SYNC_LEDGER.md`: camera roles, audio roles, offsets, mapping convention, sync proofs
- `EDIT_DECISIONS.md`: editorial structure, camera rules, QC notes
- `CLIP_CANDIDATES.md`: ranked clips and statuses
- `MEMORY.md`: concise state for future resume

Record exact filenames, durations, LUFS/true peak, black/freeze results, and rejection reasons.
