# ////////////////////////////////////////////////////////////////
# mouse centered // randomly spawns grid-aligned isometric cubes in a muted purple ASK color palette
# cubes spawn in a radius centered around mouse cursor
# ////////////////////////////////////////////////////////////////
# Copyright 2025 Andrew S Klug // ASK
# ////////////////////////////////////////////////////////////////
# Licensed under the Apache License, Version 2.0 (the "License"); this file may not be used except in compliance with the License, a copy of which is available at http://www.apache.org/licenses/LICENSE-2.0
# ////////////////////////////////////////////////////////////////
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
# ////////////////////////////////////////////////////////////////
# refactored/adapted from p5.js >> https://editor.p5js.org/asymptoticSystemKey/sketches/B1fxc_4K2
# ////////////////////////////////////////////////////////////////

# ////////////////////////////////////////////////////////////////
#  quick‑start
#
#  1/ create a fresh environment (conda or venv) with Python 3.10+
#  2/ install py5’s pre‑release build (needed for Processing‑4 core)
#
#      # conda example
#      conda create -n py5env python=3.10 openjdk=17 -c conda-forge -y
#      conda activate py5env
#      pip install --upgrade pip wheel setuptools
#      pip install --pre py5         # grab the latest py5 nightly
#
#  3/ run the sketch:
#      python isometric_cubes_v2.py
#
#  4/ click anywhere in the window >> PNG output saved beside the script
# ////////////////////////////////////////////////////////////////

import math, random
import os 
import pathlib
from datetime import datetime
import py5

# ////////////////////////////////////////////////////////////////
# globals (mutated later)
# ////////////////////////////////////////////////////////////////

colors_ASK     = []   # master palette >> filled in "setup"
background_ASK = None # translucent lavender background color
stroke_color   = None # thin line color for cube edges
grid_unit      = 0    # size of grid cell >> set in "settings"
mouse_radius   = 0    # range around mouse position for cubes to spawn >> set in "settings"


# ////////////////////////////////////////////////////////////////
# py5 scaffolding
# ////////////////////////////////////////////////////////////////

def settings():
    # called once, before py5 initialises its Java back‑end
    # use this to set the canvas size
    # anything else that needs py5’s runtime goes in "setup"
    
    global grid_unit

    width4K = 3840 // 2             # half‑4K width >> 1920 px
    height  = int(width4K * 9 / 16) # 16:9 aspect ratio

    py5.size(width4K, height)       # create the canvas

    grid_unit = width4K / 32        # size of grid cell

    mouse_radius = 3                # range within which cubes may spawn // measured in grid_units, around mouse position


def setup():
    # build the color palette + paint the first frame
    # runs once after the Java VM is ready
    
    global colors_ASK, background_ASK, stroke_color

    # ////////////////////////////////////////////////////////////////
    # ASK color palette
    # ////////////////////////////////////////////////////////////////

    white      = py5.color(255, 255, 255)
    lavender5  = py5.color(226, 211, 240)   # warm lavender 5   // light
    lavender1  = py5.color(193, 154, 216)   # warm lavender 1   // mid
    lavender4  = py5.color(174, 135, 194)   # warm lavender 4   // dark
    lavender2  = py5.color(84, 77, 93)      # smokey lavender 2 // stroke

    # ASK color palette with relative frequencey weights
    colors_ASK = (
        [white]     * 20 +
        [lavender5] * 24 +
        [lavender1] *  6 +
        [lavender4] * 20
    )

    # set stroke and background colors
    stroke_color   = lavender2
    background_ASK = lavender5

    # paint background once – subsequent frames draw on top (no clear)
    py5.background(background_ASK)


# ////////////////////////////////////////////////////////////////
# draw loop
# ////////////////////////////////////////////////////////////////

