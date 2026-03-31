import librosa # library used to load model pickle files from root dirtectory and audio 
import numpy as np
from scipy.signal import butter, sosfilt

def _bandpass(y, sr, low, high):
    sos = butter(4, [low, min(high, sr / 2 - 1)], btype='band', fs=sr, output='sos')
    return sosfilt(sos, y)

def transcribe_drums(audio_path):
    y, sr = librosa.load(audio_path, sr=44100)
    _, y_perc = librosa.effects.hpss(y, margin=4.0)

    y_kick  = _bandpass(y_perc, sr, 40,   150)
    y_snare = _bandpass(y_perc, sr, 150,  8000)
    y_hihat = _bandpass(y_perc, sr, 5000, 20000)

    n_fft      = 2048
    hop_length = 512
    S          = np.abs(librosa.stft(y_perc, n_fft=n_fft, hop_length=hop_length))
    freqs      = librosa.fft_frequencies(sr=sr, n_fft=n_fft)

    onset_frames = librosa.onset.onset_detect(
        y=y_perc, sr=sr,
        units='frames',
        backtrack=True,
        wait=4,
        pre_avg=6, post_avg=6,
        pre_max=6, post_max=6
    )
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)

    kick_mask  = (freqs >= 40)   & (freqs <= 150)
    snare_mask = (freqs >= 150)  & (freqs <= 600)
    rattle_mask= (freqs >= 2000) & (freqs <= 8000)
    hihat_mask = (freqs >= 5000) & (freqs <= 20000)

    events = []
    for frame, time in zip(onset_frames, onset_times):
        start  = max(0, frame - 1)
        end    = min(S.shape[1], frame + 8)
        window = S[:, start:end]

        if window.shape[1] == 0:
            continue

        spec   = window.mean(axis=1)
        total  = spec.sum() + 1e-9

        centroid = np.sum(freqs * spec) / total
        kick_e   = spec[kick_mask].sum()   / total
        snare_e  = (spec[snare_mask].sum() + spec[rattle_mask].sum() * 0.6) / total
        hihat_e  = spec[hihat_mask].sum()  / total

        if centroid < 400 and kick_e > 0.28:
            drum_type = "kick"
        elif centroid > 6000 or hihat_e > 0.50:
            drum_type = "hi-hat"
        elif snare_e > 0.22 or (centroid > 400 and centroid < 4000):
            drum_type = "snare"
        else:
            drum_type = "other"

        events.append({"time": round(float(time), 3), "type": drum_type})

    return events


def events_to_grid(events, bpm=None, total_duration=None):
    if not events:
        return []

    if total_duration is None:
        total_duration = events[-1]["time"] + 0.5

    if bpm is None:
        impulse = np.zeros(int(44100 * total_duration))
        for e in events:
            idx = int(e["time"] * 44100)
            if idx < len(impulse):
                impulse[idx] = 1.0
        detected_bpm, _ = librosa.beat.beat_track(y=impulse, sr=44100)
        bpm = int(round(float(detected_bpm)))
        if bpm < 60 or bpm > 240:
            bpm = 120

    sixteenth = 60.0 / bpm / 4
    num_steps = int(total_duration / sixteenth) + 1

    grid = {
        "bpm":  bpm,
        "steps": num_steps,
        "sixteenth_duration": round(sixteenth, 4),
        "rows": {
            "kick":   [False] * num_steps,
            "snare":  [False] * num_steps,
            "hi-hat": [False] * num_steps,
            "other":  [False] * num_steps,
        }
    }

    for event in events:
        step = int(round(event["time"] / sixteenth))
        if step < num_steps and event["type"] in grid["rows"]:
            grid["rows"][event["type"]][step] = True

    return grid