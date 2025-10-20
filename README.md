# HighlightMaker (2025‑10‑20)

Automated pipeline to preprocess (EXIF + perceptual hashing), cluster, sequence, tag, and rough‑assemble photos & videos from the image and video files into an editable draft before fine editorial work (color grading, captions, motion effects). Supports generating a horizontal master (16:9) and a vertical social version (9:16).

> Focus sports: running, tug of war, high five / celebration.  
> Teams by shirt color: Blue (청팀), White (백팀), Staff (Black).  

---

## Table of Contents
- [Goals](#goals)
- [Features](#features)
- [Folder Structure](#folder-structure)
- [Install & Environment](#install--environment)
- [End-to-End Workflow](#end-to-end-workflow)
- [Scripts Overview](#scripts-overview)
- [Typical Usage Quick Start](#typical-usage-quick-start)
- [Improving Cutlist Quality](#improving-cutlist-quality)
- [Slow Motion Handling](#slow-motion-handling)
- [Vertical (9:16) Version](#vertical-916-version)
- [Troubleshooting](#troubleshooting)
- [Optimization Tips](#optimization-tips)
- [Next Ideas](#next-ideas)
- [License](#license)

---

## Goals
1. Rapid first pass organization of large, unordered photo/video dumps.
2. Detect near‑duplicate / burst photos and convert them into short sequences.
3. Provide an auto‑generated draft cutlist grouped by semantic sections (intro, prep, team, running, tug, highfive, group, misc).
4. Produce slow‑motion variants of highlight clips.
5. Build a rough concatenated draft for review before detailed NLE editing.
6. Re‑frame final horizontal master to a vertical format for social media.

---

## Features
| Area | Capability |
|------|------------|
| Metadata | EXIF extraction (DateTimeOriginal) + perceptual hash (pHash) |
| Clustering | pHash distance grouping (distance threshold configurable) |
| Burst → Sequence | Convert clusters above a size threshold to numbered image sequences → MP4 |
| Team Tagging | Simple color heuristic (blue / white / staff_black / unknown) |
| Cutlist Generation | Assign sequences/photos to logical sections based on filename keywords |
| Slow Motion | Declarative list (file, factor) → generated retimed clips |
| Rough Draft | FFmpeg concat list creation → draft MP4 |
| Vertical Output | Face‑aware 16:9 → 9:16 cropping (Haar Cascade + smoothing) |
| Uniform Transcode | Optional pass to standardize resolution/fps/codec |
| Extensibility | Modular scripts, easily swapped pHash threshold, min cluster size, keyword patterns |

---

## Folder Structure
```
raw/
  photo/              # Original photos (.jpg/.png)
  video/              # Original videos (.mp4)
  music/              # Background music track(s)
metadata/
  photos.csv
  photo_clusters.csv
  photo_tags.csv
  timeline_cutlist_generated.md
  slow_list.txt
  concat_list.txt
work/
  sequences/          # Cluster-based sequence MP4s
  slow/               # Slow-motion outputs
  uniform/            # Normalized resolution/fps re-encodes
  vertical/           # Vertical reframed outputs
  selects/            # (Optional) curated chosen assets
  models/             # haarcascade_frontalface_default.xml
outputs/
  drafts/             # draft_v1.mp4 etc.
  final/              # final master + vertical export
scripts/              # All Python helper scripts
logs/                 # (Optional) execution logs
```

---

## Install & Environment
```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

`requirements.txt` (example):
```
imagehash==4.3.2
Pillow==12.0.0
ExifRead==3.5.1
opencv-python==4.12.0.88
pandas==2.2.2
imageio-ffmpeg==0.6.0
```

FFmpeg:
- Either system PATH static build (e.g. gyan.dev).
- Or use `imageio-ffmpeg`’s bundled binary (path resolved programmatically).

---

## End-to-End Workflow
| Step | Script | Description | Output |
|------|--------|-------------|--------|
| 1 | `extract_and_cluster.py` | Scan photos, extract EXIF, pHash, cluster | `photos.csv`, `photo_clusters.csv` |
| 2 | `cluster_to_sequences_seq.py` | Convert qualifying clusters to numbered sequences → MP4 | `work/sequences/clusterX_seq.mp4` |
| 3 | `auto_tag_photos.py` | Rough team color tagging | `photo_tags.csv` |
| 4 | `generate_cutlist.py` | Build draft cutlist by filename patterns | `timeline_cutlist_generated.md` |
| 5 | `make_slowmo.py` | Produce slow-motion variants from list | `work/slow/*_slow.mp4` |
| 6 | `create_uniform_videos.py` (optional) | Normalize codec/size/fps | `work/uniform/*_u.mp4` |
| 7 | `build_rough_concat.py` | Create FFmpeg concat list | `concat_list.txt` |
| 8 | `ffmpeg concat` | Rough draft assembly | `outputs/drafts/draft_v1.mp4` |
| 9 | Manual NLE (Premiere/Resolve) | Color, text, rhythm edits | `outputs/final/...mp4` |
| 10 | `vertical_reframe.py` | 16:9 master → 9:16 vertical crop | `work/vertical/Mangwon_Field_Day_vertical_full.mp4` |

---

## Scripts Overview
| Script | Key Params | Notes |
|--------|------------|-------|
| `extract_and_cluster.py` | `THRESH` (pHash distance) | Increase THRESH if clusters too small; decrease if over-grouping |
| `cluster_to_sequences_seq.py` | `MIN_COUNT`, frame rates | Converts bursts to sequences using `%04d` pattern (glob unsupported workaround) |
| `auto_tag_photos.py` | Internal thresholds | Simple heuristic; refine manually if needed |
| `generate_cutlist.py` | Keyword regex patterns | Add keywords to filenames for better section classification |
| `make_slowmo.py` | `slow_list.txt` factors | Factor 2.0–2.5 → 40–50% speed |
| `create_uniform_videos.py` | Fixed 1920x1080 30fps | Use when concat fails due to heterogeneous streams |
| `build_rough_concat.py` | Section ordering | Only includes existing MP4 assets |
| `vertical_reframe.py` | Haar cascade path, smoothing `alpha` | Lower `alpha` for less jitter |
| `rename_to_pattern.py` | RULES list | Helps reclassify generic filenames (optional) |

---

## Typical Usage Quick Start
```bash
python scripts/extract_and_cluster.py
python scripts/cluster_to_sequences_seq.py
python scripts/auto_tag_photos.py
python scripts/generate_cutlist.py
# Edit metadata/slow_list.txt (file, factor)
python scripts/make_slowmo.py
python scripts/build_rough_concat.py
ffmpeg -y -f concat -safe 0 -i metadata/concat_list.txt -c:v libx264 -preset fast -pix_fmt yuv420p -c:a aac -b:a 192k outputs/drafts/draft_v1.mp4
```
Then open the draft in your NLE for refinement.

---

## Improving Cutlist Quality
If many sections show `- (none)`:
1. **Filename Keywords Missing**: Rename files with semantic prefixes (e.g., `run_start_01.jpg`, `tug_clash_01.mp4`, `highfive_seq_01.jpg`).
2. **Clusters Too Small**: Raise pHash threshold (`THRESH` 6 → 7 or 8) or lower `MIN_COUNT` (3 → 2).
3. **Manual Override**: Create a manual file `metadata/timeline_cutlist_manual.md` and adapt `build_rough_concat.py` to parse it.
4. **Add Pattern Variants**: Extend regex patterns in `generate_cutlist.py` for local naming conventions (e.g., Korean terms: `달리기`, `줄다리기`, `하이파이브`).

Example manual template:
```markdown
## running
- run_start_clip1.mp4
- run_mid_seq.mp4
- run_finish_slow.mp4
## tug
- tug_prepare_close.jpg
- tug_clash_clip1.mp4
...
```

---

## Slow Motion Handling
- Use high framerate originals (≥60fps) for best results.
- Recommended factor range: 2.0–2.5 (setpts=2.0*PTS → 50% speed).
- Remove noisy on‑camera audio (`-an`) and replace with clean music track.
- If motion judder appears, consider optical flow (external tools) or choose different source clip.

---

## Vertical (9:16) Version
1. Export final 16:9 master (`outputs/final/...mp4`).
2. Download `haarcascade_frontalface_default.xml` to `work/models/`.
3. Run `vertical_reframe.py`.
4. Inspect framing—adjust smoothing `alpha` (0.15 → 0.1) or enforce center crop for crowd scenes.
5. Recreate lower‑third titles near top 10–12% safe margin (avoid obstruction by platform UI).

---

## Troubleshooting
| Symptom | Cause | Fix |
|---------|-------|-----|
| Few or no sequences | MIN_COUNT too high / THRESH too low | Lower MIN_COUNT / raise THRESH |
| Concat failure (stream mismatch) | Mixed resolutions/codecs | Run `create_uniform_videos.py` before concat |
| Glob pattern error | FFmpeg build lacks globbing | Using `%04d` pattern resolves this (already implemented) |
| Mis-tagged teams | Simple color heuristic limits | Edit `photo_tags.csv` manually |
| Vertical crop jitter | Face detection unstable | Reduce `alpha` or fallback to center crop |
| Excessive duplicates | THRESH too high | Lower threshold & re-run clustering |

---

## Optimization Tips
- Pre‑filter unusable assets (blur, out‑of‑focus) before hashing to save time.
- Maintain a curated “selects” list for final editorial decisions.
- Use a separate branch or tag (e.g., `baseline-draft`) before significant pipeline tuning.
- Keep large binaries (original raw video) out of git (use Git LFS or external storage if needed).

---

## Next Ideas
- Beat detection to auto‑align cuts with music transients.
- Pose / action recognition (switch to Mediapipe in Python 3.11 for better vertical reframing).
- Automatic highlight scoring (motion intensity + cheering detection).
- Thumbnail auto‑generation: brightest faces + team color accents + overlay title.
- Timeline EDL/XML export for direct import into NLE.

---

## License
Choose one appropriate for collaborative improvement (e.g., MIT):

```text
MIT License – See LICENSE file for details.
```

---

## Attribution / Credits
- Event organized by Mangwon Youth Association.
- Participants consented to image usage.
- Music track: (verify licensing; add attribution if required).

---

## Status Badges (optional)
(Add CI, Code Style, or Lint badges here once set up.)

---

Happy editing!  
Feel free to open issues / PRs for enhancements to clustering, tagging, or cutlist logic.