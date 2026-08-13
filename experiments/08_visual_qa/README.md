# Experiment 8 — Image Retrieval / Visual QA System

Develop a **multimodal pipeline**: find the right image for a text query,
then answer a precise question about it using the model's vision
capability — and see exactly where a cheap retrieval signal (a caption)
stops being enough and looking at actual pixels starts mattering.

## Why synthetic, procedurally-drawn images

There's no image-search tool in this environment, and downloading real
images raises licensing/provenance questions this experiment doesn't need
to deal with. `generate_images.py` draws 5 images with Pillow instead —
deterministic, reproducible, and with **known ground truth** for every
visual detail (exact bar heights/colors, exact box counts, which traffic
light is lit), so a VQA answer can actually be checked for correctness:

| Image | Contains |
|---|---|
| `quarterly_revenue.png` | A 4-bar chart, Q1-Q3 blue, Q4 (tallest) orange |
| `network_diagram.png` | 4 labeled nodes (Server, Database, Client A, Client B), 3 edges |
| `traffic_scene.png` | A traffic light with only the red lamp lit, a car on a road |
| `weather_icons.png` | 4 icons in a grid: sun, cloud, rain, snow |
| `warehouse_plan.png` | 3 labeled zones; exactly 5 boxes drawn in the Storage zone |

## Pipeline

```
images/*.png
      │
      ▼
1. Indexing (indexer.py)    — one vision call per image produces a
                               deliberately COARSE caption (topic only, no
                               counts/colors), then the caption is embedded
      │
query │
      ▼
2. Retrieval (retriever.py) — embed the query, rank images by caption
                               similarity, no vision call needed here
      │
      ▼
3. Visual QA (visual_qa.py) — one vision call on the ACTUAL pixels of the
                               top-matched image to answer a precise
                               question the caption was never meant to
```

This mirrors a real constraint: there's no off-the-shelf image-embedding
model in this stack, so retrieval works by embedding a caption instead
(cheap, coarse, scalable across many images). Getting a precise answer
still needs a real vision call on the specific image, which is why that
step only runs once, on the one image retrieval already narrowed down to.

## Run it

```bash
cd experiments
pip install -r requirements.txt        # includes Pillow now
python 08_visual_qa/main.py
```

Needs `GEMINI_API_KEY`. First run captions all 5 images (5 vision calls),
cached to `visual_index.json` afterward (auto-rebuilds if `images/`
changes). Each visual question costs one more vision call.

Try search queries: `which quarter had the best revenue`, `is the
intersection safe to cross`, `how much inventory is being stored`. Then ask
a follow-up like `what color is the highest bar, and which quarter is it?`

**Verified live**: all 5 captions came back correctly coarse (e.g. "A bar
chart of quarterly revenue" — no color or exact values), retrieval matched
`quarterly_revenue.png` for a revenue query, and the VQA call correctly
answered "The highest bar is orange, and it is Q4" — a level of precision
the caption deliberately didn't carry.

## Files

| File | Purpose |
|---|---|
| `generate_images.py` | Procedurally draws the 5 sample images with Pillow |
| `images/` | The generated sample images (committed, reproducible via the script above) |
| `indexer.py` | Captions each image (vision call) + embeds the caption, with caching |
| `retriever.py` | Text query → ranked images by caption similarity |
| `visual_qa.py` | Answers a question about one image using its actual pixels |
| `main.py` | CLI: search → show candidates → ask a precise question about the top match |

## Notes / limitations

- Retrieval quality is bounded by how well the one-sentence caption
  captures what a query might ask about — a caption that's too coarse
  could plausibly under-retrieve for a query about fine detail. This
  experiment's captions are intentionally coarse to make that gap visible.
- Every visual question costs a fresh vision API call; there's no
  caching of Q&A answers the way captions are cached, since the same
  image can be asked about in many different ways.
