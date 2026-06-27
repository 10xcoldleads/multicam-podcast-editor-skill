# Social Clips, HyperFrames, And Optional Remotion

## Renderer Selection

Keep the editorial pipeline separate from the graphics renderer.

- Use FFmpeg for source sync, camera crops, base social clips, audio muxing, fast drafts, and objective QC.
- Use HyperFrames when the user wants deterministic animated captions, title overlays, quote cards, lower thirds, branded social packaging, and inspectable layout validation.
- Use Remotion only when a reusable React component/template system is valuable: client-specific branded layouts, programmatic variants, reusable subtitle components, progress bars, speaker labels, and batch rendering from JSON.

Do not use Remotion, HyperFrames, or any graphics renderer to decide the edit. The edit still comes from transcript timing, camera offsets, active-speaker logic, and QC.

Remotion can improve packaging quality and reusability, but it does not automatically solve:

- audio/video sync
- active speaker detection
- clip selection
- transcript boundary repair
- loudness/true-peak mastering
- speaker-on-screen verification

If using Remotion, feed it locked base clips and JSON metadata rather than raw camera files whenever possible. Mux or export with the same locked audio used in the FFmpeg/HyperFrames workflow, then run the same final QC gates.

## Is HyperFrames Required?

No for the core multicam edit.

Yes or strongly preferred when the deliverable needs deterministic:

- embedded captions
- quote cards
- lower thirds
- kinetic title cards
- chapter cards
- branded overlays
- motion graphics
- polished social packaging

FFmpeg/ASS subtitles are sufficient for simple burned captions. HyperFrames is better when text hierarchy, animation, layout, and brand consistency matter.

## Clip Selection

Score transcript windows for:

- hook strength
- emotional turn
- tactical value
- novelty
- clear beginning/end
- speaker conviction
- visual energy

Then validate visually.

For each selected clip, record:

- beginning: why the first 1-3 seconds create a hook
- ending: why the final line is complete, satisfying, or loopable
- value: what the viewer gains from the clip
- context: what was removed and why the clip still makes sense
- speaker coverage: who is speaking at hook/middle/end and whether the screen shows the right person
- format choice: active-speaker full frame, wide/two-shot, or two-speaker stack

## Caption Style

Use two tiers:

- rail captions for spoken words
- large cinematic text only for peak phrases

Do not put every word in large text. Large text should tell a parallel story or emphasize the emotional/strategic turn.

## Word-Cued Caption Timing

Use word-level transcript timestamps when available.

Recommended social caption grouping:

- group 2-4 spoken words per caption
- start each caption slightly before the first word, around 20-50 ms
- end each caption shortly after the last word, around 75-125 ms
- split groups at pauses, speaker turns, strong nouns, numbers, and emphasis words
- prevent overlapping caption DOM/timeline intervals before rendering
- animate captions quickly enough to feel responsive, but never so much that they lag the spoken word

When highlighting hot terms, build line breaks before injecting HTML spans. Do not split already-rendered markup because it can create nested/broken spans and false overlap warnings.

## FFmpeg Caption QC

If using ASS captions:

- inspect the generated `.ass`
- check currency symbols and `$` values
- extract hook frames
- verify text does not cover faces or important gestures
- keep button-safe/social-safe margins

PowerShell warning: pass hook strings containing `$` in single quotes or escape `$`.

## Vertical Cropping

For 4K 16:9 source to 9:16:

- crop around the active speaker's face, mic, and upper torso
- preserve hand movement when it adds energy
- avoid cutting off the chin/top of head
- inspect frames at the hook and mid-clip

For 1080p horizontal podcast cameras:

- avoid rendering a small horizontal strip inside a vertical black canvas
- crop each close-up from the original camera file before scaling
- use a high-quality scaler such as Lanczos for derived base clips
- use a visually transparent encode for base clips, such as H.264 CRF 16-18, before a HyperFrames graphics pass
- keep the final handoff MP4 separate from base clips and HyperFrames work folders

For two-speaker vertical stacks:

- crop each 16:9 camera to a portrait-safe speaker panel
- scale each panel to half-height, then stack top/bottom
- place interviewer/host top and guest bottom unless project context says otherwise
- keep a divider or caption rail between panels
- verify both faces, microphones, and key gestures remain visible

