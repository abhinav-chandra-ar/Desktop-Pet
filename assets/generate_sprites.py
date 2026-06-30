"""
Pixel-art lion sprite generator.
Draws on a 16x16 grid then scales 3x with NEAREST -> 48x48 per frame.
Every shape is a rectangle or individual pixel — no circles.
"""

from pathlib import Path
from PIL import Image

OUT = Path(__file__).parent / "sprites"
OUT.mkdir(exist_ok=True)

SRC  = 16    # source canvas size (px)
SCALE = 3    # scale factor  =>  48 x 48 per frame

# ── Palette (single-char keys) ────────────────────────────────────────────────
P: dict[str, tuple] = {
    ".": (  0,   0,   0,   0),   # transparent
    "M": ( 90,  44,   6, 255),   # mane dark
    "m": (140,  82,  20, 255),   # mane mid
    "F": (230, 178,  82, 255),   # face / light fur
    "b": (195, 142,  50, 255),   # body
    "s": (140, 100,  28, 255),   # shadow / belly
    "e": ( 22,  14,   4, 255),   # eye dark (pupil)
    "W": (255, 255, 255, 255),   # eye white
    "n": (192,  68,  68, 255),   # nose
    "p": (175, 126,  40, 255),   # paw
    "t": (160, 115,  32, 255),   # tail
    "T": ( 80,  44,   8, 255),   # tail tip
    "z": (155, 175, 220, 200),   # zzz
    "R": (220,  88,  88, 120),   # blush (semi-transparent)
    "o": ( 80,  28,  18, 255),   # open mouth
    "L": (230, 200, 160, 255),   # tongue / highlight
    "c": (255, 225, 175, 255),   # catchlight in eye
}


def px_img(rows: list[str]) -> Image.Image:
    """
    Build a 16x16 RGBA image from a list of 16-char strings,
    then scale up with NEAREST for crisp pixel-art blocks.
    """
    img = Image.new("RGBA", (SRC, SRC), (0, 0, 0, 0))
    for y, row in enumerate(rows[:SRC]):
        for x, ch in enumerate(row[:SRC]):
            color = P.get(ch, P["."])
            img.putpixel((x, y), color)
    return img.resize((SRC * SCALE, SRC * SCALE), Image.NEAREST)


def sheet(frames: list[Image.Image]) -> Image.Image:
    if not frames:
        return Image.new("RGBA", (SRC * SCALE, SRC * SCALE))
    w, h = frames[0].size
    s = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        s.paste(f, (i * w, 0))
    return s


# ── Base lion facing RIGHT ────────────────────────────────────────────────────
#
# Column guide:  0123456789012345
#                          1111111
#
# M = mane dark   m = mane mid   F = face   b = body   s = shadow
# W = eye white   e = eye dark   n = nose   p = paw    . = clear

IDLE_A = [          # body shifted up 1 row (bob frame A)
    "................",
    "..MM......MM....",
    ".MmmM....MmmM...",
    "MmmmmmmmmmmmM...",
    "MmFFFFFFFFFFmM..",
    "MmFWWeFFWeWFmM..",
    "MmFWeFFFFeWFmM..",
    "MmFFFFnFFFFFmM..",
    "MmFFFFFFFFFFmM..",
    "MmbbbbbbbbbbbM..",   # body starts
    ".Mbbbbbbbbbbb...",
    "..bbbsssssbbb...",   # belly shadow
    ".pp.bbbbbbb.pp..",   # paws
    ".pp.........pp..",
    "................",
    "................",
]

IDLE_B = [          # body 1 row lower (bob frame B)
    "................",
    "..MM......MM....",
    ".MmmM....MmmM...",
    "MmmmmmmmmmmmM...",
    "MmFFFFFFFFFFmM..",
    "MmFWWeFFWeWFmM..",
    "MmFWeFFFFeWFmM..",
    "MmFFFFnFFFFFmM..",
    "MmFFFFFFFFFFmM..",
    ".Mbbbbbbbbbbb...",  # body 1 lower
    "..bbbbbbbbbbb...",
    "..bbbsssssbbb...",
    ".pp.bbbbbbb.pp..",
    ".pp.........pp..",
    "................",
    "................",
]

