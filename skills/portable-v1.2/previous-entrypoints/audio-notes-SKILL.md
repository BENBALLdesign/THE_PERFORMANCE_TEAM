---
name: audio-notes
description: Run the local Python audio exporter with cached speech models, checked GPU selection, resumable chunks, and timestamped transcript files.
---
# Audio notes

```powershell
python -B scripts/export_audio.py --check-device
python -B scripts/export_audio.py "path/to/audio.m4a" --output "path/to/new-export" --model "path/to/cached-model.pt" --device auto
```

This script reads the source without changing it. It uses local FFmpeg and Whisper only; it never uploads audio, calls an API or downloads a model.

- `--device auto` verifies CUDA computation and free memory, then uses GPU or reports CPU fallback. `--device cuda` requires GPU; `--device cpu` forces CPU. CuPy support in a different application does not establish PyTorch GPU support.
- Default: five-minute chunks with two-second context on both sides. Word timestamps assign overlap to its original time interval. Unidentified speakers stay unidentified. Conflicting boundary words still require review.
- `--threads 4` limits CPU threads; `--gpu-reserve-gb 3` is the minimum free GPU memory before starting, not a hard allocation limit. Automatic mode retries on CPU if CUDA runs out of memory.
- `progress.json` records the current chunk and device. Create a file named `STOP` inside the output folder to stop after the current chunk. Remove that marker and rerun the same command to resume. Do not change source/model/settings in an existing export.
- Open `transcript.md`; use `transcript.json` for word timing, uncertainty scores, device record and provenance, or `transcript.srt` for captions. Raw chunk results are retained. Silence produces an explicit record without invented speech.
- If a crashed run leaves `.export.lock`, check its recorded PID before removing only that stale lock. Sources and prior outputs are never cleanup targets.

Dependencies: Python 3.11+, FFmpeg/ffprobe, openai-whisper, PyTorch and an already-downloaded local checkpoint. GPU needs a CUDA-enabled PyTorch runtime; the script does not install or replace packages.