import glob
import os
from music21 import stream, note, meter, tempo, clef, duration, metadata, chord, environment

us = environment.UserSettings()
us['musescoreDirectPNGPath'] = r'C:\Program Files\MuseScore 4\bin\MuseScore4.exe'
us['directoryScratch'] = os.environ.get('TEMP', 'C:\\Temp')

DRUM_PITCH_MAP = {
    "kick":   ("C4",  "normal", "down"),
    "snare":  ("A4",  "normal", "up"),
    "hi-hat": ("G5",  "x",      "up"),
    "other":  ("E5",  "normal", "up"),
}

def events_to_sheet(events, bpm=120, title="Drum Transcription", output_path="sheet.xml"):
    score = stream.Score()
    
    score.metadata = metadata.Metadata()
    score.metadata.title = ""
    score.metadata.composer = ""
    score.metadata.movementName = ""

    part = stream.Part()
    part.insert(0, clef.PercussionClef())
    part.insert(0, tempo.MetronomeMark(number=bpm))
    part.insert(0, meter.TimeSignature("4/4"))

    if not events:
        return None, []

    beat_duration  = 60.0 / bpm
    sixteenth_dur  = beat_duration / 4
    last_time      = events[-1]["time"] + beat_duration
    total_steps    = int(last_time / sixteenth_dur) + 1
    steps_per_bar  = 16
    num_bars       = (total_steps // steps_per_bar) + 1

    grid = {}
    for event in events:
        step = int(round(event["time"] / sixteenth_dur))
        bar  = step // steps_per_bar
        beat = step %  steps_per_bar
        grid.setdefault(bar, {}).setdefault(beat, []).append(event["type"])

    for bar_idx in range(num_bars):
        measure = stream.Measure(number=bar_idx + 1)
        for step in range(steps_per_bar):
            hits = grid.get(bar_idx, {}).get(step, [])
            if hits:
                if len(hits) == 1:
                    drum         = hits[0]
                    p_str, head, _ = DRUM_PITCH_MAP.get(drum, ("D2", "normal", "above"))
                    n            = note.Note(p_str)
                    n.duration   = duration.Duration("16th")
                    n.notehead   = head
                    n.stemDirection = "down" if drum == "kick" else "up"
                    measure.append(n)
                else:
                    pitches = [DRUM_PITCH_MAP.get(d, ("D2", "normal", "above"))[0] for d in hits]
                    c          = chord.Chord(pitches)
                    c.duration = duration.Duration("16th")
                    measure.append(c)
            else:
                r          = note.Rest()
                r.duration = duration.Duration("16th")
                measure.append(r)
        part.append(measure)

    score.append(part)

    xml_path = output_path.replace(".xml", ".musicxml")
    score.write("musicxml", fp=xml_path)

    png_base_path = output_path.replace(".xml", ".png")
    png_paths     = []
    try:
        score.write("musicxml.png", fp=png_base_path)
        search_pattern = output_path.replace(".xml", "*.png")
        png_paths      = sorted(glob.glob(search_pattern))
    except Exception:
        pass

    return xml_path, png_paths