IDLE_BLINK = [      # eyes closed
    "................",
    "..MM......MM....",
    ".MmmM....MmmM...",
    "MmmmmmmmmmmmM...",
    "MmFFFFFFFFFFmM..",
    "MmFFFFFFFFFFFM..",   # eyes closed (no W/e)
    "MmFeeFFFFeeFFM..",   # thin closed-eye line
    "MmFFFFnFFFFFmM..",
    "MmFFFFFFFFFFmM..",
    "MmbbbbbbbbbbbM..",
    ".Mbbbbbbbbbbb...",
    "..bbbsssssbbb...",
    ".pp.bbbbbbb.pp..",
    ".pp.........pp..",
    "................",
    "................",
]


# ── Walk frames (facing right) ────────────────────────────────────────────────

WALK_R = [          # walk right: 4 frames, paws alternate
    [  # frame 0 – left paw fwd, right paw back
        "................",
        "..MM......MM....",
        ".MmmM....MmmM...",
        "MmmmmmmmmmmmM...",
        "MmFFFFFFFFFFmM..",
        "MmFWWeFFWeWFmM..",
        "MmFWeFFFFeWFmM..",
        "MmFFFFnFFFFFmM..",
        "MmFFFFFFFFFFmM..",
        "MmbbbbbbbbbbbM..",
        ".Mbbbbbbbbbbb...",
        "..bbbsssssbbb...",
        ".p..bbbbbbb..pp.",   # L fwd, R back
        "pp...........pp.",
        "................",
        "................",
    ],
    [  # frame 1 – mid-step bob up
        "................",
        "..MM......MM....",
        ".MmmM....MmmM...",
        "MmmmmmmmmmmmM...",
        "MmFFFFFFFFFFmM..",
        "MmFWWeFFWeWFmM..",
        "MmFWeFFFFeWFmM..",
        "MmFFFFnFFFFFmM..",
        "MmbbbbbbbbbbbM..",   # body up 1
        ".Mbbbbbbbbbbb...",
        "..bbbbbbbbbbb...",
        "..bbbsssssbbb...",
        ".pp.bbbbbbb.pp..",
        ".pp.........pp..",
        "................",
        "................",
    ],
    [  # frame 2 – right paw fwd, left paw back
        "................",
        "..MM......MM....",
        ".MmmM....MmmM...",
        "MmmmmmmmmmmmM...",
        "MmFFFFFFFFFFmM..",
        "MmFWWeFFWeWFmM..",
        "MmFWeFFFFeWFmM..",
        "MmFFFFnFFFFFmM..",
        "MmFFFFFFFFFFmM..",
        "MmbbbbbbbbbbbM..",
        ".Mbbbbbbbbbbb...",
        "..bbbsssssbbb...",
        ".pp.bbbbbbb..p..",   # R fwd, L back
        ".pp..........p..",
        "................",
        "................",
    ],
    [  # frame 3 – mid-step
        "................",
        "..MM......MM....",
        ".MmmM....MmmM...",
        "MmmmmmmmmmmmM...",
        "MmFFFFFFFFFFmM..",
        "MmFWWeFFWeWFmM..",
        "MmFWeFFFFeWFmM..",
        "MmFFFFnFFFFFmM..",
        "MmbbbbbbbbbbbM..",
        ".Mbbbbbbbbbbb...",
        "..bbbbbbbbbbb...",
        "..bbbsssssbbb...",
        ".pp.bbbbbbb.pp..",
        "................",
        "................",
        "................",
    ],
]


def mirror(rows: list[str]) -> list[str]:
    """Horizontally flip a pixel map (for walk left)."""
    return [row[::-1] for row in rows]


