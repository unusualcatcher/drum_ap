# Drum Transcriber

A Django web application that transcribes drum beats from audio files and generates
sheet music images. Upload an MP3 or WAV file and the application detects kick drums,
snare hits, and hi-hat patterns using librosa, then renders the result as printable
sheet music.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Windows Setup](#windows-setup)
- [macOS Setup](#macos-setup)
- [Linux Setup](#linux-setup)
- [Python Dependencies](#python-dependencies)
- [Running the Server](#running-the-server)
- [Project Structure](#project-structure)
- [Common Errors and Fixes](#common-errors-and-fixes)


---

## Prerequisites

Before installing Python dependencies, three external tools must be installed on your
machine. The exact installation method depends on your operating system.

### Required External Tools

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.10.x | Runtime. Version 3.10 specifically is required for madmom compatibility. |
| FFmpeg | Any recent | Required by librosa to decode MP3 and other compressed audio formats. |
| MuseScore | 4.x | Converts MusicXML files to PNG sheet music images. |

---

## Getting the Project

### Option A — Clone with Git

```
git clone https://github.com/yourusername/drum_ap.git
cd drum_ap
```

### Option B — Download as ZIP

1. Go to the repository page on GitHub.
2. Click the green "Code" button and select "Download ZIP".
3. Extract the ZIP to a folder of your choice.
4. Open a terminal and navigate into the extracted folder:

```
cd path/to/drum_ap
```

You should now be in the same directory as `manage.py`. All subsequent commands must
be run from this location.

---

## Windows Setup

### Step 1 — Install Python 3.10

Open PowerShell or Command Prompt and run:

```
winget install --id Python.Python.3.10 -e --accept-source-agreements --accept-package-agreements
```

Close and reopen your terminal after installation so that the `py` launcher picks up
the new version. Verify with:

```
py -3.10 --version
```

### Step 2 — Install FFmpeg

```
winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements
```

After installation, verify FFmpeg is on your PATH:

```
ffmpeg -version
```

If the command is not found, add `C:\ProgramData\chocolatey\bin` or the FFmpeg `bin`
folder to your system PATH manually via System Properties > Environment Variables.

### Step 3 — Install MuseScore 4

```
winget install --id MuseScore.MuseScore4 -e --accept-source-agreements --accept-package-agreements
```

MuseScore installs to `C:\Program Files\MuseScore 4\bin\MuseScore4.exe` by default.
The `sheet_generator.py` file references this path directly. If your installation path
differs, update the `us['musescoreDirectPNGPath']` line accordingly.

### Step 4 — Create and Activate a Virtual Environment

From the same directory as `manage.py`, run:

```
py -3.10 -m venv venv_audio
venv_audio\Scripts\activate
```

If you are using Git Bash instead of Command Prompt, the activation command is:

```
source venv_audio/Scripts/activate
```

---

## macOS Setup

### Step 1 — Install Python 3.10

Using Homebrew:

```
brew install python@3.10
```

Or download the macOS installer directly from https://www.python.org/downloads/release/python-31011/

Verify:

```
python3.10 --version
```

### Step 2 — Install FFmpeg

```
brew install ffmpeg
```

### Step 3 — Install MuseScore 4

Download the DMG from https://musescore.org/en/download and install to `/Applications`.

Then update `sheet_generator.py` to point to the correct binary:

```python
us['musescoreDirectPNGPath'] = '/Applications/MuseScore 4.app/Contents/MacOS/mscore'
```

### Step 4 — Create and Activate a Virtual Environment

From the same directory as `manage.py`, run:

```
python3.10 -m venv venv_audio
source venv_audio/bin/activate
```

---

## Linux Setup

### Step 1 — Install Python 3.10

On Ubuntu 22.04 or Debian:

```
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev build-essential -y
```

On Fedora / RHEL:

```
sudo dnf install python3.10 python3.10-devel gcc gcc-c++ make -y
```

### Step 2 — Install FFmpeg

Ubuntu / Debian:

```
sudo apt install ffmpeg -y
```

Fedora:

```
sudo dnf install ffmpeg -y
```

### Step 3 — Install MuseScore 4

Using Flatpak (recommended for most distros):

```
flatpak install flathub org.musescore.MuseScore
```

Then update `sheet_generator.py`:

```python
us['musescoreDirectPNGPath'] = '/usr/bin/mscore'
# or for Flatpak:
# us['musescoreDirectPNGPath'] = 'flatpak run org.musescore.MuseScore'
```

### Step 4 — Create and Activate a Virtual Environment

From the same directory as `manage.py`, run:

```
python3.10 -m venv venv_audio
source venv_audio/bin/activate
```

---

## Python Dependencies

This is the exact installation sequence. The order matters. Installing packages out of
order will cause build failures, particularly with madmom and its Cython extensions.

### Step 1 — Upgrade pip, setuptools, and wheel

```
python -m pip install --upgrade pip setuptools wheel
```

### Step 2 — Install NumPy and Cython before anything else

madmom requires NumPy headers and Cython to be present in the build environment before
its C extensions are compiled. Install these first:

```
pip install "numpy<2.0.0" "Cython<3.0"
```

NumPy 2.x removed internal C struct members that madmom's compiled extensions depend on.
Cython 3.x introduced breaking changes to the code generation that madmom 0.16.1 is not
compatible with. Both version pins are required.

### Step 3 — Install PyYAML with --no-build-isolation

PyYAML 5.4.1 requires Cython at build time. Without `--no-build-isolation`, pip creates
an isolated build environment where Cython is not available, causing the build to fail.

```
pip install pyyaml==5.4.1 --no-build-isolation
```

### Step 4 — Install madmom with --no-build-isolation

Same reasoning as PyYAML — madmom must see the already-installed Cython and NumPy in the
active environment during its build:

```
pip install madmom==0.16.1 --no-build-isolation
```

### Step 5 — Install all remaining dependencies

```
pip install django librosa soundfile pretty_midi music21
```

### Complete Install Sequence (copy-paste version)

```
python -m pip install --upgrade pip setuptools wheel
pip install "numpy<2.0.0" "Cython<3.0"
pip install pyyaml==5.4.1 --no-build-isolation
pip install madmom==0.16.1 --no-build-isolation
pip install django librosa soundfile pretty_midi music21
```

## Running the Server

With the virtual environment activated, from the same directory as `manage.py`, run:

```
python manage.py runserver
```

Open http://127.0.0.1:8000 in your browser. Upload an audio file using the form. The
server will process the file, generate sheet music, and display the PNG pages inline.

To apply the built-in Django migrations (not required for core functionality but removes
the warning on startup):

```
python manage.py migrate
```

---

## Project Structure

```
drum_ap/
    drum_ap/
        settings.py
        urls.py
        wsgi.py
    transcriber/
        drum_engine.py     
        sheet_generator.py  
        views.py           
        urls.py             
        templates/
            index.html    
    media/
        uploads/           
        sheets/           
    manage.py
```
