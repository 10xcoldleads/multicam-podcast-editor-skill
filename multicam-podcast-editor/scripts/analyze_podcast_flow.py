import argparse
import json
import math
import re
import wave
from pathlib import Path


FILLER_PATTERNS = [
    r"\byou know\b",
    r"\blike\b",
    r"\bum\b",
    r"\buh\b",
    r"\bi mean\b",
    r"\bright\b",
    r"\bokay\b",
    r"\byeah\b",
]


def read_pcm_wav(path: Path):
    with wave.open(str(path), "rb") as wf:
        channels = wf.getnchannels()
        rate = wf.getframerate()
        width = wf.getsampwidth()
        frames = wf.readframes(wf.getnframes())
    if width == 2:
        import numpy as np

        data = np.frombuffer(frames, dtype="<i2").astype("float32") / 32768.0
    elif width == 3:
        import numpy as np

        b = np.frombuffer(frames, dtype="uint8").reshape(-1, 3)
        vals = b[:, 0].astype("int32") | (b[:, 1].astype("int32") << 8) | (b[:, 2].astype("int32") << 16)
        vals = (vals ^ 0x800000) - 0x800000
        data = vals.astype("float32") / 8388608.0
    elif width == 4:
        import numpy as np

        data = np.frombuffer(frames, dtype="<i4").astype("float32") / 2147483648.0
    else:
        raise ValueError(f"Unsupported sample width {width} for {path}")
    if channels > 1:
        data = data.reshape(-1, channels).mean(axis=1)
    return data, rate


def rms_db(data, rate, start, end):
    import numpy as np

    a = max(0, int(start * rate))
    b = min(len(data), int(end * rate))
    if b <= a:
        return -120.0
    chunk = data[a:b]
    rms = float(np.sqrt(np.mean(chunk * chunk) + 1e-12))
    return round(20 * math.log10(rms + 1e-12), 1)


def norm_text(text):
    return re.sub(r"\s+", " ", text or "").strip()


def filler_score(text):
    lower = f" {text.lower()} "
    return sum(len(re.findall(p, lower)) for p in FILLER_PATTERNS)


def classify_segment(seg, track_a, track_b, rate_a, rate_b, track_a_name, track_b_name, threshold_db):
    ra = rms_db(track_a, rate_a, seg["start"], seg["end"])
    rb = rms_db(track_b, rate_b, seg["start"], seg["end"])
    diff = rb - ra
    if diff >= threshold_db:
        speaker = track_b_name
    elif diff <= -threshold_db:
        speaker = track_a_name
    else:
        speaker = "mixed"
    return speaker, ra, rb, diff


def interruption_candidates(segments):
    out = []
    for i in range(1, len(segments) - 1):
        prev_seg = segments[i - 1]
        seg = segments[i]
        nxt = segments[i + 1]
        txt = norm_text(seg["text"])
        dur = seg["end"] - seg["start"]
        same_speaker_around = prev_seg["speaker"] == nxt["speaker"] and seg["speaker"] != prev_seg["speaker"]
        short_backchannel = dur <= 2.2 and re.fullmatch(
            r"(?i)(yeah|okay|right|interesting|mm+h?m?|for sure|exactly|wow|true|yep)[\s.!,?]*",
            txt or "",
        )
        overlapish = seg["speaker"] == "mixed" and dur <= 4.0
        high_filler = filler_score(txt) >= 3 and dur <= 8.0
        if same_speaker_around and (short_backchannel or dur <= 3.0):
            reason = "short backchannel interrupts same-speaker answer"
        elif overlapish:
            reason = "mixed/overlap-like short exchange"
        elif high_filler:
            reason = "filler-heavy small segment"
        else:
            continue
        out.append({
            "start": seg["start"],
            "end": seg["end"],
            "duration": round(dur, 2),
            "speaker": seg["speaker"],
            "reason": reason,
            "text": txt,
            "prev": norm_text(prev_seg["text"]),
            "next": norm_text(nxt["text"]),
        })
    return out


def intro_candidates(segments):
    keywords = ["welcome", "today", "with", "interesting", "person", "guest", "conversation", "show"]
    out = []
    for i in range(min(80, len(segments))):
        for j in range(i, min(i + 8, len(segments), 90)):
            start = segments[i]["start"]
            end = segments[j]["end"]
            if end - start < 8 or end - start > 60:
                continue
            text = norm_text(" ".join(s["text"] for s in segments[i : j + 1]))
            lower = text.lower()
            score = sum(1 for k in keywords if k in lower)
            if score >= 4:
                out.append({"start": start, "end": end, "duration": round(end - start, 2), "score": score, "text": text})
    out.sort(key=lambda x: (-x["score"], x["duration"]))
    return out[:10]


def main():
    parser = argparse.ArgumentParser(description="Classify active speaker and flag intro/interruption candidates.")
    parser.add_argument("--segments", type=Path, required=True, help="Whisper-style transcript segments JSON")
    parser.add_argument("--track-a", type=Path, required=True, help="First isolated speaker WAV")
    parser.add_argument("--track-b", type=Path, required=True, help="Second isolated speaker WAV")
    parser.add_argument("--track-a-name", default="track_a")
    parser.add_argument("--track-b-name", default="track_b")
    parser.add_argument("--threshold-db", type=float, default=5.0)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    segments = json.loads(args.segments.read_text(encoding="utf-8"))
    track_a, rate_a = read_pcm_wav(args.track_a)
    track_b, rate_b = read_pcm_wav(args.track_b)
    enriched = []
    for seg in segments:
        speaker, ra, rb, diff = classify_segment(
            seg,
            track_a,
            track_b,
            rate_a,
            rate_b,
            args.track_a_name,
            args.track_b_name,
            args.threshold_db,
        )
        item = dict(seg)
        item.update({
            "speaker": speaker,
            f"{args.track_a_name}_rms_db": ra,
            f"{args.track_b_name}_rms_db": rb,
            f"{args.track_b_name}_minus_{args.track_a_name}_db": round(diff, 1),
        })
        enriched.append(item)

    names = [args.track_a_name, args.track_b_name, "mixed"]
    result = {
        "speaker_counts": {k: sum(1 for s in enriched if s["speaker"] == k) for k in names},
        "intro_candidates": intro_candidates(enriched),
        "interruption_candidates": interruption_candidates(enriched),
        "segments": enriched,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ["speaker_counts"]}, indent=2))
    print(f"intro_candidates={len(result['intro_candidates'])}")
    print(f"interruption_candidates={len(result['interruption_candidates'])}")


if __name__ == "__main__":
    main()
