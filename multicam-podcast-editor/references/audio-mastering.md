# Audio Mastering

## Source Priority

Prefer isolated speaker tracks for final dialogue. Use the studio mix as a reference, not necessarily as the final bus.

Build a dialogue bus:

- balance isolated speaker levels
- compress gently
- de-ess if needed
- remove obvious noise only if it does not damage speech
- keep room tone natural

## Audio/Video Match Rules

Use one master audio clock for every deliverable. Prefer the final dialogue bus or studio mix, not camera scratch audio.

For longform:

- render picture from selected camera angles on the studio timeline
- map every selected visual segment with `camera_seek_time = studio_time - camera_offset`
- use the matching studio-audio interval for that same source time
- reject workflows where video is cut from camera time but audio is cut from a different unverified timeline

For shorts:

- cut base clips from the same studio start/end as the transcript window
- seek each camera with the verified camera offset
- mux HyperFrames video-only output back to the locked base clip audio
- check the final MP4 after AAC encode, because filters and muxing can change duration/peak behavior

Do not repair sync by nudging only the final MP4 unless source media is unavailable. Correct the offset/edit plan and rerender.

## Targets

Longform podcast/video:

- integrated loudness around -16 LUFS
- true peak below -1.5 dBFS/dBTP
- stereo AAC 48 kHz for review/delivery unless platform requires otherwise

Short-form social:

- integrated loudness around -14 LUFS
- true peak below -1.5 dBFS/dBTP
- voice clearly ahead of music/SFX

## Loudness QC

Measure the encoded output:

```powershell
ffmpeg -hide_banner -nostats -i "render.mp4" -filter_complex ebur128=peak=true -f null - 2>&1
```

Use the final `Integrated loudness` and `True peak` summary.

## True-Peak Failure

Do not approve a render just because integrated LUFS is right. AAC encoding can create true-peak overs.

If a raw gain pass overshoots, reject it and render from the clean source with loudnorm:

```powershell
ffmpeg -hide_banner -y -i "source.mp4" -map 0:v -map 0:a -c:v copy `
  -af "loudnorm=I=-16:TP=-2.0:LRA=7" `
  -c:a aac -b:a 192k -ar 48000 -ac 2 "delivery_loudnorm.mp4"
```

For short-form:

```powershell
loudnorm=I=-14:TP=-1.5:LRA=8
```

## Music And SFX

For real podcast edits, music/SFX are optional and usually belong in:

- intro/outro
- chapter/title moments
- social clip hooks
- quote-card transitions

Duck music/SFX under speech. Voice should remain intelligible at low playback volume.
