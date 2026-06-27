# Intake And Sync

## Intake

Use completed media only. Reject `.crdownload`, partial, zero-byte, or still-growing files.

Create a project structure like:

```text
raw_video/
raw_audio/
audio_master/
analysis/
analysis/video_probe/
analysis/camera_scratch_audio/
transcript/
renders/full_podcast/
renders/social_clips/
previews/
work/
```

Probe every source:

```powershell
ffprobe -v error -show_entries stream=index,codec_type,codec_name,width,height,r_frame_rate,duration,channels,sample_rate -show_entries format=duration,size,bit_rate -of json "path\to\source.mp4"
```

Record file size, duration, codec, resolution, fps, audio streams, sample rate, and role.

## Camera Roles

Identify roles with contact sheets and frame inspection:

- host close-up
- guest close-up
- wide/two-shot
- secondary/reaction angles

## Audio Authority

Prefer isolated speaker WAVs for final dialogue. Use camera scratch only for sync unless the camera audio is the only source.

Common roles:

- studio mix: transcript and sync reference
- host isolated mic: host RMS/speaker detection
- guest isolated mic: guest RMS/speaker detection
- dialogue bus: final mixed voice source

## Sync Method

Extract scratch audio:

```powershell
ffmpeg -hide_banner -y -i "raw_video\CAMERA.mp4" -vn -ac 1 -ar 16000 "analysis\camera_scratch_audio\CAMERA.scratch_mono16k.wav"
```

Estimate each camera's offset against the studio reference with envelope/cross-correlation, then verify at known speech windows.

Store offsets in a ledger with an explicit mapping convention. Do not rely on the sign label alone.

## Mapping Convention

Use studio audio / transcript time as the source timeline.

If a camera starts later than the studio reference by `offset`, use:

```text
camera_seek_time = studio_time - offset
```

Validate this with at least two windows:

- one host-speaking window
- one guest-speaking window

Compare plus-offset and minus-offset hypotheses. Reject the mapping that produces high residuals or obvious lip-sync failure.

## Sync Proof Standard

Treat offsets as untrusted until they survive both objective and visual checks.

For each camera:

- choose at least two studio-time windows with clear speech and visible mouth movement
- include one host/interviewer-speaking window and one guest-speaking window when roles exist
- render a short proof using `camera_seek_time = studio_time - offset`
- compare the rendered audio against the studio dialogue bus and the camera scratch waveform
- inspect mouth consonants, hand hits, laughs, and turn-taking visually

If audio feels late or early, do not hand-shift the final MP4. Recompute or correct the camera offset, rebuild the edit plan, and rerender from source.

Store in `SYNC_LEDGER.md`:

- source timeline convention
- each camera role and offset
- exact proof windows used
- objective lag/residual result when measured
- human lip-sync notes
- final accepted mapping formula

## Sync Preview

Create a multicam grid proof around a known high-value exchange:

```powershell
ffmpeg -hide_banner -y `
  -ss <host_camera_seek> -t 60 -i "raw_video\HOST.mp4" `
  -ss <guest_camera_seek> -t 60 -i "raw_video\GUEST.mp4" `
  -ss <wide_camera_seek> -t 60 -i "raw_video\WIDE.mp4" `
  -ss <studio_start> -t 60 -i "audio_master\dialogue_bus_longform.wav" `
  -filter_complex "[0:v]scale=640:360,setpts=PTS-STARTPTS[host];[1:v]scale=640:360,setpts=PTS-STARTPTS[guest];[2:v]scale=640:360,setpts=PTS-STARTPTS[wide];[host][guest][wide]hstack=inputs=3[v]" `
  -map "[v]" -map 3:a -c:v libx264 -crf 20 -preset veryfast -r 25 -c:a aac -b:a 192k -shortest "previews\sync_preview_syncfixed.mp4"
```

Run black/freeze QC and inspect frames. Human listening review is still required for final lip-sync taste.
