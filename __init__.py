'''
PyMOL Demo Plugin

The plugin resembles the old "Rendering Plugin" from Michael Lerner, which
was written with Tkinter instead of PyQt.

(c) Schrodinger, Inc.

License: BSD-2-Clause
'''

from __future__ import absolute_import
from __future__ import print_function

# Avoid importing "expensive" modules here (e.g. scipy), since this code is
# executed on PyMOL's startup. Only import such modules inside functions.

import os
import subprocess
import tempfile
import shutil


def __init_plugin__(app=None):
    '''
    Add an entry to the PyMOL "Plugin" menu
    '''
    from pymol.plugins import addmenuitemqt
    addmenuitemqt('SibiPlugin', run_plugin_gui)


# global reference to avoid garbage collection of our dialog
dialog = None


def run_plugin_gui():
    '''
    Open our custom dialog
    '''
    global dialog

    if dialog is None:
        dialog = make_dialog()

    dialog.show()


def make_dialog():
    # entry point to PyMOL's API
    from pymol import cmd

    # pymol.Qt provides the PyQt5 interface, but may support PyQt4
    # and/or PySide as well
    from pymol.Qt import QtWidgets
    from pymol.Qt.utils import loadUi

    # create a new Window
    dialog = QtWidgets.QDialog()

    # populate the Window from our *.ui file which was created with the Qt Designer
    uifile = os.path.join(os.path.dirname(__file__), 'demowidget.ui')
    form = loadUi(uifile, dialog)

    WATER_RESNAMES = {"HOH", "WAT", "DOD", "H2O", "OH2"}

    def get_residues_to_remove(parent_widget):
        try:
            model = cmd.get_model("hetatm or solvent")
            atoms = model.atom
        except Exception as e:
            print(f"[SibiPlugin] Could not enumerate heteroatoms: {e}")
            return []

        resn_set = sorted({a.resn.strip().upper() for a in atoms if a.resn.strip()})
        if not resn_set:
            return []

        dlg = QtWidgets.QDialog(parent_widget)
        dlg.setWindowTitle("Remove molecules before styling")
        dlg.setMinimumWidth(350)

        outer_layout = QtWidgets.QVBoxLayout(dlg)

        info_label = QtWidgets.QLabel(
            "Hydrogens will always be removed.\n"
            "Select additional molecules to remove before applying the style:"
        )
        info_label.setWordWrap(True)
        outer_layout.addWidget(info_label)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(200)
        scroll_content = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(4)

        checkboxes = {}
        for resn in resn_set:
            cb = QtWidgets.QCheckBox(resn)
            cb.setChecked(resn in WATER_RESNAMES)
            scroll_layout.addWidget(cb)
            checkboxes[resn] = cb

        scroll.setWidget(scroll_content)
        outer_layout.addWidget(scroll)

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(dlg.accept)
        button_box.rejected.connect(dlg.reject)
        outer_layout.addWidget(button_box)

        result = dlg.exec_()
        if result != QtWidgets.QDialog.Accepted:
            return None

        return [resn for resn, cb in checkboxes.items() if cb.isChecked()]

    def reset_style_defaults():
        cmd.set("cartoon_fancy_helices", 0)
        cmd.set("cartoon_smooth_loops", 0)
        cmd.set("cartoon_flat_sheets", 1)
        cmd.set("cartoon_loop_radius", 0.2)
        cmd.set("ambient", 0.1)
        cmd.set("direct", 0.45)
        cmd.set("specular", 0.5)
        cmd.set("depth_cue", 1)
        cmd.set("ray_trace_mode", 0)
        cmd.set("ambient_occlusion_mode", 0)
        cmd.set("ambient_occlusion_scale", 25)
        cmd.set("ambient_occlusion_smooth", 9)

    def update_protein_color_button(display_name):
        _, rgb = get_color(display_name)
        r, g, b = rgb
        text_color = "black" if (r * 299 + g * 587 + b * 114) / 1000 > 128 else "white"
        form.ProteinColorButton.setText(display_name)
        form.ProteinColorButton.setStyleSheet(
            f"background-color: rgb({r},{g},{b}); color: {text_color};"
        )

    def apply_sibi_style():
        reset_style_defaults()
        cmd.bg_color("white")
        resns_to_remove = get_residues_to_remove(dialog)
        if resns_to_remove is None:
            return
        cmd.remove("hydro")
        for resn in resns_to_remove:
            cmd.remove(f"resn {resn}")
        cmd.color("magenta")
        update_protein_color_button("Magenta")
        cmd.color("blue",   "elem N")
        cmd.color("red",    "elem O")
        cmd.color("yellow", "elem S")
        cmd.color("blue",   "sele and elem N")
        cmd.color("red",    "sele and elem O")
        cmd.color("yellow", "sele and elem S")
        cmd.set("ray_shadows", 0)
        cmd.set("ray_trace_fog", 0)
        cmd.set("cartoon_side_chain_helper", "on")
        cmd.set("antialias_shader", 2)
        cmd.set("surface_quality", 1)
        cmd.set("line_smooth", 1)
        cmd.set("cartoon_sampling", 19)
        cmd.set("use_shaders", 1)
        cmd.set("cartoon_use_shader", 1)
        cmd.set("cartoon_nucleic_acid_as_cylinders", 1)
        cmd.set("stick_ball", 0)
        cmd.set("sphere_mode", 9)
        cmd.show("cartoon")
        cmd.hide("lines")

    def apply_brown_style():
        reset_style_defaults()
        cmd.bg_color("white")
        resns_to_remove = get_residues_to_remove(dialog)
        if resns_to_remove is None:
            return
        cmd.remove("hydro")
        for resn in resns_to_remove:
            cmd.remove(f"resn {resn}")
        cmd.color("firebrick")
        update_protein_color_button("Firebrick")
        cmd.color("blue",   "elem N")
        cmd.color("red",    "elem O")
        cmd.color("yellow", "elem S")
        cmd.color("blue",   "sele and elem N")
        cmd.color("red",    "sele and elem O")
        cmd.color("yellow", "sele and elem S")
        cmd.set("ray_shadows", 0)
        cmd.set("ray_trace_fog", 0)
        cmd.set("cartoon_side_chain_helper", "on")
        cmd.set("antialias_shader", 2)
        cmd.set("surface_quality", 1)
        cmd.set("line_smooth", 1)
        cmd.set("cartoon_sampling", 19)
        cmd.set("use_shaders", 1)
        cmd.set("cartoon_use_shader", 1)
        cmd.set("cartoon_nucleic_acid_as_cylinders", 1)
        cmd.set("stick_ball", 0)
        cmd.set("sphere_mode", 9)
        cmd.show("cartoon")
        cmd.hide("lines")
        # cartoon quality
        cmd.set("cartoon_fancy_helices", 1)
        cmd.set("cartoon_smooth_loops", 1)
        cmd.set("cartoon_flat_sheets", 1)
        cmd.set("cartoon_loop_radius", 0.3)
        # lighting
        cmd.set("ambient", 0.4)
        cmd.set("direct", 0.7)
        cmd.set("specular", 0.1)
        cmd.set("depth_cue", 0)
        # ray trace mode with ambient occlusion
        cmd.set("ray_trace_mode", 1)
        cmd.set("ambient_occlusion_mode", 1)
        cmd.set("ambient_occlusion_scale", 25)
        cmd.set("ambient_occlusion_smooth", 9)

    # map display name -> (pymol color name, RGB tuple)
    color_map = {
        # Basic
        "White":        ("white",       (255, 255, 255)),
        "Black":        ("black",       (0,   0,   0  )),
        "Gray":         ("gray",        (128, 128, 128)),
        "Silver":       ("silver",      (192, 192, 192)),
        # Reds
        "Red":          ("red",         (255, 0,   0  )),
        "Firebrick":    ("firebrick",   (178, 34,  34 )),
        "Salmon":       ("salmon",      (250, 128, 114)),
        "Raspberry":    ("raspberry",   (178, 0,   102)),
        "Warm Pink":    ("warmpink",    (252, 100, 97 )),
        # Greens
        "Green":        ("green",       (0,   255, 0  )),
        "TV Green":     ("tv_green",    (0,   204, 0  )),
        "Lime":         ("lime",        (128, 255, 0  )),
        "Greencyan":    ("greencyan",   (0,   255, 128)),
        "Forest":       ("forest",      (0,   85,  0  )),
        "Chartreuse":   ("chartreuse",  (128, 255, 0  )),
        # Blues
        "Blue":         ("blue",        (0,   0,   255)),
        "TV Blue":      ("tv_blue",     (51,  51,  255)),
        "Marine":       ("marine",      (0,   0,   128)),
        "Slate":        ("slate",       (102, 153, 204)),
        "Light Blue":   ("lightblue",   (173, 216, 230)),
        "Sky Blue":     ("skyblue",     (135, 206, 235)),
        "Purple Blue":  ("purpleblue",  (102, 51,  255)),
        # Yellows / Oranges
        "Yellow":       ("yellow",      (255, 255, 0  )),
        "TV Yellow":    ("tv_yellow",   (255, 204, 0  )),
        "Orange":       ("orange",      (255, 165, 0  )),
        "Gold":         ("gold",        (255, 215, 0  )),
        "Wheat":        ("wheat",       (245, 222, 179)),
        "Sand":         ("sand",        (210, 180, 140)),
        # Purples / Pinks
        "Purple":       ("purple",      (128, 0,   128)),
        "Violet":       ("violet",      (238, 130, 238)),
        "Pink":         ("pink",        (255, 192, 203)),
        "Hot Pink":     ("hotpink",     (255, 105, 180)),
        "Magenta":      ("magenta",     (255, 0,   255)),
        # Cyans
        "Cyan":         ("cyan",        (0,   255, 255)),
        "Aquamarine":   ("aquamarine",  (127, 255, 212)),
        "Teal":         ("teal",        (0,   128, 128)),
        "Deep Teal":    ("deepteal",    (0,   90,  90 )),
    }

    # Brown Lab colors (from Dr. Anne Brown, Virginia Tech publications)
    brown_lab_colors = {
        # Base
        "AB Gray":        ("gray",        (128, 128, 128)),
        "AB Dark Teal":   ("deepteal",    (0,   90,  90 )),
        "AB Red":         ("red",         (255, 0,   0  )),
        "AB Dark Red":    ("firebrick",   (178, 34,  34 )),
        "AB Orange":      ("orange",      (255, 165, 0  )),
        "AB Wheat":       ("wheat",       (245, 222, 179)),
        "AB Blue":        ("blue",        (0,   0,   255)),
        "AB Cyan":        ("cyan",        (0,   255, 255)),
        "AB Teal":        ("teal",        (0,   128, 128)),
        "AB Purple":      ("purple",      (128, 0,   128)),
        "AB Pink":        ("pink",        (255, 192, 203)),
        "AB Gold":        ("gold",        (255, 215, 0  )),
        "AB Green":       ("green",       (0,   255, 0  )),
        "AB Tan":         ("sand",        (210, 180, 140)),
        "AB Slate":       ("slate",       (102, 153, 204)),
        # Navy
        "AB Navy":        ("marine",      (0,   0,   128)),
        "AB Royal Blue":  ("0x4169e1",   (65,  105, 225)),
        "AB Steel Blue":  ("0x4682b4",   (70,  130, 180)),
        # Royal Purple
        "AB Royal Purple":("0x7851a9",   (120, 81,  169)),
        "AB Indigo":      ("0x4b0082",   (75,  0,   130)),
        "AB Plum":        ("0x8b008b",   (139, 0,   139)),
        "AB Orchid":      ("0xda70d6",   (218, 112, 214)),
        # Tans
        "AB Light Tan":   ("0xfff8dc",   (255, 248, 220)),
        "AB Dark Tan":    ("0xd2691e",   (210, 105, 30 )),
        "AB Sienna":      ("0xa0522d",   (160, 82,  45 )),
        # Golds
        "AB Dark Gold":   ("0xdaa520",   (218, 165, 32 )),
        "AB Bronze":      ("0xcd7f32",   (205, 127, 50 )),
        "AB Pale Gold":   ("0xeee8aa",   (238, 232, 170)),
    }

    def get_color(name):
        return color_map.get(name) or brown_lab_colors.get(name, ("white", (255, 255, 255)))

    def apply_ligand_color():
        if not form.YesLigandButton.isChecked():
            return
        if "sele" not in cmd.get_names("selections"):
            return
        pymol_color, _ = get_color(form.LigandColorButton.text())
        cmd.color(pymol_color, "sele")
        cmd.color("blue",   "sele and elem N")
        cmd.color("red",    "sele and elem O")
        cmd.color("yellow", "sele and elem S")

    def on_ligand_color_change(color_name):
        if not form.YesLigandButton.isChecked():
            return
        if "sele" not in cmd.get_names("selections"):
            return
        pymol_color, _ = get_color(color_name)
        cmd.color(pymol_color, "sele")
        cmd.color("blue",   "sele and elem N")
        cmd.color("red",    "sele and elem O")
        cmd.color("yellow", "sele and elem S")

    def on_color_change(color_name):
        pymol_color, _ = get_color(color_name)
        cmd.color(pymol_color)
        cmd.color("blue",   "elem N")
        cmd.color("red",    "elem O")
        cmd.color("yellow", "elem S")

    def open_color_picker(button, callback):
        from pymol.Qt import QtWidgets
        picker = QtWidgets.QDialog(dialog)
        picker.setWindowTitle("Pick a color")
        layout = QtWidgets.QVBoxLayout(picker)
        layout.setSpacing(4)
        cols = 6

        def make_color_grid(color_dict):
            grid_widget = QtWidgets.QWidget()
            grid = QtWidgets.QGridLayout(grid_widget)
            grid.setSpacing(4)
            for i, (name, (_, rgb)) in enumerate(color_dict.items()):
                r, g, b = rgb
                text_color = "black" if (r * 299 + g * 587 + b * 114) / 1000 > 128 else "white"
                btn = QtWidgets.QPushButton(name)
                btn.setFixedSize(90, 30)
                btn.setToolTip(name)
                btn.setStyleSheet(
                    f"background-color: rgb({r},{g},{b}); color: {text_color}; font-size: 10px;"
                )
                btn.clicked.connect(lambda _, n=name, rc=rgb: (
                    callback(n),
                    button.setText(n),
                    button.setStyleSheet(
                        f"background-color: rgb({rc[0]},{rc[1]},{rc[2]}); "
                        f"color: {'black' if (rc[0]*299+rc[1]*587+rc[2]*114)/1000 > 128 else 'white'};"
                    ),
                    picker.accept(),
                ))
                grid.addWidget(btn, i // cols, i % cols)
            return grid_widget

        def make_section(title, color_dict):
            group = QtWidgets.QGroupBox(title)
            group_layout = QtWidgets.QVBoxLayout(group)
            group_layout.setContentsMargins(4, 4, 4, 4)
            group_layout.addWidget(make_color_grid(color_dict))
            return group

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(580)
        scroll.setMaximumHeight(500)
        inner = QtWidgets.QWidget()
        inner_layout = QtWidgets.QVBoxLayout(inner)
        inner_layout.addWidget(make_section("General Colors", color_map))
        inner_layout.addWidget(make_section("Brown Lab Colors", brown_lab_colors))
        scroll.setWidget(inner)
        layout.addWidget(scroll)

        button.setEnabled(False)
        picker.exec_()
        button.setEnabled(True)

    def on_transparency_change(value):
        transparency = value / 99.0
        if form.YesLigandButton.isChecked() and "sele" in cmd.get_names("selections"):
            target = "all and not sele"
        else:
            target = "all"
        props = [
            "cartoon_transparency", "surface_transparency", "stick_transparency",
            "sphere_transparency",  "ribbon_transparency",  "mesh_transparency",
            "dash_transparency",    "dot_transparency",
        ]
        for obj in cmd.get_object_list():
            if cmd.count_atoms(f"{obj} and ({target})") == 0:
                continue
            for prop in props:
                cmd.set(prop, transparency, obj)

    # --- Pocket Analysis tab ---

    fpocket_output_dir = [None]  # mutable container to share across closures
    pocket_data = [{}]           # mutable container: dict keyed by pocket number

    pocket_colors = [
        "tv_red", "tv_orange", "tv_yellow", "tv_green", "tv_blue",
        "violet", "cyan", "salmon", "lime", "pink",
    ]

    def populate_object_dropdown():
        form.fpocketObjectDropdown.clear()
        for obj in cmd.get_object_list():
            form.fpocketObjectDropdown.addItem(obj)
        update_visible_chains_label()

    def update_visible_chains_label():
        obj = form.fpocketObjectDropdown.currentText()
        if not obj:
            form.fpocketVisibleChainsLabel.setText("")
            return
        visible_chains = [
            ch for ch in cmd.get_chains(obj)
            if cmd.count_atoms(f"{obj} and chain {ch} and visible and polymer") > 0
        ]
        if visible_chains:
            form.fpocketVisibleChainsLabel.setText(
                "Visible chains: " + ", ".join(visible_chains) + " — fpocket will analyze these"
            )
            form.fpocketVisibleChainsLabel.setStyleSheet("color: #226622; font-size: 10px;")
        else:
            form.fpocketVisibleChainsLabel.setText(
                "No visible chains — unhide chains in Advanced Visual Controls"
            )
            form.fpocketVisibleChainsLabel.setStyleSheet("color: #aa2222; font-size: 10px;")

    def run_fpocket():
        obj_name = form.fpocketObjectDropdown.currentText()
        if not obj_name:
            form.fpocketStatusLabel.setText("No object selected.")
            return

        fpocket_bin = shutil.which("fpocket")
        if not fpocket_bin:
            for candidate in [
                "/opt/anaconda3/bin/fpocket",
                "/opt/miniconda3/bin/fpocket",
                "/usr/local/bin/fpocket",
                "/usr/bin/fpocket",
                os.path.expanduser("~/anaconda3/bin/fpocket"),
                os.path.expanduser("~/miniconda3/bin/fpocket"),
            ]:
                if os.path.isfile(candidate):
                    fpocket_bin = candidate
                    break
        if not fpocket_bin:
            form.fpocketStatusLabel.setText("Error: fpocket not found on PATH.")
            return

        form.fpocketStatusLabel.setText("Running fpocket...")
        form.fpocketRunButton.setEnabled(False)
        form.fpocketResultsList.clear()

        tmp_dir = tempfile.mkdtemp()
        tmp_pdb = os.path.join(tmp_dir, obj_name + ".pdb")

        try:
            visible_sel = f"{obj_name} and visible and polymer"
            if cmd.count_atoms(visible_sel) == 0:
                form.fpocketStatusLabel.setText(
                    "No visible polymer atoms — unhide chains in Advanced Visual Controls first."
                )
                form.fpocketRunButton.setEnabled(True)
                return
            cmd.save(tmp_pdb, visible_sel)
            result = subprocess.run(
                [fpocket_bin, "-f", tmp_pdb],
                capture_output=True, text=True, cwd=tmp_dir
            )
            if result.returncode != 0:
                form.fpocketStatusLabel.setText("fpocket error: " + result.stderr.strip())
                return

            out_dir = os.path.join(tmp_dir, obj_name + "_out")
            fpocket_output_dir[0] = out_dir

            # parse pocket info file for all metrics
            info_file = os.path.join(out_dir, obj_name + "_info.txt")
            pockets = []
            pocket_data[0] = {}
            metric_keys = {
                "Druggability Score": "druggability",
                "Volume": "volume",
                "Small Molecule Binding Score": "area",
                "Hydrophobicity Score": "hydrophobicity",
                "Polarity Score": "polarity",
                "Number of Alpha Spheres": "alpha_spheres",
            }
            if os.path.exists(info_file):
                current_pocket = None
                current_metrics = {}
                with open(info_file) as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("Pocket"):
                            if current_pocket is not None:
                                pocket_data[0][current_pocket] = current_metrics
                                pockets.append((current_pocket, current_metrics.get("druggability", "N/A")))
                            current_pocket = line.split()[1].rstrip(":")
                            current_metrics = {}
                        else:
                            for label, key in metric_keys.items():
                                if label in line:
                                    current_metrics[key] = line.split(":")[-1].strip()
                    if current_pocket is not None:
                        pocket_data[0][current_pocket] = current_metrics
                        pockets.append((current_pocket, current_metrics.get("druggability", "N/A")))

            if not pockets:
                form.fpocketStatusLabel.setText("No pockets detected.")
            else:
                pockets.sort(key=lambda x: float(x[1]) if x[1] != "N/A" else -1, reverse=True)
                form.fpocketStatusLabel.setText(f"Found {len(pockets)} pocket(s).")
                for num, score in pockets:
                    form.fpocketResultsList.addItem(f"Pocket {num}  |  Druggability: {score}")

        except Exception as e:
            form.fpocketStatusLabel.setText("Error: " + str(e))
        finally:
            form.fpocketRunButton.setEnabled(True)

    def load_pocket(pocket_num, color):
        out_dir = fpocket_output_dir[0]
        if not out_dir:
            return
        pocket_pdb = os.path.join(out_dir, "pockets", f"pocket{pocket_num}_atm.pdb")
        if not os.path.exists(pocket_pdb):
            form.fpocketStatusLabel.setText(f"Pocket {pocket_num} file not found.")
            return
        pocket_obj = f"pocket_{pocket_num}"
        cmd.load(pocket_pdb, pocket_obj)
        cmd.hide("everything", pocket_obj)
        cmd.show("surface", pocket_obj)
        cmd.color(color, pocket_obj)
        cmd.set("transparency", 0.3, pocket_obj)

    def on_pocket_selected(idx):
        if idx < 0:
            return
        item = form.fpocketResultsList.item(idx)
        if not item:
            return
        pocket_num = item.text().split()[1]
        metrics = pocket_data[0].get(pocket_num, {})
        lines = [
            f"Pocket {pocket_num}",
            "─" * 30,
            f"Druggability Score:   {metrics.get('druggability', 'N/A')}",
            f"Volume:               {metrics.get('volume', 'N/A')}",
            f"Area:                 {metrics.get('area', 'N/A')}",
            f"Hydrophobicity:       {metrics.get('hydrophobicity', 'N/A')}",
            f"Polarity Score:       {metrics.get('polarity', 'N/A')}",
            f"Alpha Spheres:        {metrics.get('alpha_spheres', 'N/A')}",
        ]
        form.fpocketDetailPanel.setPlainText("\n".join(lines))

    def on_pocket_color_change(color_name):
        pymol_color, _ = get_color(color_name)
        selected = form.fpocketResultsList.currentItem()
        if not selected:
            return
        pocket_num = selected.text().split()[1]
        pocket_obj = f"pocket_{pocket_num}"
        if pocket_obj in cmd.get_object_list():
            cmd.color(pymol_color, pocket_obj)

    def show_selected_pocket():
        selected = form.fpocketResultsList.currentItem()
        if not selected:
            form.fpocketStatusLabel.setText("No pocket selected in list.")
            return
        pocket_num = selected.text().split()[1]
        pymol_color, _ = get_color(form.fpocketPocketColorButton.text())
        load_pocket(pocket_num, pymol_color)

    def show_all_pockets():
        if fpocket_output_dir[0] is None:
            form.fpocketStatusLabel.setText("Run fpocket first.")
            return
        for i in range(form.fpocketResultsList.count()):
            pocket_num = form.fpocketResultsList.item(i).text().split()[1]
            color = pocket_colors[i % len(pocket_colors)]
            load_pocket(pocket_num, color)

    def export_to_csv():
        if form.fpocketResultsList.count() == 0:
            form.fpocketStatusLabel.setText("No results to export.")
            return

        from pymol.Qt import QtWidgets
        import csv

        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            dialog, "Save pocket results", "", "CSV Files (*.csv)"
        )
        if not path:
            return

        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Pocket", "Druggability Score"])
            for i in range(form.fpocketResultsList.count()):
                text = form.fpocketResultsList.item(i).text()
                parts = text.split("|")
                pocket_num = parts[0].strip().split()[-1]
                score = parts[1].strip().split(":")[-1].strip()
                writer.writerow([pocket_num, score])

        form.fpocketStatusLabel.setText(f"Exported to {os.path.basename(path)}")

    def clear_pockets():
        for obj in cmd.get_object_list():
            if obj.startswith("pocket_"):
                cmd.delete(obj)
        pocket_data[0] = {}
        form.fpocketDetailPanel.clear()
        form.fpocketStatusLabel.setText("Pockets cleared.")

    score_ramp = ["blue", "cyan", "green", "yellow", "orange", "red", "violet"]
    pre_score_color = [None]

    def color_by_pocket_score():
        if not pocket_data[0]:
            form.fpocketStatusLabel.setText("Run fpocket first.")
            return
        obj_name = form.fpocketObjectDropdown.currentText()
        if not obj_name:
            return
        out_dir = fpocket_output_dir[0]
        pre_score_color[0] = form.ProteinColorButton.text()

        cmd.show("surface", obj_name)
        cmd.set("surface_quality", 1, obj_name)
        cmd.color("gray", obj_name)

        for i in range(form.fpocketResultsList.count()):
            pocket_num = form.fpocketResultsList.item(i).text().split()[1]
            pocket_pdb = os.path.join(out_dir, "pockets", f"pocket{pocket_num}_atm.pdb")
            if not os.path.exists(pocket_pdb):
                continue

            residues = {}
            with open(pocket_pdb) as f:
                for line in f:
                    if line.startswith("ATOM") or line.startswith("HETATM"):
                        chain = line[21].strip() or "A"
                        resi = line[22:26].strip()
                        residues.setdefault(chain, set()).add(resi)

            if not residues:
                continue

            parts = []
            for chain, resi_set in residues.items():
                resi_str = "+".join(sorted(resi_set, key=lambda x: int(x) if x.isdigit() else 0))
                parts.append(f"(chain {chain} and resi {resi_str})")
            sel = f"{obj_name} and (" + " or ".join(parts) + ")"
            color = score_ramp[i % len(score_ramp)]
            cmd.color(color, sel)

        form.fpocketStatusLabel.setText("Surface colored by pocket score.")

    def export_docking_box():
        selected = form.fpocketResultsList.currentItem()
        if not selected:
            form.fpocketStatusLabel.setText("No pocket selected.")
            return
        out_dir = fpocket_output_dir[0]
        if not out_dir:
            form.fpocketStatusLabel.setText("Run fpocket first.")
            return

        pocket_num = selected.text().split()[1]
        pocket_pdb = os.path.join(out_dir, "pockets", f"pocket{pocket_num}_atm.pdb")
        if not os.path.exists(pocket_pdb):
            form.fpocketStatusLabel.setText(f"Pocket {pocket_num} file not found.")
            return

        xs, ys, zs = [], [], []
        with open(pocket_pdb) as f:
            for line in f:
                if line.startswith("ATOM") or line.startswith("HETATM"):
                    try:
                        xs.append(float(line[30:38]))
                        ys.append(float(line[38:46]))
                        zs.append(float(line[46:54]))
                    except ValueError:
                        continue

        if not xs:
            form.fpocketStatusLabel.setText("No coordinates found in pocket file.")
            return

        padding = 8.0
        cx = round(sum(xs) / len(xs), 3)
        cy = round(sum(ys) / len(ys), 3)
        cz = round(sum(zs) / len(zs), 3)
        sx = round((max(xs) - min(xs)) + padding, 3)
        sy = round((max(ys) - min(ys)) + padding, 3)
        sz = round((max(zs) - min(zs)) + padding, 3)

        from pymol.Qt import QtWidgets
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            dialog, "Save docking box config", f"pocket{pocket_num}_box.txt", "Text Files (*.txt)"
        )
        if not path:
            return

        with open(path, "w") as f:
            f.write(f"center_x = {cx}\n")
            f.write(f"center_y = {cy}\n")
            f.write(f"center_z = {cz}\n")
            f.write(f"size_x = {sx}\n")
            f.write(f"size_y = {sy}\n")
            f.write(f"size_z = {sz}\n")

        cmd.pseudoatom("docking_center", pos=[cx, cy, cz])
        cmd.show("sphere", "docking_center")
        cmd.set("sphere_scale", 0.5, "docking_center")
        cmd.color("magenta", "docking_center")

        form.fpocketStatusLabel.setText(f"Docking box saved to {os.path.basename(path)} | Center: ({cx}, {cy}, {cz})")

    def reset_surface():
        obj_name = form.fpocketObjectDropdown.currentText()
        if obj_name:
            cmd.hide("surface", obj_name)
        if pre_score_color[0]:
            on_color_change(pre_score_color[0])
            pre_score_color[0] = None
        form.fpocketStatusLabel.setText("Surface reset.")

    populate_object_dropdown()

    form.fpocketRefreshButton.clicked.connect(populate_object_dropdown)
    form.fpocketObjectDropdown.currentIndexChanged.connect(lambda _: update_visible_chains_label())
    form.tabWidget.currentChanged.connect(
        lambda idx: populate_object_dropdown() if idx == 1 else None
    )
    form.fpocketResultsList.currentRowChanged.connect(on_pocket_selected)
    form.fpocketRunButton.clicked.connect(run_fpocket)
    form.fpocketShowSelectedButton.clicked.connect(show_selected_pocket)
    form.fpocketShowAllButton.clicked.connect(show_all_pockets)
    form.fpocketClearButton.clicked.connect(clear_pockets)
    form.fpocketExportButton.clicked.connect(export_to_csv)
    form.fpocketPocketColorButton.clicked.connect(
        lambda: open_color_picker(form.fpocketPocketColorButton, on_pocket_color_change)
    )
    form.fpocketColorByScoreButton.clicked.connect(color_by_pocket_score)
    form.fpocketResetSurfaceButton.clicked.connect(reset_surface)
    form.fpocketDockingBoxButton.clicked.connect(export_docking_box)

    form.YesLigandButton.toggled.connect(lambda checked: apply_ligand_color() if checked else None)
    form.YesLigandButton.toggled.connect(lambda _: on_transparency_change(form.TransparencySlider.value()))
    form.NoLigandButton.toggled.connect(lambda _: on_transparency_change(form.TransparencySlider.value()))
    form.ProteinColorButton.clicked.connect(
        lambda: open_color_picker(form.ProteinColorButton, on_color_change)
    )
    form.LigandColorButton.clicked.connect(
        lambda: open_color_picker(form.LigandColorButton, on_ligand_color_change)
    )
    form.SibiStyleSign.toggled.connect(lambda checked: apply_sibi_style() if checked else None)
    form.BrownStyleSign.toggled.connect(lambda checked: apply_brown_style() if checked else None)
    form.OtherButton.toggled.connect(lambda checked: apply_sibi_style() if checked else None)
    form.TransparencySlider.valueChanged.connect(on_transparency_change)

    # ── Advanced Visual Controls tab ─────────────────────────────────────────
    def build_advanced_tab():
        from pymol.Qt import QtCore, QtGui

        # ── Info popup content ───────────────────────────────────────────────
        INFO_DATA = {
            "representations": {
                "image": "rep_overview.png",
                "html": """
<h3>Representations</h3>
<p>Representations control how atomic structures appear in the PyMOL viewport.
Use <b>Apply to</b> to limit any representation to a specific chain, object, or selection.</p>
<h4>Types:</h4>
<ul>
<li><b>Cartoon</b> — Ribbon diagram highlighting secondary structure (helices, sheets, loops).
Best for showing overall protein fold. Use for most publication figures.</li>
<li><b>Surface</b> — Molecular surface (solvent-accessible). Shows shape and size of binding
pockets. Can be slow for very large structures.</li>
<li><b>Sticks</b> — Cylindrical bond representation. Best for ligands, active sites, or any
time you need to show individual bonds clearly.</li>
<li><b>Spheres</b> — Space-filling CPK spheres showing van der Waals radii. Good for
showing packing or contact surfaces.</li>
<li><b>Mesh</b> — Wireframe surface. Lighter than solid surface — useful overlaid with
cartoon to show interior structure.</li>
<li><b>Dots</b> — Dot cloud surface. Softer, less prominent than solid surface. Good for
background context.</li>
<li><b>Putty</b> — Cartoon where tube width scales with B-factor. Wider = more
mobile/flexible. Excellent for communicating crystallographic dynamics.</li>
<li><b>Hide</b> — Removes all representations from the selected target only.</li>
</ul>
<h4>Common combinations:</h4>
<ul>
<li>Binding site: Cartoon (protein) + Sticks (ligand) + transparent Surface</li>
<li>Flexibility: Putty colored by B-factor</li>
<li>Large complex: Surface only, colored by chain</li>
</ul>"""
            },
            "ray_trace": {
                "image": "ray_trace_modes.png",
                "html": """
<h3>Ray Trace Mode</h3>
<p>Ray tracing calculates realistic lighting and shadows, producing publication-quality
images. Each mode produces a distinct visual style. Click <b>Apply Ray Trace Now</b>
to render — this may take a few seconds to minutes depending on structure size.</p>
<h4>Modes:</h4>
<ul>
<li><b>Mode 0 — Standard</b>: Default OpenGL rendering. Fast, good for interactive work.
No ray tracing effects.</li>
<li><b>Mode 1 — Photorealistic + AO</b>: Adds ambient occlusion — crevices appear darker,
giving strong depth cues. Best choice for most publication figures.</li>
<li><b>Mode 2 — Black Ink Outline</b>: Draws outlines around structures — cartoon/comic
style. Great for graphical abstracts, posters, and teaching materials. Pair with the
outline color button to customize.</li>
<li><b>Mode 3 — Toon / Quantized</b>: Cel-shaded look with quantized lighting zones.
Striking for posters and educational figures.</li>
</ul>
<h4>Contrast (ray_trace_gain):</h4>
<p>Increases the difference between lit and shadowed regions. Higher values produce
more dramatic, high-contrast renders.</p>
<h4>Use cases:</h4>
<ul>
<li>Journal figure: Mode 1 + Soft Studio lighting preset</li>
<li>Graphical abstract / cover image: Mode 2 with colored outline</li>
<li>Poster or teaching slide: Mode 3</li>
</ul>"""
            },
            "lighting": {
                "image": "lighting.png",
                "html": """
<h3>Lighting</h3>
<p>These controls adjust the virtual lights illuminating your structure. Small changes
here can dramatically improve the depth and clarity of a figure.</p>
<h4>Parameters:</h4>
<ul>
<li><b>Ambient</b>: Overall scene fill light — how bright shadowed areas are. High
ambient = flat/even, low ambient = dramatic shadows.</li>
<li><b>Direct</b>: Main directional light strength. Increases contrast between lit
and shadowed faces of the structure.</li>
<li><b>Specular</b>: Intensity of specular highlights (shiny spots on surfaces).
High = glossy/plastic look. Low = matte/diffuse.</li>
<li><b>Shininess</b>: Size of specular highlights. High = small tight spots,
Low = broad diffuse glow.</li>
<li><b>Two-sided lighting</b>: Illuminates both faces of surfaces. Without this,
the inside of helices and the backs of beta-sheets appear pitch black.</li>
</ul>
<h4>Presets:</h4>
<ul>
<li><b>Flat</b>: Even illumination, minimal shadows. Good for schematic/diagram figures.</li>
<li><b>Soft Studio</b>: Balanced professional lighting — good all-purpose starting point.</li>
<li><b>Dramatic</b>: Strong directional light with deep shadows. Striking for posters.</li>
<li><b>Hard Scientific</b>: PyMOL default scientific settings. Neutral and clean.</li>
</ul>"""
            },
            "color_by": {
                "image": "color_by.png",
                "html": """
<h3>Color By Property</h3>
<p>Map structural or chemical properties onto atom colors to communicate information
visually. These options apply to all loaded atoms unless you have a selection active.</p>
<h4>Options:</h4>
<ul>
<li><b>By B-factor</b>: Crystallographic temperature factor. <b>Blue = rigid/ordered,
Red = flexible/mobile.</b> Use min/max to clamp to your data range. Essential for
discussing protein dynamics from crystal structures.</li>
<li><b>By Chain</b>: Each polypeptide chain gets a unique color. Ideal for
multi-chain complexes, homo/heterodimers, or antibody-antigen complexes.</li>
<li><b>By Secondary Structure</b>: Helices = red, Sheets = yellow, Loops = green.
Instant structural overview without needing to know the sequence.</li>
<li><b>By Hydrophobicity</b>: Kyte-Doolittle scale. <b>Red = hydrophobic</b>
(ILE, VAL, LEU...), <b>Blue = hydrophilic</b> (ARG, LYS, ASP...). Identify
hydrophobic patches, membrane-binding faces, or protein-protein interaction surfaces.</li>
<li><b>Rainbow (sequence)</b>: Blue at N-terminus → red at C-terminus. Shows chain
directionality and helps identify domain boundaries.</li>
<li><b>By Element</b>: CPK coloring — C=green, N=blue, O=red, S=yellow. Standard
chemistry representation for active site figures.</li>
</ul>"""
            },
            "cartoon_quality": {
                "image": "cartoon_quality.png",
                "html": """
<h3>Cartoon Quality</h3>
<p>Fine-tune the smoothness and proportions of the cartoon representation.
Changes apply in real time — adjust while looking at the structure.</p>
<h4>Parameters:</h4>
<ul>
<li><b>Smoothness</b> (cartoon_sampling): Number of interpolation points along the
backbone. Higher = smoother curves. Use 14+ for publication, 7–10 for interactive
work with large structures where speed matters.</li>
<li><b>Loop Radius</b>: Thickness of coil/loop tubes. Increase for bold poster-style
figures or to make loops more visible in complex scenes.</li>
<li><b>Tube Radius</b>: Thickness of the backbone in tube representation mode.</li>
<li><b>Helix Radius</b>: Cross-sectional size of alpha helices. Increase for emphasis,
decrease for a sleeker minimalist look.</li>
</ul>
<h4>Tips:</h4>
<ul>
<li><b>Journal figure:</b> smoothness 16–20, standard radii</li>
<li><b>Poster:</b> smoothness 14, increase radii by ~30% for boldness</li>
<li><b>Large complex (>500 residues):</b> smoothness 7–9 for interactive speed</li>
</ul>"""
            },
            "depth_fog": {
                "image": "depth_fog.png",
                "html": """
<h3>Depth &amp; Fog</h3>
<p>Control how depth is communicated and how the background appears in rendered images.</p>
<h4>Settings:</h4>
<ul>
<li><b>Depth Cue</b>: Fades atoms in the background to convey depth. Very effective
for dense, complex structures. Disable for flat 2D-style schematic figures.</li>
<li><b>Fog Start</b>: Where fog begins relative to the scene depth.
<b>0.0</b> = fog starts at the camera (everything foggy),
<b>1.0</b> = fog at the very back (no visible fog).
Values of <b>0.4–0.6</b> work well for most structures.</li>
<li><b>Ray Trace Fog</b>: Apply fog during ray tracing. Disable for maximum clarity
in publication renders — fog can obscure fine structural details.</li>
<li><b>Transparent Background</b>: Remove the background color from PNG exports.
Essential for compositing in Adobe Illustrator, PowerPoint, or Photoshop — places
the structure on any background without a white box.</li>
</ul>
<h4>Use cases:</h4>
<ul>
<li>Large complex (ribosome, virus capsid): depth cue on, fog 0.4–0.5</li>
<li>Journal figure panel: depth cue off, ray trace fog off, transparent background on</li>
<li>Poster with colored background: transparent background on</li>
</ul>"""
            },
            "hbonds": {
                "image": "hbonds.png",
                "html": """
<h3>H-Bond Visualization</h3>
<p>Draws dashed lines between hydrogen bond donors and acceptors. Uses PyMOL's
distance command in H-bond mode (mode=2), which checks both geometry and chemistry.</p>
<h4>Settings:</h4>
<ul>
<li><b>Max distance</b>: Maximum donor–acceptor distance to consider an H-bond.
Typical strong H-bonds: <b>2.5–3.2 Å</b>. Standard cutoff: <b>3.5 Å</b>.
Increase to 4.0 Å to capture weak or water-mediated interactions.</li>
<li><b>Show distance labels</b>: Display the exact distance in Å on each dash.
Useful for detailed analysis; turn off for clean publication figures.</li>
</ul>
<h4>Use cases:</h4>
<ul>
<li><b>Alpha helix backbone H-bonds:</b> Select the helix region, then Show H-bonds</li>
<li><b>Protein-ligand contacts:</b> Select the ligand in PyMOL (sele), Show H-bonds</li>
<li><b>Beta sheet network:</b> Select the sheet strands, Show H-bonds</li>
<li><b>Active site analysis:</b> Select catalytic residues, Show H-bonds to substrate</li>
</ul>
<p><b>Tip:</b> Make a PyMOL selection first to limit H-bonds to a region of interest.
Using "all" on large proteins will draw thousands of dashes and clutter the scene.</p>"""
            },
            "export": {
                "image": "export.png",
                "html": """
<h3>Export / Render</h3>
<p>Ray trace and save high-resolution images for publication or presentation.
Set your Ray Trace Mode and lighting <em>before</em> clicking Ray Trace &amp; Save.</p>
<h4>Resolution guide:</h4>
<ul>
<li><b>1x (800×600)</b>: Draft review and presentations where file size matters.</li>
<li><b>2x (1600×1200)</b>: Good for most journal figures at 300 DPI.
<b>Recommended starting point.</b></li>
<li><b>4x (3200×2400)</b>: High resolution for large poster panels or journals
requiring 600 DPI. Ray trace time is roughly 4× longer than 2x.</li>
<li><b>Custom</b>: Full control — useful for specific journal dimension requirements
(e.g. 3.5-inch column width at 300 DPI = 1050 px wide).</li>
</ul>
<h4>Transparent background:</h4>
<p>PNG supports transparency; JPEG does not. With a transparent background you can
place the structure on any colored or gradient background in Illustrator or
PowerPoint without white-box artifacts around the structure.</p>
<h4>Tips:</h4>
<ul>
<li>2x is sufficient for the vast majority of journal submissions</li>
<li>Ray tracing a 4x image of a large protein can take several minutes</li>
<li>Use Mode 1 (Photorealistic + AO) for best-looking publication renders</li>
</ul>"""
            },
        }

        def show_info_popup(title, info_key):
            data = INFO_DATA.get(info_key, {})
            html  = data.get("html",  "<p>No information available.</p>")
            image_name = data.get("image", None)

            popup = QtWidgets.QDialog(dialog)
            popup.setWindowTitle(title)
            popup.setMinimumWidth(500)
            layout = QtWidgets.QVBoxLayout(popup)

            if image_name:
                img_path = os.path.join(os.path.dirname(__file__), "images", image_name)
                if os.path.exists(img_path):
                    img_lbl = QtWidgets.QLabel()
                    pixmap = QtGui.QPixmap(img_path)
                    img_lbl.setPixmap(
                        pixmap.scaledToWidth(480, QtCore.Qt.SmoothTransformation)
                    )
                    img_lbl.setAlignment(QtCore.Qt.AlignCenter)
                    layout.addWidget(img_lbl)

            browser = QtWidgets.QTextBrowser()
            browser.setHtml(html)
            browser.setMinimumHeight(220)
            browser.setOpenExternalLinks(True)
            layout.addWidget(browser)

            btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Close)
            btn_box.rejected.connect(popup.reject)
            layout.addWidget(btn_box)
            popup.exec_()

        def make_section(title, info_key):
            """Returns (outer_frame, content_layout) — replaces QGroupBox."""
            frame = QtWidgets.QFrame()
            frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
            frame.setFrameShadow(QtWidgets.QFrame.Raised)
            outer = QtWidgets.QVBoxLayout(frame)
            outer.setContentsMargins(6, 4, 6, 6)
            outer.setSpacing(4)

            # Header row: bold title left, ? button right
            header = QtWidgets.QWidget()
            header_layout = QtWidgets.QHBoxLayout(header)
            header_layout.setContentsMargins(0, 0, 0, 0)
            title_lbl = QtWidgets.QLabel(f"<b>{title}</b>")
            info_btn = QtWidgets.QPushButton("?")
            info_btn.setFixedSize(20, 20)
            info_btn.setToolTip(f"Learn more about {title}")
            info_btn.setStyleSheet(
                "QPushButton { font-weight: bold; border-radius: 10px; "
                "background-color: #4a90d9; color: white; border: none; }"
                "QPushButton:hover { background-color: #357abd; }"
            )
            info_btn.clicked.connect(lambda _, t=title, k=info_key: show_info_popup(t, k))
            header_layout.addWidget(title_lbl)
            header_layout.addStretch()
            header_layout.addWidget(info_btn)
            outer.addWidget(header)

            line = QtWidgets.QFrame()
            line.setFrameShape(QtWidgets.QFrame.HLine)
            line.setFrameShadow(QtWidgets.QFrame.Sunken)
            outer.addWidget(line)

            content_widget = QtWidgets.QWidget()
            content_layout = QtWidgets.QVBoxLayout(content_widget)
            content_layout.setContentsMargins(2, 2, 2, 2)
            outer.addWidget(content_widget)
            return frame, content_layout

        def make_info_label(text):
            lbl = QtWidgets.QLabel(text)
            lbl.setWordWrap(True)
            lbl.setStyleSheet("color: #666; font-size: 10px; font-style: italic;")
            return lbl

        def make_slider_row(minimum, maximum, value, scale=1.0, fmt="{:.2f}"):
            """Returns (container widget, QSlider). A value label updates live."""
            container = QtWidgets.QWidget()
            layout = QtWidgets.QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            slider.setMinimum(minimum)
            slider.setMaximum(maximum)
            slider.setValue(value)
            val_lbl = QtWidgets.QLabel(fmt.format(value * scale))
            val_lbl.setFixedWidth(42)
            slider.valueChanged.connect(lambda v, l=val_lbl, f=fmt, s=scale: l.setText(f.format(v * s)))
            layout.addWidget(slider)
            layout.addWidget(val_lbl)
            return container, slider

        # ── 1. Representations ───────────────────────────────────────────────
        rep_group, rep_layout = make_section("Representations", "representations")
        rep_layout.addWidget(make_info_label(
            "Show or hide structural representations. Use 'Apply to' to target "
            "a specific object, chain, or your current PyMOL selection."
        ))

        # — Target selector row —
        target_row = QtWidgets.QWidget()
        target_row_layout = QtWidgets.QHBoxLayout(target_row)
        target_row_layout.setContentsMargins(0, 0, 0, 0)
        target_row_layout.addWidget(QtWidgets.QLabel("Apply to:"))

        target_dropdown = QtWidgets.QComboBox()
        target_dropdown.addItems(["All", "Selection", "Object", "Chain"])
        target_dropdown.setToolTip("Choose what the representation buttons act on")
        target_row_layout.addWidget(target_dropdown)

        # Object combo (shown when mode = Object)
        object_combo = QtWidgets.QComboBox()
        object_combo.setToolTip("Choose a loaded PyMOL object")
        object_combo.setVisible(False)
        target_row_layout.addWidget(object_combo)

        # Chain combo (shown when mode = Chain)
        chain_combo = QtWidgets.QComboBox()
        chain_combo.setToolTip("Choose a chain")
        chain_combo.setVisible(False)
        target_row_layout.addWidget(chain_combo)

        # Selection status label (shown when mode = Selection)
        sele_label = QtWidgets.QLabel("")
        sele_label.setStyleSheet("color: #444; font-size: 10px;")
        sele_label.setVisible(False)
        target_row_layout.addWidget(sele_label)

        # Refresh button
        rep_refresh_btn = QtWidgets.QPushButton("Refresh")
        rep_refresh_btn.setFixedWidth(64)
        rep_refresh_btn.setToolTip("Refresh available objects, chains, or selection info")
        target_row_layout.addWidget(rep_refresh_btn)
        target_row_layout.addStretch()
        rep_layout.addWidget(target_row)

        def refresh_rep_widgets():
            mode = target_dropdown.currentText()
            object_combo.setVisible(mode == "Object")
            chain_combo.setVisible(mode == "Chain")
            sele_label.setVisible(mode == "Selection")

            if mode == "Object":
                object_combo.clear()
                for obj in cmd.get_object_list():
                    object_combo.addItem(obj)

            elif mode == "Chain":
                chain_combo.clear()
                seen = []
                for obj in cmd.get_object_list():
                    for ch in cmd.get_chains(obj):
                        if ch and ch not in seen:
                            seen.append(ch)
                            chain_combo.addItem(ch)

            elif mode == "Selection":
                if "sele" in cmd.get_names("selections"):
                    count = cmd.count_atoms("sele")
                    sele_label.setText(f"sele: {count} atoms")
                    sele_label.setStyleSheet("color: #226622; font-size: 10px;")
                else:
                    sele_label.setText("No active selection in PyMOL")
                    sele_label.setStyleSheet("color: #aa2222; font-size: 10px;")

        target_dropdown.currentIndexChanged.connect(lambda _: refresh_rep_widgets())
        rep_refresh_btn.clicked.connect(refresh_rep_widgets)

        def get_rep_target():
            mode = target_dropdown.currentText()
            if mode == "Selection":
                return "sele" if "sele" in cmd.get_names("selections") else "all"
            if mode == "Object":
                return object_combo.currentText() or "all"
            if mode == "Chain":
                ch = chain_combo.currentText()
                return f"chain {ch}" if ch else "all"
            return "all"

        # — Representation buttons —
        rep_btn_widget = QtWidgets.QWidget()
        rep_btn_grid = QtWidgets.QGridLayout(rep_btn_widget)
        rep_btn_grid.setSpacing(4)
        rep_actions = [
            ("Cartoon",  lambda: (cmd.show("cartoon", get_rep_target()), cmd.hide("lines", get_rep_target())),
             "Standard ribbon/cartoon — best for overall fold"),
            ("Surface",  lambda: cmd.show("surface", get_rep_target()),
             "Molecular surface — slow for large structures"),
            ("Sticks",   lambda: cmd.show("sticks", get_rep_target()),
             "Bond stick representation — good for ligands"),
            ("Spheres",  lambda: cmd.show("spheres", get_rep_target()),
             "Space-filling CPK spheres"),
            ("Mesh",     lambda: cmd.show("mesh", get_rep_target()),
             "Wireframe mesh surface — lighter than solid surface"),
            ("Dots",     lambda: cmd.show("dots", get_rep_target()),
             "Dot surface — softer alternative to solid surface"),
            ("Putty",    lambda: (cmd.cartoon("putty", get_rep_target()), cmd.show("cartoon", get_rep_target())),
             "Putty: tube radius scales with B-factor (crystallographic flexibility)"),
            ("Hide",     lambda: cmd.hide("everything", get_rep_target()),
             "Hide all representations on the current target"),
        ]
        for i, (lbl, fn, tip) in enumerate(rep_actions):
            btn = QtWidgets.QPushButton(lbl)
            btn.setToolTip(tip)
            btn.clicked.connect(fn)
            rep_btn_grid.addWidget(btn, i // 4, i % 4)
        rep_layout.addWidget(rep_btn_widget)

        # ── 2. Ray Trace Mode ────────────────────────────────────────────────
        rt_group, rt_layout = make_section("Ray Trace Mode", "ray_trace")
        rt_layout.addWidget(make_info_label(
            "Mode 1 adds ambient occlusion for depth. Mode 2 draws ink outlines — "
            "pair with the outline color button. Mode 3 gives a cel-shaded look."
        ))
        rt_modes = [
            (0, "Standard"),
            (1, "Photorealistic + Ambient Occlusion"),
            (2, "Black Ink Outline"),
            (3, "Toon / Quantized"),
        ]
        rt_radios = []
        for mode, label in rt_modes:
            rb = QtWidgets.QRadioButton(label)
            rb.setToolTip(f"Sets ray_trace_mode to {mode}")
            rb.toggled.connect(lambda checked, m=mode: cmd.set("ray_trace_mode", m) if checked else None)
            rt_layout.addWidget(rb)
            rt_radios.append(rb)
        rt_radios[0].setChecked(True)

        outline_row = QtWidgets.QWidget()
        outline_layout = QtWidgets.QHBoxLayout(outline_row)
        outline_layout.setContentsMargins(0, 0, 0, 0)
        outline_layout.addWidget(QtWidgets.QLabel("Outline color (mode 2):"))
        outline_btn = QtWidgets.QPushButton("Black")
        outline_btn.setToolTip("Color of ink outlines when using Black Ink Outline mode")
        outline_btn.setStyleSheet("background-color: rgb(0,0,0); color: white;")
        outline_btn.clicked.connect(
            lambda: open_color_picker(outline_btn,
                lambda name: cmd.set("ray_trace_color", get_color(name)[0]))
        )
        outline_layout.addWidget(outline_btn)
        rt_layout.addWidget(outline_row)

        rt_layout.addWidget(QtWidgets.QLabel("Contrast (ray_trace_gain):"))
        gain_row, gain_slider = make_slider_row(0, 200, 100, scale=0.01, fmt="{:.2f}")
        gain_slider.setToolTip("Higher values increase contrast between lit and shadowed areas")
        gain_slider.valueChanged.connect(lambda v: cmd.set("ray_trace_gain", v / 100.0))
        rt_layout.addWidget(gain_row)

        apply_rt_btn = QtWidgets.QPushButton("Apply Ray Trace Now")
        apply_rt_btn.setToolTip("Render the current view with ray tracing and save to file")

        def apply_ray_trace():
            path, _ = QtWidgets.QFileDialog.getSaveFileName(
                dialog, "Save Ray Traced Image", "",
                "PNG Files (*.png);;JPEG Files (*.jpg)"
            )
            if not path:
                return
            cmd.ray()
            cmd.png(path, dpi=300)

        apply_rt_btn.clicked.connect(apply_ray_trace)
        rt_layout.addWidget(apply_rt_btn)

        # ── 3. Lighting ──────────────────────────────────────────────────────
        light_group, light_layout = make_section("Lighting", "lighting")
        light_layout.addWidget(make_info_label(
            "Ambient = overall scene brightness. Direct = main light strength. "
            "Two-sided lighting illuminates the inside of helices and sheets."
        ))
        light_sliders = {}
        light_configs = [
            ("ambient",   "Ambient",   0, 100, 10,  0.01, "{:.2f}"),
            ("direct",    "Direct",    0, 100, 45,  0.01, "{:.2f}"),
            ("specular",  "Specular",  0, 100, 50,  0.01, "{:.2f}"),
            ("shininess", "Shininess", 1, 100, 50,  1.0,  "{:.0f}"),
        ]
        for key, label, mn, mx, default, scale, fmt in light_configs:
            light_layout.addWidget(QtWidgets.QLabel(label + ":"))
            row, slider = make_slider_row(mn, mx, default, scale=scale, fmt=fmt)
            slider.setToolTip(f"Adjusts PyMOL '{key}' setting")
            slider.valueChanged.connect(lambda v, k=key, s=scale: cmd.set(k, v * s))
            light_layout.addWidget(row)
            light_sliders[key] = slider

        two_sided_cb = QtWidgets.QCheckBox("Two-sided lighting")
        two_sided_cb.setToolTip("Illuminates both faces — makes helix interiors visible")
        two_sided_cb.toggled.connect(lambda c: cmd.set("two_sided_lighting", 1 if c else 0))
        light_layout.addWidget(two_sided_cb)

        light_layout.addWidget(QtWidgets.QLabel("Presets:"))
        preset_row = QtWidgets.QWidget()
        preset_layout = QtWidgets.QHBoxLayout(preset_row)
        preset_layout.setContentsMargins(0, 0, 0, 0)
        lighting_presets = {
            "Flat":           {"ambient": 80, "direct": 20, "specular": 0,  "shininess": 10},
            "Soft Studio":    {"ambient": 40, "direct": 60, "specular": 30, "shininess": 40},
            "Dramatic":       {"ambient": 10, "direct": 80, "specular": 60, "shininess": 80},
            "Hard Scientific":{"ambient": 10, "direct": 45, "specular": 50, "shininess": 50},
        }
        for name, preset in lighting_presets.items():
            btn = QtWidgets.QPushButton(name)
            btn.setToolTip(f"Apply '{name}' lighting preset")
            btn.clicked.connect(lambda _, p=preset: [light_sliders[k].setValue(v) for k, v in p.items()])
            preset_layout.addWidget(btn)
        light_layout.addWidget(preset_row)

        # ── 4. Color By Property ─────────────────────────────────────────────
        color_group, color_layout = make_section("Color By Property", "color_by")
        color_layout.addWidget(make_info_label(
            "B-factor: blue=rigid, red=flexible. Set min/max to clamp the color range. "
            "'By Element' restores standard CPK coloring."
        ))
        bf_row = QtWidgets.QWidget()
        bf_layout = QtWidgets.QHBoxLayout(bf_row)
        bf_layout.setContentsMargins(0, 0, 0, 0)
        bf_layout.addWidget(QtWidgets.QLabel("B-factor min:"))
        bf_min = QtWidgets.QDoubleSpinBox()
        bf_min.setRange(0, 200); bf_min.setValue(0); bf_min.setDecimals(1)
        bf_layout.addWidget(bf_min)
        bf_layout.addWidget(QtWidgets.QLabel("max:"))
        bf_max = QtWidgets.QDoubleSpinBox()
        bf_max.setRange(0, 200); bf_max.setValue(100); bf_max.setDecimals(1)
        bf_layout.addWidget(bf_max)
        color_layout.addWidget(bf_row)

        def color_by_hydrophobicity():
            kd = {"ILE": 4.5, "VAL": 4.2, "LEU": 3.8, "PHE": 2.8, "CYS": 2.5,
                  "MET": 1.9, "ALA": 1.8, "GLY": -0.4, "THR": -0.7, "SER": -0.8,
                  "TRP": -0.9, "TYR": -1.3, "PRO": -1.6, "HIS": -3.2, "GLU": -3.5,
                  "GLN": -3.5, "ASP": -3.5, "ASN": -3.5, "LYS": -3.9, "ARG": -4.5}
            cmd.alter("all", "b=0")
            for resn, score in kd.items():
                normalized = (score + 4.5) / 9.0 * 100
                cmd.alter(f"resn {resn}", f"b={normalized:.1f}")
            cmd.spectrum("b", "blue_white_red", "all", 0, 100)

        color_actions = [
            ("By B-factor",
             lambda: cmd.spectrum("b", "blue_white_red", "all", bf_min.value(), bf_max.value()),
             "Color by crystallographic B-factor: blue=rigid, red=flexible"),
            ("By Chain",
             lambda: cmd.util.cbc(),
             "Assign a unique color to each chain"),
            ("By Secondary Struct",
             lambda: cmd.util.cbss(),
             "Color helices red, sheets yellow, loops green"),
            ("By Hydrophobicity",
             color_by_hydrophobicity,
             "Kyte-Doolittle scale: red=hydrophobic, blue=hydrophilic"),
            ("Rainbow (sequence)",
             lambda: cmd.spectrum("count", "rainbow"),
             "Color residues from blue (N-terminus) to red (C-terminus)"),
            ("By Element",
             lambda: cmd.util.cbag(),
             "Restore CPK element coloring: C=green, N=blue, O=red, S=yellow"),
        ]
        color_btn_widget = QtWidgets.QWidget()
        color_btn_grid = QtWidgets.QGridLayout(color_btn_widget)
        color_btn_grid.setSpacing(4)
        for i, (lbl, fn, tip) in enumerate(color_actions):
            btn = QtWidgets.QPushButton(lbl)
            btn.setToolTip(tip)
            btn.clicked.connect(fn)
            color_btn_grid.addWidget(btn, i // 2, i % 2)
        color_layout.addWidget(color_btn_widget)

        # ── 5. Cartoon Quality ───────────────────────────────────────────────
        cartoon_group, cartoon_layout = make_section("Cartoon Quality", "cartoon_quality")
        cartoon_layout.addWidget(make_info_label(
            "Higher smoothness = slower but publication-quality curves. "
            "Increase radii for bold, poster-style figures."
        ))
        cartoon_sliders = {}
        cartoon_configs = [
            ("cartoon_sampling",     "Smoothness",    7,  20,  14, 1.0,  "{:.0f}"),
            ("cartoon_loop_radius",  "Loop Radius",   1,  10,  2,  0.1,  "{:.1f}"),
            ("cartoon_tube_radius",  "Tube Radius",   1,  10,  4,  0.1,  "{:.1f}"),
            ("cartoon_helix_radius", "Helix Radius",  5,  30,  13, 0.1,  "{:.1f}"),
        ]
        for key, label, mn, mx, default, scale, fmt in cartoon_configs:
            cartoon_layout.addWidget(QtWidgets.QLabel(label + ":"))
            row, slider = make_slider_row(mn, mx, default, scale=scale, fmt=fmt)
            slider.setToolTip(f"Adjusts PyMOL '{key}' setting")
            slider.valueChanged.connect(lambda v, k=key, s=scale: cmd.set(k, v * s))
            cartoon_layout.addWidget(row)
            cartoon_sliders[key] = slider

        cartoon_reset_btn = QtWidgets.QPushButton("Reset Defaults")
        cartoon_reset_btn.setToolTip("Restore default cartoon quality settings")
        cartoon_reset_btn.clicked.connect(lambda: [
            cartoon_sliders["cartoon_sampling"].setValue(14),
            cartoon_sliders["cartoon_loop_radius"].setValue(2),
            cartoon_sliders["cartoon_tube_radius"].setValue(4),
            cartoon_sliders["cartoon_helix_radius"].setValue(13),
        ])
        cartoon_layout.addWidget(cartoon_reset_btn)

        # ── 6. Depth & Fog ───────────────────────────────────────────────────
        fog_group, fog_layout = make_section("Depth & Fog", "depth_fog")
        fog_layout.addWidget(make_info_label(
            "Fog start of 0.4 = fog begins 40% into the scene. "
            "Disable depth cue for flat, journal-style figures."
        ))
        depth_cue_cb = QtWidgets.QCheckBox("Depth Cue")
        depth_cue_cb.setChecked(True)
        depth_cue_cb.setToolTip("Fade distant atoms to convey depth in complex structures")
        depth_cue_cb.toggled.connect(lambda c: cmd.set("depth_cue", 1 if c else 0))
        fog_layout.addWidget(depth_cue_cb)

        fog_layout.addWidget(QtWidgets.QLabel("Fog Start:"))
        fog_row, fog_slider = make_slider_row(0, 100, 40, scale=0.01, fmt="{:.2f}")
        fog_slider.setToolTip("0.0 = fog at camera, 1.0 = fog at far end of scene")
        fog_slider.valueChanged.connect(lambda v: cmd.set("fog_start", v / 100.0))
        fog_layout.addWidget(fog_row)

        rt_fog_cb = QtWidgets.QCheckBox("Ray Trace Fog")
        rt_fog_cb.setToolTip("Apply fog during ray tracing — disable for crisp publication renders")
        rt_fog_cb.toggled.connect(lambda c: cmd.set("ray_trace_fog", 1 if c else 0))
        fog_layout.addWidget(rt_fog_cb)

        transp_bg_cb = QtWidgets.QCheckBox("Transparent Background")
        transp_bg_cb.setToolTip(
            "Removes background for PNG export — useful for compositing in Illustrator or PowerPoint"
        )
        transp_bg_cb.toggled.connect(lambda c: cmd.set("ray_opaque_background", 0 if c else 1))
        fog_layout.addWidget(transp_bg_cb)

        # ── 7. H-Bond Visualization ──────────────────────────────────────────
        hb_group, hb_layout = make_section("H-Bond Visualization", "hbonds")
        hb_layout.addWidget(make_info_label(
            "Draws dashed lines between H-bond donors and acceptors. "
            "If a PyMOL selection ('sele') exists, only that region is used."
        ))
        hb_cutoff_row = QtWidgets.QWidget()
        hb_cutoff_layout = QtWidgets.QHBoxLayout(hb_cutoff_row)
        hb_cutoff_layout.setContentsMargins(0, 0, 0, 0)
        hb_cutoff_layout.addWidget(QtWidgets.QLabel("Max distance (Å):"))
        hb_cutoff = QtWidgets.QDoubleSpinBox()
        hb_cutoff.setRange(2.0, 5.0); hb_cutoff.setValue(3.5)
        hb_cutoff.setSingleStep(0.1); hb_cutoff.setDecimals(1)
        hb_cutoff.setToolTip("Typical H-bond cutoff is 3.2–3.5 Å")
        hb_cutoff_layout.addWidget(hb_cutoff)
        hb_layout.addWidget(hb_cutoff_row)

        hb_labels_cb = QtWidgets.QCheckBox("Show distance labels")
        hb_labels_cb.setToolTip("Display Å distance on each H-bond dash line")
        hb_layout.addWidget(hb_labels_cb)

        def show_hbonds():
            sel = "sele" if "sele" in cmd.get_names("selections") else "all"
            cmd.delete("hbonds")
            cmd.distance("hbonds", sel, sel, hb_cutoff.value(), mode=2)
            if not hb_labels_cb.isChecked():
                cmd.hide("labels", "hbonds")

        hb_btn_row = QtWidgets.QWidget()
        hb_btn_layout = QtWidgets.QHBoxLayout(hb_btn_row)
        hb_btn_layout.setContentsMargins(0, 0, 0, 0)
        show_hb_btn = QtWidgets.QPushButton("Show H-bonds")
        show_hb_btn.setToolTip("Draw H-bond dashes in the current scene")
        show_hb_btn.clicked.connect(show_hbonds)
        clear_hb_btn = QtWidgets.QPushButton("Clear H-bonds")
        clear_hb_btn.setToolTip("Remove all H-bond distance objects from the scene")
        clear_hb_btn.clicked.connect(lambda: cmd.delete("hbonds"))
        hb_btn_layout.addWidget(show_hb_btn)
        hb_btn_layout.addWidget(clear_hb_btn)
        hb_layout.addWidget(hb_btn_row)

        # ── 8. Export / Render ───────────────────────────────────────────────
        export_group, export_layout = make_section("Export / Render", "export")
        export_layout.addWidget(make_info_label(
            "Ray tracing is slow at 4x — use 2x for most publications. "
            "PNG supports transparency; JPEG does not."
        ))
        res_row = QtWidgets.QWidget()
        res_layout = QtWidgets.QHBoxLayout(res_row)
        res_layout.setContentsMargins(0, 0, 0, 0)
        res_layout.addWidget(QtWidgets.QLabel("Resolution:"))
        res_combo = QtWidgets.QComboBox()
        res_combo.addItems(["1x — 800×600", "2x — 1600×1200", "4x — 3200×2400", "Custom"])
        res_combo.setToolTip("Select output image resolution — higher = slower ray trace")
        res_layout.addWidget(res_combo)
        export_layout.addWidget(res_row)

        custom_row = QtWidgets.QWidget()
        custom_layout = QtWidgets.QHBoxLayout(custom_row)
        custom_layout.setContentsMargins(0, 0, 0, 0)
        custom_layout.addWidget(QtWidgets.QLabel("W:"))
        custom_w = QtWidgets.QSpinBox()
        custom_w.setRange(100, 8000); custom_w.setValue(1200)
        custom_layout.addWidget(custom_w)
        custom_layout.addWidget(QtWidgets.QLabel("H:"))
        custom_h = QtWidgets.QSpinBox()
        custom_h.setRange(100, 8000); custom_h.setValue(900)
        custom_layout.addWidget(custom_h)
        custom_row.setVisible(False)
        export_layout.addWidget(custom_row)
        res_combo.currentIndexChanged.connect(lambda i: custom_row.setVisible(i == 3))

        export_transp_cb = QtWidgets.QCheckBox("Transparent background (PNG only)")
        export_transp_cb.setToolTip("Sets ray_opaque_background=0 before rendering")
        export_layout.addWidget(export_transp_cb)

        def ray_and_save():
            resolutions = [(800, 600), (1600, 1200), (3200, 2400)]
            idx = res_combo.currentIndex()
            w, h = resolutions[idx] if idx < 3 else (custom_w.value(), custom_h.value())
            if export_transp_cb.isChecked():
                cmd.set("ray_opaque_background", 0)
            path, _ = QtWidgets.QFileDialog.getSaveFileName(
                dialog, "Save rendered image", "",
                "PNG Files (*.png);;JPEG Files (*.jpg)"
            )
            if not path:
                cmd.set("ray_opaque_background", 1)
                return
            cmd.ray(w, h)
            cmd.png(path, dpi=300)
            if export_transp_cb.isChecked():
                cmd.set("ray_opaque_background", 1)

        save_btn = QtWidgets.QPushButton("Ray Trace & Save")
        save_btn.setToolTip("Ray trace at the selected resolution and save to file")
        save_btn.clicked.connect(ray_and_save)
        export_layout.addWidget(save_btn)

        # ── Assemble 2-column grid ───────────────────────────────────────────
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        content = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout(content)
        grid.setSpacing(10)
        grid.setContentsMargins(10, 10, 10, 10)
        grid.addWidget(rep_group,     0, 0)
        grid.addWidget(rt_group,      0, 1)
        grid.addWidget(light_group,   1, 0)
        grid.addWidget(color_group,   1, 1)
        grid.addWidget(cartoon_group, 2, 0)
        grid.addWidget(fog_group,     2, 1)
        grid.addWidget(hb_group,      3, 0)
        grid.addWidget(export_group,  3, 1)
        scroll.setWidget(content)

        tab_layout = QtWidgets.QVBoxLayout(form.advancedTab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll)

    build_advanced_tab()

    return dialog
