from typing import Union
import io
import os
import sys

from pathlib import Path
import cairosvg

def render(content: str, target: Union[Path, str]):
    FONT_STYLE = "CaskaydiaCove Nerd Font Mono"
    TEXT_STYLE = f"font-family:'{FONT_STYLE}';"
    TEXT_TEMPLATE = (
        '    <text x="{}" y="{}" font-size="11pt" xml:space="preserve" '
             'fill="#00FFFF" '
             'style="' + TEXT_STYLE + '">{}</text>\n')
    svg_file = io.StringIO()
    # -inkscape-font-specification:'CaskaydiaCove Nerd Font Mono';"
    w=673
    h=768/1366*w
    svg_file.write(f'<svg width="{w}px" height="{h}px">\n')
    svg_file.write(f'    <rect width="{w}px" height="{h}px"/>\n')
    for i, line in enumerate(content.split('\n')):
        # Fugly fix for monospace
        for j in range(min(79, len(line))):
            if line[j] == " ":
                continue
            svg_file.write(
                TEXT_TEMPLATE.format(1+(w-2)/79*j, 17*(i+1), line[j]))
    svg_file.write('</svg>')
    svg_file.seek(0)
    # cairosvg.svg2png(file_obj=svg_file, write_to=str(target), scale=4)
    svg_target=str(target)+".svg"
    with open(svg_target, "w") as outf:
        svg_file.seek(0)
        outf.write(svg_file.read())
    png_target=str(target)+".png"
    os.system(f"inkscape \"{svg_target}\" -o \"{png_target}\" "
               "--export-width=1366 --export-height=768")
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
