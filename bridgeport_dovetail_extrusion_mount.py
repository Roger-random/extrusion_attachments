"""
MIT License

Copyright (c) 2025 Roger Cheng

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
Mount a 2" x 2" extrusion beam onto the ram dovetail of a Bridgeport mill

https://www.mcmaster.com/products/extrusions/t-slotted-framing-and-fittings~/t-slotted-framing-rail-profile~quad/system-of-measurement~inch/t-slotted-framing-rails-4/quad-rail-profile-style~quad/rail-width~2/

I do not own a Bridgeport mill, only infrequently access to one. So getting the
dimensions correct took several tries hence all the "estimated", "shift", and
"adjustment" values in dimension math.
"""

# Original estimate values
estimated_dovetail_base_width = 133.35
dovetail_height = 25
estimated_dovetail_top_width = estimated_dovetail_base_width - dovetail_height*2

# Bridgeport dovetail is not 45 degrees! Adjust as per measurement against
# a test print with incorrect 45 degree dovetail.
lr_shift_adjustment = 2.5
dovetail_base_width = estimated_dovetail_base_width + 10 - 6 - lr_shift_adjustment
dovetail_top_width = estimated_dovetail_top_width + 10 - lr_shift_adjustment

# Extrusion beam I want to clamp onto Bridgeport ram
extrusion_unit = 25.4 # 25.4mm = extrusion based on 1" squares
extrusion_height_units = 2
extrusion_depth_units = 1
extrusion_height = extrusion_height_units * extrusion_unit
extrusion_depth = extrusion_depth_units * extrusion_unit

# Standard distance available when using default fastener. If design is
# thicker than this value, a longer bolt will be needed.
extrusion_fastener_distance = 6
extrusion_fastener_diameter = 6.5

# Placeholder built from measured dimensions of Bridgeport mill ram dovetail.
# Might be off by a tiny bit so design will need to be flexible.
def dovetail_placeholder():
    dovetail_half = (
        cq.Workplane("YZ")
        .lineTo(dovetail_base_width/2, 0)
        .lineTo(dovetail_top_width/2, dovetail_height)
        .lineTo(0, dovetail_height)
        .close()
        .extrude(extrusion_unit * 1.5, both=True)
    ).faces("<Z").edges(">Y").chamfer(2)

    return (
        dovetail_half
        + dovetail_half.mirror("XZ")
    )

def extrusion_beam_placeholder():
    return (
        cq.Workplane("XZ")
        .rect(extrusion_depth, extrusion_height)
        .extrude(100, both=True)
    )

def test_fit_plate_01():
    """
    This was the first plate I printed based on my first set of measurements.
    There were significant errors but since I had a physical unit on hand I
    used it as reference for further corrections. In order to compare against
    my physical print as reference, I'm preserving the CadQuery code behind it.
    """
    test_dovetail_base_width = 133.35
    beam_top_corner_x = test_dovetail_base_width/2 + 5
    plate_claw_thickness = 20
    plate_claw_height = 25

    test_beam_height = 20

    plate_half = (
        cq.Workplane("YZ")
        .lineTo(beam_top_corner_x, 0)
        .lineTo(beam_top_corner_x - plate_claw_height                       , plate_claw_height)
        .lineTo(beam_top_corner_x - plate_claw_height + plate_claw_thickness, plate_claw_height)
        .lineTo(beam_top_corner_x                     + plate_claw_thickness, 0)
        .lineTo(beam_top_corner_x                                           , -test_beam_height)
        .lineTo(0                                                           , -test_beam_height)
        .close()
        .extrude(6)
    )

    plate = plate_half + plate_half.mirror("XZ")

    return plate.translate((25.4,0,0))

def test_fit_plate():
    """
    Plate to test updated dimensions derived from measuring errors against plate #1
    """
    plate_width = 10
    plate_thickness = 3

    plate_half = (
        cq.Workplane("YZ")
        .lineTo(dovetail_base_width/2              , 0)
        .lineTo(dovetail_top_width/2               , dovetail_height)
        .lineTo(dovetail_top_width/2  + plate_width, dovetail_height)
        .lineTo(dovetail_base_width/2 + plate_width, 0)
        .lineTo(dovetail_base_width/2              , -plate_width)
        .lineTo(0                                  , -plate_width)
        .close()
        .extrude(plate_thickness)
    )

    plate = plate_half + plate_half.mirror("XZ")

    return plate.translate((extrusion_depth/2, 0, 0))

simple_slot_width = 5

def simple_half_base():
    claw_width = 10
    mount_half = (
        cq.Workplane("YZ")
        .lineTo(dovetail_base_width/2             , 0)
        .lineTo(dovetail_top_width/2              , dovetail_height)
        .lineTo(dovetail_top_width/2  + claw_width, dovetail_height)
        .lineTo(dovetail_base_width/2 + claw_width, 0)
        .lineTo(dovetail_base_width/2 + claw_width + extrusion_unit, 0)
        .lineTo(dovetail_base_width/2 + claw_width + extrusion_unit, -extrusion_fastener_distance)
        .lineTo(0                                 , -extrusion_fastener_distance)
        .close()
        .extrude(extrusion_depth/2, both=True)
    )

    fastener_hole_drill = (
        cq.Workplane("XY")
        .circle(extrusion_fastener_diameter/2)
        .extrude(-extrusion_fastener_distance)
    )

    for h in range(extrusion_depth_units):
        mount_half = (
            mount_half
            -fastener_hole_drill.translate((
                extrusion_depth/2 - extrusion_unit/2 - extrusion_unit * h,
                dovetail_base_width/2 + claw_width + extrusion_unit/2))
            -fastener_hole_drill.translate((
                extrusion_depth/2 - extrusion_unit/2 - extrusion_unit * h,
                simple_slot_width/2 + extrusion_unit/2))
        )

    mount_half = mount_half.faces(">Y").edges("|X").fillet(extrusion_fastener_distance * 0.4)
    mount_half = mount_half.faces(">Z").edges("|X").fillet(extrusion_fastener_distance * 0.4)

    return mount_half

def simple_one_piece():
    """
    The simplest single-piece design without any provision for adjustment.
    Will only work if all dimensions are correct!
    """
    mount_half = simple_half_base()
    mount = mount_half + mount_half.mirror("XZ")

    return mount

def simple_two_pieces():
    """
    Tiny bit more flexible than one-piece, as distance between claws can be
    adjusted. But the claw profile is still fixed.
    """
    mount_half = simple_half_base()

    simple_slot = (
        cq.Workplane("YZ")
        .transformed(offset=cq.Vector(0, -extrusion_fastener_distance/2,0))
        .rect(simple_slot_width, extrusion_fastener_distance)
        .extrude(extrusion_depth, both=True)
    )

    mount_half = mount_half - simple_slot

    mount_half = mount_half.faces("<Y").edges("|X").fillet(extrusion_fastener_distance * 0.4)

    return mount_half

if show_object:
    show_object(dovetail_placeholder(), options={"color":"red", "alpha":0.5})
    show_object(extrusion_beam_placeholder()
        .translate((0,0,-extrusion_height/2 - extrusion_fastener_distance)), options={"color":"white", "alpha":0.5})
    #show_object(simple_one_piece(), options={"color":"blue", "alpha":0.5})
    show_object(simple_two_pieces(), options={"color":"green", "alpha":0.5})
