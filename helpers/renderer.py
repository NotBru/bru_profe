from collections import defaultdict
from typing import Optional, Union
import io
import os
import sys

from pathlib import Path
import cairosvg
import yaml

class Renderer:

    @staticmethod
    def remap(ch):
        REMAP = {"<": "&lt;", ">": "&gt;", '"': "&quot;"}
        if ch in REMAP:
            return REMAP[ch]
        return ch

    def formatted_character(self, i: int, j: int, ch: str):
        fill = self.colors[(i, j)]
        style = f"font-family:'{self.fonts[(i, j)]}'"
        size = self._font_size
        y = 1 + (i + 1) * self._vstep
        x = 1 + j * self._hstep
        x += self.offsets[ch] * self._hstep
        ch = self.remap(ch)
        return (
            f'    <text x={x}px" y="{y}px" font-size="{self._font_size}pt" '
                 f'fill="#{fill}" style="{style}">{ch}</text>')

    def __init__(self, width=1366, height=768, h_chars=79, v_chars=22,
        offsets: Optional[defaultdict]=None, default_color="#00FFAF",
        default_font="CaskaydiaCove Nerd Font Mono",):
        self.default_color = default_color
        self.default_font = default_font
        self.colors = defaultdict(lambda: self.default_color)
        self.fonts = defaultdict(lambda: self.default_font)
        if offsets is None:
            offsets = defaultdict(lambda: 0)
            offsets["í"] = offsets["Í"] = 2 / 7
        else:
            self.offsets = offsets
        self._width = width
        self._height = height
        self._hstep = (width - 2) / h_chars
        self._vstep = (height - 2) / v_chars
        # 1pt = 96/72 px
        # 6/7th of a step for the font
        self._font_size = self._vstep * 96 * 6 / 7 / 72 

def parse(content: str) -> dict:
    split = content.split("\n", 22)
    lines = split[:22]
    if (
        len(split) < 23
        or (config := yaml.safe_load(io.StringIO(split[22]))) is None):

        config = {}
    return lines, config

def dump_text(lines: list[str], svg_file):
    FONT_STYLE = "CaskaydiaCove Nerd Font Mono"
    TEXT_STYLE = f"font-family:'{FONT_STYLE}';"
    TEXT_TEMPLATE = (
        '    <text x="{}" y="{}" font-size="22.3pt" xml:space="preserve" '
             'fill="#00FFAF" '
             'style="' + TEXT_STYLE + '">{}</text>\n')
    hstep=1364/79
    vstep=768/22.1
    for i, line in enumerate(lines):
        for j in range(min(79, len(line))):
            if line[j] == " ":
                continue
            content = line[j]
            if line[j] in ["í", "Í"]:
                offset = hstep * 2 / 7
            else:
                offset = 0

            if content == "<":
                content = "&lt;"
            elif content == ">":
                content = "&gt;"
            elif content == '"':
                content = "&quot;"
            svg_file.write(
                TEXT_TEMPLATE.format(1+hstep*j+offset, vstep*(i+1), content))

def dump_external(filepath: str, svg_file, pwd: Path):
    if filepath == "":
        return
    if filepath[0] == "/" or filepath[0] == "~":
        filepath = Path(filepath)
    else:
        filepath = pwd / filepath
    absolute = filepath.resolve()
    svg_file.write(f'    <image x="0" y="0" xlink:href="{absolute}"/>\n')

def render(content: str, target: Union[Path, str]):
    lines, config = parse(content)
    svg_target=str(target)+".svg"
    pwd = target.parent.parent
    with open(svg_target, "w") as svg_file:
        svg_file.write('<svg \n'
            '  width="1366px"\n'
            '  height="768px"\n'
            '  xmlns:xlink="http://www.w3.org/1999/xlink"\n'
            '  xmlns="http://www.w3.org/2000/svg"\n'
            '  xmlns:svg="http://www.w3.org/2000/svg">\n')
        svg_file.write('    <rect width="1366px" height="768px"/>\n')
        dump_external(config.get("background", ""), svg_file, pwd)
        dump_text(lines, svg_file)
        dump_external(config.get("foreground", ""), svg_file, pwd)
        svg_file.write('</svg>')
    png_target=str(target)+".png"
    os.system(f'inkscape "{svg_target}" -o "{png_target}" 2>/dev/null')
    Path(svg_target).unlink()

def num_digits(n: int):
    d = 1
    while 10 ** d <= n:
        d += 1
    return d

def run(dir_: Path) -> int:
    filenames = [ path.name for path in dir_.iterdir() ]
    target_dir = dir_ / "rendered"
    target_dir.mkdir(exist_ok=True)
    for fn in target_dir.iterdir():
        fn.unlink()
    i = 0
    while (name := str(i)) in filenames:
        with open(dir_ / name, "r") as inf:
            render(inf.read(), target_dir / name)
        i += 1
    digits = num_digits(i - 1)
    for j in range(i):
        (target_dir / f"{j}.png").rename(target_dir / f"{j:0{digits}d}.png")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("What the hell, Bru.", file=sys.stderr)
        exit(1)
    dir_ = Path(sys.argv[1])
    exit(run(dir_))
