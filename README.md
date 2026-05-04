# PyMOL Workbench

An integrated GUI toolkit for protein visualization and pocket analysis in PyMOL.

PyMOL Workbench wraps PyMOL's most-used functionality into an accessible three-tab dialog, enabling researchers and students to produce publication-quality figures and perform binding pocket analysis without relying on command-line workflows.

Developed at the Virginia Tech Department of Biochemistry by Sibi Mallesan, Jonathan Briganti, and Dr. Anne Brown.

## Requirements

PyMOL 2.x

## Installation

1. Install fpocket (for Pocket Analysis)

`__conda install -c conda-forge fpocket__`

2. Download the repository as a ZIP: Code → Download ZIP
[Download ZIP](https://github.com/Pymol-Scripts/pymol2-demo-plugin/archive/master.zip)
and install with PyMOL's plugin manager
(Plugin → Plugin Manger → Install New Plugin → Install from local file).

3. Launch
After installation, the plugin is accessible from PyMOL's menu:
Plugin → SibiPlugin

## Plugin files

* [\_\_init\_\_.py](__init__.py): Entry point, provides the `__init_plugin__` function which adds an entry to PyMOL's plugin menu.
* [demowidget.ui](demowidget.ui): Graphical user interface file, created with [Qt Designer](http://doc.qt.io/qt-5/qtdesigner-manual.html)

## Features

Visual Controls

One-click publication-ready style presets (Sibi Style, Dr. Brown Style)
Color picker with 50+ colors including a dedicated Brown Lab palette
Per-element color locking (N = blue, O = red, S = yellow always preserved)
Selection-aware coloring — color a ligand independently from the protein
Global transparency slider across all representations simultaneously

Pocket Analysis

Integrated fpocket binding pocket detection
Pockets ranked by druggability score
Per-pocket metrics: volume, hydrophobicity, polarity, alpha sphere count
Surface coloring by pocket rank
One-click docking box generation (AutoDock / Vina–compatible .txt output)
CSV export of pocket results

Advanced Visual Controls

Representation buttons (Cartoon, Surface, Sticks, Spheres, Mesh, Dots, Putty, Hide)
with per-object, per-chain, or selection targeting
Ray trace modes: Standard, Photorealistic + AO, Black Ink Outline, Toon/Quantized
Lighting presets: Flat, Soft Studio, Dramatic, Hard Scientific
Color by property: B-factor, chain, secondary structure, hydrophobicity (Kyte-Doolittle), rainbow, element
Cartoon quality controls: smoothness, loop/tube/helix radius
Depth & fog controls with transparent background export
H-bond visualization with adjustable distance cutoff
Export / Render panel with 1×, 2×, 4×, and custom resolution ray tracing

## License

[BSD-2-Clause](LICENSE)

(c) Schrodinger, Inc.
