import os
import shutil
from django.shortcuts import render
from django.conf import settings
from .drum_engine import transcribe_drums, events_to_grid
from .sheet_generator import events_to_sheet

def index(request):
    context = {}
    sheet_dir = os.path.join(settings.MEDIA_ROOT, "sheets")

    if request.method == "GET":
        if os.path.exists(sheet_dir):
            shutil.rmtree(sheet_dir)
        os.makedirs(sheet_dir, exist_ok=True)

    if request.method == "POST" and request.FILES.get("audio_file"):
        audio_file = request.FILES["audio_file"]
        upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        file_path  = os.path.join(upload_dir, audio_file.name)

        with open(file_path, "wb") as f:
            for chunk in audio_file.chunks():
                f.write(chunk)

        try:
            events = transcribe_drums(file_path)
            grid   = events_to_grid(events)
            bpm    = grid.get("bpm", 120)

            os.makedirs(sheet_dir, exist_ok=True)
            sheet_name = os.path.splitext(audio_file.name)[0] + "_sheet.xml"
            sheet_path = os.path.join(sheet_dir, sheet_name)

            xml_path, png_paths = events_to_sheet(
                events,
                bpm=bpm,
                title=os.path.splitext(audio_file.name)[0],
                output_path=sheet_path
            )

            context["events"]   = events
            context["grid"]     = grid
            context["filename"] = audio_file.name
            context["success"]  = True

            if xml_path:
                context["sheet_url"] = settings.MEDIA_URL + "sheets/" + os.path.basename(xml_path)

            if png_paths:
                context["sheet_image_urls"] = [
                    settings.MEDIA_URL + "sheets/" + os.path.basename(p)
                    for p in png_paths
                ]

        except Exception as e:
            context["error"] = str(e)
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    return render(request, "index.html", context)