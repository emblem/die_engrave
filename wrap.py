import itertools
import math
import numpy as np

from pygcode import Line, GCode, Machine, Position
import pygcode
from math import sin, cos

center_x = -1.25 / 2
#center_y = -1.25 / 2
center_y= 0

wrap_dir = 'Y'

# center_x = 0
radius = 4.409 / 2


def wrap_coords(gcode: GCode):
    if gcode.modal_group == pygcode.GCodeMotion.modal_group:
        x = gcode.params['X'].value
        y = gcode.params['Y'].value
        z = gcode.params['Z'].value

        if wrap_dir == 'X':
            angle = (x - center_x) / radius
            new_x = sin(angle) * radius + center_x
            new_y = y
        else:
            angle = (y - center_y) / radius
            new_x = x
            new_y = sin(angle) * radius + center_y

        new_z = (cos(angle) - 1) * radius + z

        gcode.params['X'] = pygcode.Word('X', new_x)
        gcode.params['Y'] = pygcode.Word('Y', new_y)
        gcode.params['Z'] = pygcode.Word('Z', new_z)

    return gcode


def as_vec(gpos):
    return np.array([gpos.values['X'], gpos.values['Y'], gpos.values['Z']])


max_seg_len = .005


def subdivide_moves(block: pygcode.Block, start_pos: pygcode.Position, end_pos):
    blocks = []
    non_move_codes = []
    for code in block.gcodes:
        if code.modal_group != pygcode.GCodeMotion.modal_group or start_pos is None:
            # print("NoSub: ", code)
            non_move_codes.append(code)
        else:
            p0 = as_vec(start_pos)
            p1 = as_vec(end_pos)
            move_len = np.linalg.norm(p0 - p1)
            steps = max(math.floor(move_len / max_seg_len), 2)
            for i in range(1, steps):
                u = float(i) / (steps - 1)
                pos = p1 * u + p0 * (1 - u)
                new_block = pygcode.Block()
                new_block.gcodes.append(pygcode.GCodeLinearMove(code.word_key, X=pos[0], Y=pos[1], Z=pos[2]))
                blocks.append(new_block)

    for block in blocks:
        block.gcodes.extend(non_move_codes)
    if len(blocks) == 0:
        blocks = [block]
    return blocks


# input = 'auk.ngc'
# output = 'wrapped_auk.ngc'

#jobs = [('Test-Pattern.ngc', 'Test-Pattern-Wrapped.ngc'),
#        ('Test-Pattern_v_clean.ngc', 'Test-Pattern_v_clean-Wrapped.ngc')]



postfix = ["", "_v_clean", "_clean"]
#prefix = ["silver", "pigeon", "red"]
#prefix = ["brown_rat", "coyote", "crow", "groundhog", "raccoon", "red_fox", "squirrel", "whitetail"]
prefix = ["elk_reg", "chimney_swift"]
inputs = ["".join(tup) for tup in itertools.product(prefix, postfix)]
jobs = [(name + ".ngc", name + "-wrapped.ngc") for name in inputs]


def main():
    for job in jobs:
        with open(job[0], 'r') as fh, open(job[1], 'w') as out_fh:
            print("Writing:", job[1])
            m_orig = Machine()
            start_pos = Position(axes=['X', 'Y', 'Z'], Z=1)
            m_orig.pos = start_pos
            last_pos = None
            for line_text in fh.readlines():
                line = Line(line_text)
                m_orig.process_block(line.block)
                pos = m_orig.pos
                blocks = subdivide_moves(line.block, last_pos, pos)
                [wrap_coords(code) for block in blocks for code in block.gcodes]
                [out_fh.write(str(block) + '\n') for block in blocks]
                last_pos = pos


main()
