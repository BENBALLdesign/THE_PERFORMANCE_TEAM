---
name: recording-notes
description: Run the local Python exporter for screen recordings to produce timestamped screen text, reference candidates, and reviewable class-note evidence.
---
# Recording notes

Run the script beside this file. The script uses local FFmpeg and Tesseract; audible tracks use the sibling audio-notes script. It makes no API calls or model downloads. Keep source files unchanged and choose an explicit output folder.

```powershell
python -B scripts/export_recordings.py "path/to/recording.mp4" "path/to/another.mp4" --output "path/to/new-export"
```

- Default: one frame each second plus intervening scene changes. `--interval 0` reads every frame; use it for very brief text. `--workers 4` limits parallel OCR work. Exact timestamp and frame links remain in the output.
- Audio is measured first. Silent tracks produce an explicit silence record, not guessed speech. `--device auto|cpu|cuda` controls audible transcription; CPU fallback is recorded.
- Follow `progress.json` or the command output. Repeating the same command resumes completed work. Use a new output folder after changing settings or scripts. If interrupted, check the PID in `.export.lock` before removing only that stale lock.
- Open `index.html` for searchable evidence. `reference-candidates.csv` is a machine candidate list, not a verified table of rules. Raw word boxes/confidence are in each source's `ocr` folder. A selected quiz option is not proof of the correct answer.
- To export a reviewed condensation, supply a notes JSON file to `scripts/publish_notes.py --export "path/to/export" --notes "path/to/notes.json"`. Run `--help` for the schema. This validates evidence links and produces a compact study guide, number table and decision-tree view; it does not generate interpretations or call an LLM.

Dependencies: Python 3.11+, Pillow, FFmpeg/ffprobe, Tesseract with the requested language. `--help` lists the path overrides. For audible media, retain the sibling audio-notes folder and its local dependencies.