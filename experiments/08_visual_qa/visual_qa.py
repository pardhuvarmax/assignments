"""
Visual QA: answers a question about ONE specific image by sending the
actual image pixels to the vision model -- not the cached caption. This is
the step that can get precise details (counts, exact colors, which light
is lit) that the coarse retrieval caption deliberately leaves out.
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import llm

HERE = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(HERE, "images")

SYSTEM_INSTRUCTION = (
    "Answer the question using only what is visibly in the image. Be "
    "precise about counts, colors, positions, and text/labels you can "
    "actually see. If the image doesn't show enough to answer, say so."
)


def answer(image_name: str, question: str) -> str:
    path = os.path.join(IMAGES_DIR, image_name)
    return llm.describe_image(path, question, system_instruction=SYSTEM_INSTRUCTION)
