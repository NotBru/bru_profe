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
    def _remap(ch):
        REMAP = {"<": "&lt;", ">": "&gt;", '"': "&quot;"}
        if ch in REMAP:
            return REMAP[ch]
        return ch

    def _formatted_character(self, i: int, j: int, ch: str):
        if ch == ' ':
            return ''
        fill = self.colors[(i, j)]
        style = f"font-family:'{self.fonts[(i, j)]}'"
        size = self._font_size
        y = 1 + (i + 1) * self._vstep
        x = 1 + j * self._hstep
        x += self.offsets[ch] * self._hstep
        ch = self._remap(ch)
        return (
            f'    <text x="{x}px" y="{y}px" font-size="{self._font_size}pt" '
                 f'fill="#{fill}" style="{style}">{ch}</text>\n')

    @staticmethod
    def _parse_file(content: str) -> dict:
        split = content.split("\n", 22)
        lines = split[:22]
        if (
            len(split) < 23
            or (config := yaml.safe_load(io.StringIO(split[22]))) is None):

            config = {}
        config["background"] = config.get("background", "")
        config["foreground"] = config.get("foreground", "")
        return lines, config

    def _svg_lines(self, svg_file: io.TextIOBase, lines: list[str]):
        for i, line in enumerate(lines):
            for j, ch in enumerate(line):
                svg_file.write(self._formatted_character(i, j, ch))

    @staticmethod
    def _svg_external_image(svg_file: io.TextIOBase, filepath: str,
        pwd: Path):

        if filepath == "":
            return
        if filepath[0] in ["/", "~"]:
            filepath = Path(filepath)
        else:
            filepath = pwd / filepath
        absolute = filepath.resolve()
        svg_file.write(f'    <image x="0" y="0" xlink:href="{absolute}"/>\n')

    def _svg_header(self, svg_file: io.TextIOBase):
        width = self._width
        height = self._height
        svg_file.write('<svg \n'
            f'  width="{width}px"\n'
            f'  height="{height}px"\n'
            '  xmlns:xlink="http://www.w3.org/1999/xlink"\n'
            '  xmlns="http://www.w3.org/2000/svg"\n'
            '  xmlns:svg="http://www.w3.org/2000/svg">\n')
        svg_file.write(f'    <rect width="{width}px" height="{height}px" '
                            f'fill="#{self.background_color}"/>\n')

    def render(self, content: str, target: Union[Path, str], pwd: Path):
        lines, config = self._parse_file(content)
        svg_target = str(target)+".svg"

        with open(svg_target, "w") as svg_file:
            self._svg_header(svg_file)
            self._svg_external_image(svg_file, config["background"], pwd)
            self._svg_lines(svg_file, lines)
            self._svg_external_image(svg_file, config["foreground"], pwd)
            svg_file.write("</svg>")

        png_target=str(target)+".png"
        os.system(f'inkscape "{svg_target}" -o "{png_target}" 2>/dev/null')
        Path(svg_target).unlink()

    def __init__(self, width=1366, height=768, h_chars=79, v_chars=22,
        offsets: Optional[defaultdict]=None, default_color="00FFAF",
        background_color="000000FF",
        default_font="CaskaydiaCove Nerd Font Mono",):

        self.background_color = background_color
        self.default_color = default_color
        self.default_font = default_font
        self.colors = defaultdict(lambda: self.default_color)
        self.fonts = defaultdict(lambda: self.default_font)
        if offsets is None:
            offsets = defaultdict(lambda: 0)
            offsets["í"] = offsets["Í"] = 2 / 7
        self.offsets = offsets
        self._width = width
        self._height = height
        self._hstep = (width - 2) / h_chars
        self._vstep = (height - 2) / v_chars * .99
        # 1pt = 96/72 px
        # 6/7th of a step for the font
        self._font_size = self._vstep * 72 * 7 / 8 / 96

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
    renderer = Renderer()
    i = 0
    while (name := str(i)) in filenames:
        with open(dir_ / name, "r") as inf:
            renderer.render(inf.read(), target_dir / name, dir_)
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