# ── Sit ───────────────────────────────────────────────────────────────────────

SIT_A = [
    "................",
    "..MM......MM....",
    ".MmmM....MmmM...",
    "MmmmmmmmmmmmM...",
    "MmFFFFFFFFFFmM..",
    "MmFWWeFFWeWFmM..",
    "MmFWeFFFFeWFmM..",
    "MmFFFFnFFFFFmM..",
    "MmFFFFFFFFFFmM..",
    "MmbbbbbbbbbbmM..",
    ".Mbbbbbbbbbbm...",
    ".pbbssssssbbp...",   # paws beside body
    ".pbbbbbbbbbbp...",
    ".pp.........pp..",
    "................",
    "................",
]

SIT_B = [           # tail tucked to side (tail visible in col 13-14)
    "................",
    "..MM......MM....",
    ".MmmM....MmmM...",
    "MmmmmmmmmmmmM...",
    "MmFFFFFFFFFFmM..",
    "MmFFFFFFFFFFFM..",   # blink mid-sit
    "MmFeeFFFFeeFFM..",
    "MmFFFFnFFFFFmM..",
    "MmFFFFFFFFFFmM..",
    "MmbbbbbbbbbbmMtt",   # tail curling right
    ".Mbbbbbbbbbbm.tT",
    ".pbbssssssbbp...",
    ".pbbbbbbbbbbp...",
    ".pp.........pp..",
    "................",
    "................",
]


# ── Sleep ─────────────────────────────────────────────────────────────────────

SLEEP_A = [         # lying flat, eyes closed
    "................",
    "................",
    "................",
    "..MMMMMMMMMM....",
    ".MmmmmmmmmmmmM..",
    ".MmFFFFFFFFFFm..",
    ".MmFeeFFFFeeeFm.",   # eyes closed
    ".MmFFFFFFFFFFFm.",
    ".MmFFFFFFFFFFm..",
    "MmbbbbbbbbbbbmM.",
    ".Mbbbbbbbbbbbb..",
    "..bbbssssbbbb...",
    "................",
    "................",
    "................",
    "................",
]

SLEEP_B = [         # same + zzz
    "................",
    "................",
    "................",
    "..MMMMMMMMMM....",
    ".MmmmmmmmmmmmM..",
    ".MmFFFFFFFFFFm..",
    ".MmFeeFFFFeeeFm.",
    ".MmFFFFFFFFFFFm.",
    ".MmFFFFFFFFFFm..",
    "MmbbbbbbbbbbbmM.",
    ".Mbbbbbbbbbbbb..",
    "..bbbssssbbbb...",
    ".........z......",   # zzz
    "........z.......",
    "................",
    "................",
]

SLEEP_C = [         # bigger zzz
    "................",
    "................",
    "................",
    "..MMMMMMMMMM....",
    ".MmmmmmmmmmmmM..",
    ".MmFFFFFFFFFFm..",
    ".MmFeeFFFFeeeFm.",
    ".MmFFFFFFFFFFFm.",
    ".MmFFFFFFFFFFm..",
    "MmbbbbbbbbbbbmM.",
    ".Mbbbbbbbbbbbb..",
    "..bbbssssbbbb...",
    "........zzz.....",
    ".......z.......",
    "................",
    "................",
]


# ── Wake ──────────────────────────────────────────────────────────────────────

WAKE_A = [          # eyes half open (still lying)
    "................",
    "................",
    "................",
    "..MMMMMMMMMM....",
    ".MmmmmmmmmmmmM..",
    ".MmFFFFFFFFFFm..",
    ".MmFeeFFFFeeeFm.",
    ".MmFFFFFFFFFFFm.",
    ".MmFFFFFFFFFFm..",
    "MmbbbbbbbbbbbmM.",
    ".Mbbbbbbbbbbbb..",
    "..bbbssssbbbb...",
    "................",
    "................",
    "................",
    "................",
]