## HyperFrames Use Pattern

Use the existing HyperFrames skills for:

- `embedded-captions`: polished captions
- `graphic-overlays`: quote cards and lower thirds
- `motion-graphics`: title cards and kinetic emphasis
- `hyperframes-core` / `hyperframes-cli`: composition, validation, rendering
- `hyperframes-media`: media preprocessing and transcript/caption work

Render editorial picture first, then add HyperFrames graphics once the cut works.

## Remotion Use Pattern

Use Remotion only after the clip slate and base media are locked.

Recommended Remotion data contract:

- `clip_id`
- `base_video_path`
- `audio_path` or `use_base_audio`
- `duration`
- `speaker_layout`
- `captions` with word/phrase start/end times
- `title`
- `hook`
- `speaker_labels`
- `accent_terms`
- `safe_zones`

Remotion output must still pass the same checks as HyperFrames output:

- expected resolution/fps/codecs
- audio loudness and true peak
- no unexpected black/freeze events
- no caption/overlay face or mouth obstruction
- active speaker or justified split-screen visible
- clean final MP4 copied into the delivery folder

## Fast Iteration Rule

Do not use full HyperFrames final renders as the first iteration loop for a large batch of podcast shorts. HyperFrames screenshot-rendering is deterministic and polished, but it is slower than FFmpeg for basic crop/caption checks.

Recommended loop:

1. Build a clip slate from transcript windows with repaired boundaries.
2. Render fast FFmpeg draft clips with basic crop and burned timing captions.
3. QC draft crops, speaker-on-camera, caption timing, and hook/end context.
4. Lock the clip slate and crop metadata.
5. Generate HyperFrames projects only for the approved final clips.
6. Run `npx hyperframes lint` and `npx hyperframes inspect --samples 15` before final render.
7. Render finals with HyperFrames and mux the locked audio.

This prevents wasting long HyperFrames renders on clips that still have bad crop, weak context, or oversized text.

## HyperFrames Finalization Rules

Before calling a HyperFrames social batch final:

- lint every project and require 0 errors / 0 warnings
- inspect every project with sampled timeline frames and require 0 layout issues, or document intentional overlap with `data-layout-allow-overlap`
- mux final HyperFrames video with the locked audio from the base clip or dialogue bus
- delete `.video_only.mp4` and leftover `work-*` render folders after successful mux/QC
- regenerate contact sheets from the final MP4s, not stale drafts

## Face-Safe Overlay QC

HyperFrames `lint` and `inspect` catch composition and layout problems, but they do not know where a speaker's eyes or mouth are. Always extract early/mid/late frames from final renders and visually verify:

- kinetic hero words do not cover eyes or mouth
- subtitles do not hide the speaker's mouth during important delivery
- top hooks stay inside social safe margins
- lower-third caption blocks leave enough gesture/mic context

If a hero emphasis layer crosses the face, move it to the torso band or above the headroom and re-render the batch before accepting finals.

## Social Batch QC Loop

Run a three-pass QC loop:

1. Automated media QC: ffprobe, loudness, true peak, blackdetect, freezedetect, expected duration, expected 1080x1920/30fps.
2. HyperFrames QC: `npx hyperframes lint public` and `npx hyperframes inspect public --samples 15` for every project.
3. Visual editorial QC: contact sheet and spot playback for speaker visibility, caption timing, title safe margins, face/mouth occlusion, sharpness, and whether the clip has a complete idea.

Only copy accepted MP4s into a clean final delivery folder after all three passes.

## Tooling To Consider

Use these as building blocks, not as blind auto-edit replacements:

- Auto-Editor (`wyattblue/auto-editor`) for silence-detection reports and rough dead-air candidates.
- WhisperX (`m-bain/whisperX`) for stronger word-level alignment/diarization when local CPU time or GPU access allows it.
- OpenTimelineIO (`AcademySoftwareFoundation/OpenTimelineIO`) for portable edit decision data if exporting to/from NLEs or building a client-facing review pipeline.

Any imported tool must preserve the studio-audio master clock and must not make final cuts without transcript/context validation.
