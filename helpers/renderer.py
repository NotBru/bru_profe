from typing import Union
import io
import os
import sys

from pathlib import Path
import cairosvg
import yaml

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
    vstep=768/22
    for i, line in enumerate(lines):
        for j in range(min(79, len(line))):
            if line[j] == " ":
                continue
            if line[j] in ["í", "Í"]:
                offset = hstep * 2 / 7
            else:
                offset = 0
            svg_file.write(
                TEXT_TEMPLATE.format(1+hstep*j+offset, vstep*(i+1), line[j]))

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

def run(dir_: Path) -> int:
    filenames = [ path.name for path in dir_.iterdir() ]
    target_dir = dir_ / "rendered"
    target_dir.mkdir(exist_ok=True)
    i = 0
    while (name := str(i)) in filenames:
        with open(dir_ / name, "r") as inf:
            render(inf.read(), target_dir / name)
        i += 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("What the hell, Bru.", file=sys.stderr)
        exit(1)
    dir_ = Path(sys.argv[1])
    exit(run(dir_))
