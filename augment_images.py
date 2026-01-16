import os
import argparse
from pathlib import Path
from typing import Tuple
import random

import cv2
import numpy as np
from tqdm import tqdm


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)
    


