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
Mounting LED light pods salvaged from a dead Aurum motion-sensing security light
onto an extrusion beam
"""

import cadquery as cq

# Extrusion beam I want to clamp onto Bridgeport ram
extrusion_unit = 25.4 # 25.4mm = extrusion based on 1" squares
extrusion_height_units = 1
extrusion_depth_units = 1
extrusion_height = extrusion_height_units * extrusion_unit
extrusion_depth = extrusion_depth_units * extrusion_unit

# Standard distance available when using default fastener. If design is
# thicker than this value, a longer bolt will be needed.
extrusion_fastener_distance = 6
extrusion_fastener_diameter = 6.5

# Aurum pod is designed to mount on a sheet metal enclosure so depth is limited
aurum_thread_depth = 4.5

# Aurum pod mount has a small tab to lock rotation if desired. Or make the
# mount point diameter large enough to let the tab spin freely.
aurum_mount_diameter = 20
aurum_mount_tab_width = 3
aurum_mount_tab_depth = 1.5
aurum_free_spin_diameter = aurum_mount_diameter + aurum_mount_tab_depth

def aurum_led_mount():
    main_profile = (
        cq.Workplane("YZ")
        .lineTo(extrusion_depth, 0)
        .lineTo(extrusion_depth, extrusion_fastener_distance)
        .lineTo(aurum_thread_depth-extrusion_fastener_distance, extrusion_fastener_distance)
        .lineTo(aurum_thread_depth-extrusion_fastener_distance, extrusion_fastener_distance + aurum_free_spin_diameter*2)
        .lineTo(-extrusion_fastener_distance,                   extrusion_fastener_distance + aurum_free_spin_diameter*2)
        .lineTo(-extrusion_fastener_distance,                  -extrusion_height)
        .lineTo(0,                                             -extrusion_height)
        .close()
        .extrude(aurum_free_spin_diameter+extrusion_fastener_distance, both=True)
    )

    # Fillet not to exceed radius of extrusion beam
    main_profile = main_profile.faces(">Z[1]").edges("<Y").fillet(1)

    # Fillet to help support LEd pod
    main_profile = main_profile.faces("<Z[1]").edges("<Y").fillet(5)

    # Add side support plate
    side_support_plate = (
        cq.Workplane("YZ")
        .transformed(offset=cq.Vector(0,0,aurum_free_spin_diameter))
        .lineTo(extrusion_depth, 0)
        .lineTo(extrusion_depth, extrusion_fastener_distance)
        .lineTo(aurum_thread_depth-extrusion_fastener_distance, extrusion_fastener_distance + aurum_free_spin_diameter*2)
        .lineTo(-extrusion_fastener_distance,                   extrusion_fastener_distance + aurum_free_spin_diameter*2)
        .lineTo(-extrusion_fastener_distance,                   0)
        .close()
        .extrude(extrusion_fastener_distance)
    )
    mount_volume = main_profile + side_support_plate

    # Cut holes
    mount_volume = mount_volume - (
        # Mounting LED
        cq.Workplane("XZ")
        .transformed(offset=cq.Vector(
            0,
            extrusion_fastener_distance + aurum_free_spin_diameter,
            -aurum_thread_depth+extrusion_fastener_distance))
        .circle(aurum_free_spin_diameter/2)
        .extrude(aurum_thread_depth)
    ) - (
        # Top extrusion fastener
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(0, extrusion_unit/2, 0))
        .circle(extrusion_fastener_diameter/2)
        .extrude(extrusion_fastener_distance)
    ) - (
        # Front extrusion fastener
        cq.Workplane("XZ")
        .transformed(offset=cq.Vector(0, -extrusion_unit/2, 0))
        .circle(extrusion_fastener_diameter/2)
        .extrude(extrusion_fastener_distance)
    )

    mount_volume = mount_volume.faces("<X").edges(">Z").fillet(aurum_free_spin_diameter+extrusion_fastener_diameter)

    # Fillets to reduce print bed adhesion issues
    mount_volume = mount_volume.faces("<Z").edges("|X").fillet(extrusion_fastener_diameter * 0.4)
    mount_volume = mount_volume.faces(">Z").edges("<Y").fillet(extrusion_fastener_diameter * 0.4)
    mount_volume = mount_volume.faces(">Y").edges("<Z").fillet(extrusion_fastener_diameter * 0.4)

    return mount_volume

if show_object:
    show_object(aurum_led_mount(), options={"color":"blue", "alpha":0.5})