def draw():
    # Called ~60 times per second
    # Each frame >> pick a random color+opacity, pick a grid‑aligned position+size, then draw one new isometric cube

    # 1/ choose random fill color + opacity
    base_color = random.choice(colors_ASK)     # pick from palette
    alpha       = py5.random(3, 7) * 32        # 96‥224 // semi‑opaque

    fill_color  = py5.color(py5.red(base_color),
                            py5.green(base_color),
                            py5.blue(base_color),
                            alpha)

    # 2/ random grid‑aligned position, within within +/- mouse_radius cells of current mouse position
    # grid spacing – x is compressed by cos(30°) in iso‑projection
    col_width   = grid_unit * math.cos(math.radians(30))

    # convert the current mouse position (pixels) to grid indices // centre_col + centre_row represent the grid cell under the cursor
    centre_col  = round(py5.mouse_x / col_width)
    centre_row  = round(py5.mouse_y / grid_unit)
    
    # randomly offset mouse position within +/- mouse_radius grid cells
    # we stay in grid coordinates to preserve alignment
    col = random.randint(centre_col - mouse_radius, centre_col + mouse_radius)
    row = random.randint(centre_row - mouse_radius, centre_row + mouse_radius)

    # convert back to pixel coordinates // still perfectly aligned
    x = col * col_width
    y = row * grid_unit

    # 3/ random radius (size) of cube
    r_grid_units = math.floor(py5.random(1, 6))      # 1–5 >> inclusive of 1, less than 6
    r            = r_grid_units * grid_unit / 4      # quarter‑grid_units

    # 4/ draw the cube
    IsometricCube(x, y, r, stroke_color, fill_color).show()


# ////////////////////////////////////////////////////////////////
# IsometricCube class
# ////////////////////////////////////////////////////////////////

class IsometricCube:
    # draws an isometric cube on an isometric grid

    def __init__(self, x, y, radius, stroke_col, fill_col):
        # store everything
        self.x, self.y, self.r = x, y, radius
        self.stroke_col = stroke_col
        self.fill_col = fill_col

    # ////////////////////////////////////////////////////////////////
    # rendering
    # ////////////////////////////////////////////////////////////////

    def show(self):
        # render the cube at (x, y) with current style

        py5.fill(self.fill_col)

        # outer petals (triangles)
        for i in range(6):
            # two angles per triangle >> −30° and +30° offset from spoke
            a1 = math.radians(-30 + i * 60)
            a2 = math.radians( 30 + i * 60)

            # three vertices >> centre, then two points on circle radius r
            x1, y1 = self.x, self.y
            x2, y2 = self.x + self.r * math.cos(a1), self.y + self.r * math.sin(a1)
            x3, y3 = self.x + self.r * math.cos(a2), self.y + self.r * math.sin(a2)

            py5.no_stroke()                     # fill‑only face
            py5.triangle(x1, y1, x2, y2, x3, y3)

            # edge lines
            py5.stroke(self.stroke_col)
            py5.line(x2, y2, x3, y3)

        # inner spokes to achieve illusion of isometric depth
        for i in range(3):
            a  = math.radians(30 + i * 120)
            x2 = self.x + self.r * math.cos(a)
            y2 = self.y - self.r * math.sin(a)  # minus flips axis
            py5.line(self.x, self.y, x2, y2)


# ////////////////////////////////////////////////////////////////
# save output PNG on mouse click
# ////////////////////////////////////////////////////////////////

def mouse_pressed():
    # save the current frame as a PNG output when user clicks
    # outputs saved to sibling folder "isometric-cubes-ASK-outputs"
    # filename format >> isometric_cubes_vX-YYYY-MM-DD-HHMMSS-#####.png

    # 1/ current script filename
    script_name = pathlib.Path(__file__).stem
    
    # 2/ datetime stamp
    datetime_stamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")

    # 3/ build output folder path
    script_dir = pathlib.Path(__file__).parent                # .../isometric-cubes-ASK
    parent_dir = script_dir.parent                            # .../2025 studioASK/13 python
    output_dir = parent_dir / "isometric-cubes-ASK-outputs" 

    # 5/ make sure that output folder exists // create it if necessary
    output_dir.mkdir(parents=True, exist_ok=True)

    # 6/ get current five‐digit frame count
    frame_count = py5.frame_count                                             
    frame_str = f"{frame_count:05d}"

    # 7/ construct final filename >> "isometric_cubes_vX-YYYY-MM-DD-HHMMSS-#####.png"
    filename = f"{script_name}-{datetime_stamp}-{frame_str}.png"

    # 8/ full path to save
    save_path = output_dir / filename

    # 9/ finally, save output PNG
    py5.save_frame(str(save_path))


# ////////////////////////////////////////////////////////////////
# window resize
# ////////////////////////////////////////////////////////////////

def window_resized():
    # keep the sketch responsive by matching the new window size
    py5.resize_canvas(py5.window_width, py5.window_height)


# ////////////////////////////////////////////////////////////////
# entry point
# ////////////////////////////////////////////////////////////////

if __name__ == "__main__":
    py5.run_sketch()