WAKE_B = [          # sitting up, eyes half open
    "................",
    "..MM......MM....",
    ".MmmM....MmmM...",
    "MmmmmmmmmmmmM...",
    "MmFFFFFFFFFFmM..",
    "MmFFFFFFFFFFFM..",
    "MmFeeFFFFeeFmM..",   # half-open eyes
    "MmFFFFnFFFFFmM..",
    "MmFFFFFFFFFFmM..",
    "MmbbbbbbbbbbmM..",
    ".Mbbbbbbbbbbm...",
    ".pbbssssssbbp...",
    ".pbbbbbbbbbbp...",
    ".pp.........pp..",
    "................",
    "................",
]

WAKE_C = [          # fully awake (same as idle_A)
    "................",
    "..MM......MM....",
    ".MmmM....MmmM...",
    "MmmmmmmmmmmmM...",
    "MmFFFFFFFFFFmM..",
    "MmFWWeFFWeWFmM..",
    "MmFWeFFFFeWFmM..",
    "MmFFFFnFFFFFmM..",
    "MmFFFFFFFFFFmM..",
    "MmbbbbbbbbbbbM..",
    ".Mbbbbbbbbbbb...",
    "..bbbsssssbbb...",
    ".pp.bbbbbbb.pp..",
    ".pp.........pp..",
    "................",
    "................",
]


# ── Happy ─────────────────────────────────────────────────────────────────────

HAPPY_A = [         # eyes closed happy, blush
    "................",
    "..MM......MM....",
    ".MmmM....MmmM...",
    "MmmmmmmmmmmmM...",
    "MmFFFFFFFFFFmM..",
    "MmFRFFFFFFRFmM..",   # blush spots
    "MmFeeFFFFeeFFM..",   # closed eyes
    "MmFFFFnFFFFFmM..",
    "MmFFFFFFFFFFmM..",
    "MmbbbbbbbbbbbM..",
    ".Mbbbbbbbbbbb...",
    "..bbbsssssbbb...",
    ".pp.bbbbbbb.pp..",
    ".pp.........pp..",
    "................",
    "................",
]

HAPPY_B = [         # bouncing up + blush
    "................",
    "..MM......MM....",
    ".MmmM....MmmM...",
    "MmmmmmmmmmmmM...",
    "MmFFFFFFFFFFmM..",
    "MmFRFFFFFFRFmM..",
    "MmFeeFFFFeeFFM..",
    "MmFFFFnFFFFFmM..",
    "MmbbbbbbbbbbbM..",   # body up 1
    ".Mbbbbbbbbbbb...",
    "..bbbbbbbbbbb...",
    "..bbbsssssbbb...",
    "...pbbbbbbbp....",   # paws closer in
    "................",
    "................",
    "................",
]

HAPPY_C = HAPPY_A
HAPPY_D = HAPPY_B


# ── Roar ──────────────────────────────────────────────────────────────────────

ROAR_A = IDLE_A     # building up

ROAR_B = [          # lean forward, mouth open
    "................",
    "..MM......MM....",
    ".MmmM....MmmM...",
    "MmmmmmmmmmmmM...",
    "MmFFFFFFFFFFmM..",
    "MmFWWeFFWeWFmM..",
    "MmFWeFFFFeWFmM..",
    "MmFFooooooFFmM..",   # open mouth
    "MmFFoLLLLooFmM..",   # tongue visible
    "MmbbbbbbbbbbbM..",
    ".Mbbbbbbbbbbb...",
    "..bbbsssssbbb...",
    ".pp.bbbbbbb.pp..",
    ".pp.........pp..",
    "................",
    "................",
]

