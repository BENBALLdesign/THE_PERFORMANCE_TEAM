# Portable local recording processing

Keep this entire `skills` directory together. Both exporters locate `local_runtime.py` from their own script location, independently of the current working directory. No user name, drive letter, or machine-specific installation directory is required in the scripts.

Requires Python 3.11+, FFmpeg/ffprobe, and local Python dependencies listed in `requirements.txt`. Screen OCR also requires Tesseract and its language data. Speech requires an already downloaded Whisper checkpoint. The scripts do not install packages, download models, upload recordings, or call external APIs.

## Configure once per installation

Copy `local-settings.example.json` to `local-settings.json` beside this README. Relative paths in that file are relative to the settings file, even when launched from another directory. Put binaries in `tools`, checkpoints in `models`, or point the settings at existing local installations. Optional keys: `tool_dirs`, `model_dirs`, `python_packages`, `model`, `profile`, `memory_reserve_gb`, and `tools` (an object with `ffmpeg`, `ffprobe`, and/or `tesseract` paths).

For example:

```json
{
  "profile": "auto",
  "tool_dirs": ["tools"],
  "model_dirs": ["models"],
  "memory_reserve_gb": 1.5
}
```

Python packages must be compatible with the selected Python version, operating system and CPU architecture. Copying a Windows package installation to another operating system does not make it compatible.

## Run from any working directory

Use the absolute path to the script (substitute your own installation location). Source and output paths supplied on the command line resolve from the current working directory; absolute paths are simplest. Configuration-file paths resolve from that configuration file.

```powershell
python -B "D:/recordings/skills/recording-notes/scripts/export_recordings.py" --check-runtime
python -B "D:/recordings/skills/recording-notes/scripts/export_recordings.py" "D:/recordings/class.mp4" --output "D:/exports/class-v1"
python -B "D:/recordings/skills/audio-notes/scripts/export_audio.py" "D:/recordings/class.m4a" --output "D:/exports/audio-v1"
```

The same Python command syntax works on other supported systems with their local paths. `--config PATH` selects another settings file. Command-line options override settings. `--tool-dir DIR` and `--model-dir DIR` may be repeated. Explicit `--ffmpeg`, `--ffprobe`, `--tesseract` and `--model PATH_OR_CACHED_NAME` take precedence. `--python-packages DIR` supports an existing local package directory without relying on the launch directory. Normal PATH installations and the user's Whisper cache are also searched.

## Resource options

- `--profile auto` (default) selects low-memory settings on machines with under 12 GiB total RAM, under 4 GiB available, or unknown total RAM. Other machines use balanced settings.
- `low-memory`: up to two OCR workers and two speech threads; prefers cached `base.en`, then `tiny.en`, then `small.en` if the estimate allows it.
- `balanced`: up to three OCR workers and three speech threads; prefers cached `small.en`, then `base.en`, then `tiny.en`.
- `throughput`: up to four OCR workers and four speech threads; same model preference as balanced.
- `--workers`, `--speech-threads` (recordings) or `--threads` (audio) override preset counts. Each invocation processes sources and speech jobs serially. Separate invocations can still compete for resources; avoid launching multiple speech exports on a low-memory machine.
- `--memory-reserve-gb 1.5` controls automatic checkpoint selection using approximate model memory needs. These are selection estimates, not enforced allocation limits or speed guarantees. Explicit model choices are honored; missing explicit models cause an error, never an unannounced substitute or download.
- `--device auto|cpu|cuda` retains checked CUDA selection and recorded CPU fallback. A smaller model can miss technical vocabulary; verify terms, numbers and units against the source.

`--check-runtime` reports resolved tools, model choice, memory, dependencies and resource counts without processing. It does not load or validate a checkpoint or prove GPU compatibility. Use the audio exporter's `--check-device` for its computation check. Each real export saves `runtime.json` for reproducibility.

Use a new output directory after changing scripts, model, or extraction settings. To resume an interrupted run, keep the same command and review the recorded PID before removing a stale `.export.lock`. Never remove an active lock. Keep original recordings unchanged. Exact timestamps and machine evidence remain separate from reviewed interpretations. A selected quiz answer is not proof that it is correct.

Validation: `python -B tests/test_runtime.py` checks portable path resolution, command-line precedence, missing-model behavior, and memory-based selection without downloading models.

