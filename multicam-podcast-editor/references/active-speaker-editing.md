# Active-Speaker Editing

## Edit Plan First

Create a JSON or CSV edit plan before rendering. Each edit should include:

- edit index
- output timeline start/end
- source studio start/end
- chosen camera
- camera seek start
- speaker label
- speaker RMS evidence or diarization confidence
- transcript text

## Speaker Detection

Use isolated mic RMS when available:

- host is active when host RMS is meaningfully louder than guest RMS.
- guest is active when guest RMS is meaningfully louder than host RMS.
- mixed when both are close or overlapping.

Use transcript boundaries to prevent frantic cutting inside a sentence.

When isolated tracks are unavailable or unreliable, combine:

- transcript speaker labels or diarization
- scratch-audio energy by camera
- visual mouth movement from early/mid/late proof frames
- manual correction for overlaps, laughter, and crosstalk

Do not trust diarization blindly. Use it to propose camera choices, then audit the actual face on screen against who is speaking.

## Camera Choice

Default:

```text
if mixed speech or very short exchange: wide
else if host speaking: host close-up
else if guest speaking: guest close-up
else: wide
```

Add editorial resets:

- periodic wide shot every several shots
- wide shot at topic changes
- wide shot for laughs, overlap, handoff moments, and context
- reaction shot only when it adds meaning

## Two-Speaker And Split-Screen Rules

Use split-screen deliberately, not as a fallback.

For longform:

- use active-speaker close-up for most monologue answers
- use wide/two-shot for overlapping speech, fast handoffs, laughs, and relationship context
- use split-screen only when the style calls for persistent dual presence or both faces are needed to understand the exchange

For Shorts/Reels:

- show the active speaker clearly whenever possible
- use vertical two-speaker stack when both interviewer and guest should be present throughout the clip
- place interviewer on the top half and guest on the bottom half unless a project-specific design says otherwise
- crop each speaker around face, mic, shoulders, and expressive hands
- preserve source sharpness by cropping from the original camera angles and scaling with a high-quality scaler before adding graphics
- keep captions and overlays in the divider/torso bands so they do not cover eyes or mouths

If only one person is speaking but the interviewer reaction adds credibility, use a two-speaker stack or brief reaction shot. If the reaction distracts, keep the active speaker full-frame.

## Coverage Checks

Before assigning a camera:

```text
camera_start = source_start - camera_offset
camera_end = source_end - camera_offset
camera_start >= 0
camera_end <= camera_duration - safety_margin
```

If the chosen camera cannot cover the source range, fall back to wide or another valid camera.

## Longform Rhythm

Longform should feel like an edited conversation, not a machine-gun jump-cut:

- Keep meaningful pauses.
- Remove dead air, technical setup, obvious repeats, and empty filler.
- Cut on thought boundaries when possible.
- Avoid overcutting during emotional answers.
- Use wide shots to re-establish both people after long close-up runs.

## Cut Quality Audit

After building the edit plan and before final render, run a transcript-aware cut audit:

- remove explicit production notes such as "cut/edit that pause out"
- remove false starts that lead into a production note
- flag source-time jumps over roughly 0.55s where the previous text does not end a sentence and the next text starts with a connector/lowercase word
- flag tiny nonsemantic fragments under one second, while preserving meaningful reactions like "yeah", "no", "oh really?", and "wow"
- manually review flagged boundaries before rendering the accepted master

For user-reported timestamps, repair the edit plan and rerender from source. Do not patch the final MP4 with a destructive timeline splice unless source media is unavailable.

## Longform Rendering

For long episodes with hundreds of active-speaker edits, avoid renderers that create one video/audio/muxed file per edit unless there is abundant disk space. However, do not rely on `ffconcat` `inpoint`/`outpoint` directly against long-GOP camera originals unless a sync proof confirms it. Direct concat inpoints can pull pre-roll around keyframes, making separately cut studio audio drift or slip against the picture.

Preferred sync-safe workflow:

- build a JSON/CSV edit plan on the studio clock
- coalesce adjacent same-camera shots to reduce segment count
- render each coalesced shot as a real trimmed segment with camera video and matching studio-audio interval
- concatenate those normalized segments with stream copy
- run final loudness mastering in a final audio pass if needed

Use direct `ffconcat` inpoints only for intermediate proofs or media that is known to cut accurately at the requested timestamps.

Render a 2-10 minute proof first. Probe it, compare proof duration against edit-plan duration, run a scratch-audio versus rendered-audio lag check, inspect early/mid/late frames, and only then render the full master.

## Shortform Rhythm

For Shorts/Reels:

- Start with the strongest claim or emotional hook.
- Keep one idea per clip.
- Remove preamble.
- Favor close-up speaker energy.
- Use wide/Ty reaction only when it improves context or credibility.
- End on a complete thought or loopable line.

## Shortform Speaker-On-Screen Audit

Before final render, inspect each clip candidate and record:

- why the first line is a hook
- why the final line is complete or loopable
- which person is speaking at the hook, middle, and ending
- whether the visible angle matches the speaker
- whether a two-speaker stack is required for context
- whether any title, overlay, or subtitle hides mouth movement

Reject or revise clips where the best words are spoken while the wrong person is on camera, unless the listener reaction is editorially stronger and explicitly justified.
