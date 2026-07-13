# Decode Scan

Target: source-only GitHub repo. No compiled binaries, no archives, no source maps.
Magic-byte scan confirmed all files are text (Python/TS/JS/shell/YAML/JSON/MD) or media
assets (PNG/JPEG/MP4/PDF/ICO). No decompilation or archive extraction required.

## Base64 strings (>=40 chars) — sample
Most are incidental (token examples, test fixtures, chart data). High-value candidates:
/usr/share/fonts/truetype/dejavu/DejaVuSans
/usr/share/fonts/truetype/liberation/LiberationSans
com/allenai/multimodalqa/master/dataset/MMQA
de9725ba5457460a9e5b0f89548e6657UN5YStvS5ingpklvVohWgOMiYRxn

## Verdict
No encoded blobs, no embedded archives, no nested encodings to recurse on (depth 0).
The repo is clean application source — extraction is a direct copy.