ROAR_C = [          # full roar + lines
    "...........lll..",   # sound lines (using z for visual lines)
    "..MM......MMzz..",
    ".MmmM....MmmMz..",
    "MmmmmmmmmmmmM...",
    "MmFFFFFFFFFFmM..",
    "MmFWWeFFWeWFmM..",
    "MmFWeFFFFeWFmM..",
    "MmFFooooooFFmM..",
    "MmFFoLLLLooFmM..",
    "MmbbbbbbbbbbbM..",
    ".Mbbbbbbbbbbb...",
    "..bbbsssssbbb...",
    ".pp.bbbbbbb.pp..",
    ".pp.........pp..",
    "................",
    "................",
]


# ── Jump ──────────────────────────────────────────────────────────────────────

JUMP_A = [          # crouch (prepare)
    "................",
    "..MM......MM....",
    ".MmmM....MmmM...",
    "MmmmmmmmmmmmM...",
    "MmFFFFFFFFFFmM..",
    "MmFWWeFFWeWFmM..",
    "MmFWeFFFFeWFmM..",
    "MmFFFFnFFFFFmM..",
    "MmFFFFFFFFFFmM..",
    ".MbbbbbbbbbbbM..",
    "..Mbbbbbbbbbb...",   # body lower = crouching
    "..pbbsssssbbbp..",
    "..ppbbbbbbbpp...",
    "..pp.........pp.",
    "................",
    "................",
]

JUMP_B = [          # airborne – body up high, legs dangling
    "................",
    "..MM......MM....",
    ".MmmM....MmmM...",
    "MmmmmmmmmmmmM...",
    "MmFFFFFFFFFFmM..",
    "MmFWWeFFWeWFmM..",
    "MmFWeFFFFeWFmM..",
    "MmFFFFnFFFFFmM..",
    "MmbbbbbbbbbbbM..",
    ".Mbbbbbbbbbbb...",
    "..bbbsssssbbb...",
    "..p.........p...",   # legs hanging
    "..p.........p...",
    "................",
    "................",
    "................",
]

JUMP_C = [          # peak (same as B)
    "................",
    "..MM......MM....",
    ".MmmM....MmmM...",
    "MmmmmmmmmmmmM...",
    "MmFFFFFFFFFFmM..",
    "MmFWWeFFWeWFmM..",
    "MmFWeFFFFeWFmM..",
    "MmFFFFnFFFFFmM..",
    "MmbbbbbbbbbbbM..",
    ".Mbbbbbbbbbbb...",
    "..bbbsssssbbb...",
    "...p.......p....",
    "................",
    "................",
    "................",
    "................",
]

JUMP_D = IDLE_A     # land (same as idle)


# ── Assemble all animations ───────────────────────────────────────────────────

ANIMATIONS: dict[str, list[list[str]]] = {
    "idle":       [IDLE_A, IDLE_B, IDLE_A, IDLE_BLINK, IDLE_B, IDLE_A],
    "idle_flip":  [mirror(f) for f in [IDLE_A, IDLE_B, IDLE_A, IDLE_BLINK, IDLE_B, IDLE_A]],
    "walk_right": WALK_R,
    "walk_left":  [mirror(f) for f in WALK_R],
    "sit":        [SIT_A, SIT_A, SIT_B, SIT_A],
    "sleep":      [SLEEP_A, SLEEP_B, SLEEP_C, SLEEP_B],
    "wake":       [WAKE_A, WAKE_A, WAKE_B, WAKE_C],
    "blink":      [IDLE_A, IDLE_BLINK, IDLE_BLINK, IDLE_A],
    "happy":      [HAPPY_A, HAPPY_B, HAPPY_C, HAPPY_D],
    "roar":       [ROAR_A, ROAR_B, ROAR_C, ROAR_B],
    "jump":       [JUMP_A, JUMP_B, JUMP_C, JUMP_D],
}


def generate_all():
    for name, frames in ANIMATIONS.items():
        images = [px_img(f) for f in frames]
        sht = sheet(images)
        path = OUT / f"{name}.png"
        sht.save(path)
        print(f"  OK {name}.png  ({len(frames)} frames, {sht.width}x{sht.height}px)")
    print("Done.")


if __name__ == "__main__":
    generate_all()