## GPU speech and concurrent CPU visuals — September 19, 2026

The speech exporter produces timestamped Markdown, JSON and SRT audio transcripts. It does not extract images or recognize screen text. The recording exporter handles timestamped frames, Tesseract OCR, searchable evidence and reference candidates.

On the current Windows computer, an NVIDIA RTX 3060 with 12 GiB VRAM was available, but the original PyTorch 2.12.0 installation was CPU-only. A separate environment at `C:\Users\benja\.cache\performance-transcription-gpu` now contains `torch 2.12.0+cu126`; the exporter’s CUDA calculation check passed. It shares other installed Python packages through `--system-site-packages`, so it is not a fully self-contained environment. The original CPU installation was preserved. The existing cached `small.en.pt` checkpoint is reused.

Setup performed (historical record, not required on every run):

```powershell
& 'C:\Users\benja\AppData\Local\Python\pythoncore-3.14-64\python.exe' -m venv --system-site-packages 'C:\Users\benja\.cache\performance-transcription-gpu'
& 'C:\Users\benja\.cache\performance-transcription-gpu\Scripts\python.exe' -m pip install 'torch==2.12.0' --index-url https://download.pytorch.org/whl/cu126 --upgrade --no-cache-dir
```

Package setup required a download from the official PyTorch repository. Transcription itself remains local, with no recording uploads or automatic model downloads. See [PyTorch installation guidance](https://docs.pytorch.org/get-started/locally/) when setting up a different machine; select a build compatible with that machine rather than assuming these historical versions apply everywhere.

Run `--check-runtime` and `--check-device` as **separate invocations**: when both are supplied, the runtime report returns first and no device calculation occurs. `--device cuda` requires a working GPU and fails rather than silently selecting CPU. `--device auto` allows recorded CPU fallback. `runtime.json`, `device.json` and chunk records document what was actually used.

To process visuals alongside a separate GPU speech job, invoke the recording exporter with:

```powershell
python -B "D:/recordings/skills/portable-v1.2/recording-notes/scripts/export_recordings.py" "D:/recordings/class.mp4" --output "D:/exports/visuals-v1" --skip-speech --device cpu --workers 2
```

Use separate audio and visual output folders. `--skip-speech` suppresses Whisper transcription; it still measures full-track audio levels and may label an audible track `needs_transcription`. That label describes this visual export, not the status of a separate audio batch. This command does not import or merge the separate transcripts. Match evidence by source SHA-256 and timestamps during review.

Frame extraction uses software FFmpeg decoding and OCR uses Tesseract on CPU. Two OCR workers are a conservative starting point; Tesseract subprocesses use `OMP_THREAD_LIMIT=1`. FFmpeg decoding, speech preparation, system memory and disk access remain shared resources. The worker count is not a global CPU cap. Reduce workers if contention affects the GPU batch. The default sampling remains one frame per second plus intervening scene changes; the visual archive can be large.

Whisper may warn about unavailable Triton timing kernels and use slower timing implementations. Those warnings alone do not mean speech decoding fell back to CPU; inspect `device.json` and current progress before diagnosing a failure. Machine output can repeat words during silence and must be reviewed against the source.

## Local batch coordination

The September 17–19 intake folder contains `run-local-transcriptions.py`, `run-local-visuals.py` and its own README. These are machine-specific launchers, separate from the portable exporters. The audio launcher:

- Runs one CUDA speech job at a time with three CPU helper threads and the cached model.
- Hashes each source, retains duplicate aliases, and reuses completed matching-source transcripts.
- Leaves chunk-level resume and settings verification to the unchanged audio exporter.
- Writes progress through unique temporary files and retries transient Dropbox replacement locks.
- Holds its batch lock until its child exits, even if publishing the child PID fails.

Check both the batch PID and any child `.export.lock` before recovery. An old coordinator error is not evidence that its child stopped. Never start a replacement worker in an active export folder. A completed-output reuse is a same-source recovery operation; for a new model, exporter or extraction settings, choose a new output version instead.

Do not edit the core exporter or runtime helper while an existing batch depends on their saved hashes. Launcher and documentation updates do not alter those fingerprints, and an already-running launcher does not hot-reload edits. Monitoring of the current batch is a separate Codex automation, not a watcher installed by these scripts.
