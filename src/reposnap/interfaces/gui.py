# src/reposnap/interfaces/gui.py

import urwid
from pathlib import Path
from reposnap.controllers.project_controller import ProjectController


class MyCheckBox(urwid.CheckBox):
    def __init__(self, label, user_data=None, **kwargs):
        super().__init__(label, **kwargs)
        self.user_data = user_data


class RepoSnapGUI:
    def __init__(self):
        self.controller = ProjectController()
        self.root_dir = Path('.').resolve()
        self.file_tree = None
        self.selected_files = set()

        self.main_loop = None
        self.build_main_menu()

    def build_main_menu(self):
        self.root_dir_edit = urwid.Edit(('bold', "Root Directory: "), str(self.root_dir))
        scan_button = urwid.Button("Scan", on_press=self.on_scan)

        main_menu = urwid.Frame(
            header=urwid.Text(('bold', "RepoSnap - Main Menu")),
            body=urwid.Padding(
                urwid.LineBox(
                    urwid.ListBox(
                        urwid.SimpleFocusListWalker([
                            self.root_dir_edit
                        ])
                    ),
                    title="Enter Root Directory"
                ),
                left=2, right=2
            ),
            footer=urwid.Padding(scan_button, align='center')
        )

        self.main_widget = main_menu

    def on_scan(self, button):
        self.root_dir = Path(self.root_dir_edit.edit_text).resolve()
        self.controller.set_root_dir(self.root_dir)
        self.controller.collect_file_tree()
        self.file_tree = self.controller.get_file_tree()
        self.build_file_tree_menu()

    def build_file_tree_menu(self):
        tree_widgets = self.build_tree_widget(self.file_tree.structure)
        tree_listbox = urwid.ListBox(urwid.SimpleFocusListWalker(tree_widgets))
        render_button = urwid.Button("Render", on_press=self.on_render)

        tree_menu = urwid.Frame(
            header=urwid.Text(('bold', f"File Tree of {self.root_dir}")),
            body=urwid.LineBox(tree_listbox),
            footer=urwid.Padding(render_button, align='center')
        )

        self.main_widget = tree_menu
        self.refresh()

    def build_tree_widget(self, tree_structure, parent_path="", level=0):
        widgets = []
        for key, value in sorted(tree_structure.items()):
            node_path = f"{parent_path}/{key}".lstrip('/')
            checkbox = MyCheckBox(
                key,
                user_data={'path': node_path, 'level': level},
                state=False,
                on_state_change=self.on_checkbox_change
            )
            indented_checkbox = urwid.Padding(checkbox, left=4*level)
            widgets.append(indented_checkbox)
            if isinstance(value, dict):
                widgets.extend(self.build_tree_widget(value, node_path, level=level+1))
        return widgets

    def on_checkbox_change(self, checkbox, state):
        user_data = checkbox.user_data
        node_path = user_data['path']
        level = user_data['level']
        if state:
            self.selected_files.add(node_path)
        else:
            self.selected_files.discard(node_path)
        # Handle toggling all children
        self.toggle_children(checkbox, state, level)

    def toggle_children(self, checkbox, state, level):
        listbox = self.main_widget.body.original_widget.body
        walker = listbox
        # Find the index of the Padding widget that contains the checkbox
        idx = None
        for i, widget in enumerate(walker):
            if isinstance(widget, urwid.Padding) and widget.original_widget == checkbox:
                idx = i
                break
        if idx is None:
            return
        idx += 1
        while idx < len(walker):
            widget = walker[idx]
            if isinstance(widget, urwid.Padding):
                checkbox_widget = widget.original_widget
                widget_user_data = checkbox_widget.user_data
                widget_level = widget_user_data['level']
                if widget_level > level:
                    checkbox_widget.set_state(state, do_callback=False)
                    node_path = widget_user_data['path']
                    if state:
                        self.selected_files.add(node_path)
                    else:
                        self.selected_files.discard(node_path)
                    idx += 1
                else:
                    break
            else:
                idx += 1

    def on_render(self, button):
        self.controller.generate_output_from_selected(self.selected_files)
        message = urwid.Text(('bold', f"Markdown generated at {self.controller.output_file}"))
        exit_button = urwid.Button("Exit", on_press=self.exit_program)
        result_menu = urwid.Frame(
            header=urwid.Text(('bold', "Success")),
            body=urwid.Filler(message, valign='middle'),
            footer=urwid.Padding(exit_button, align='center')
        )
        self.main_widget = result_menu
        self.refresh()

    def refresh(self):
        if self.main_loop:
            self.main_loop.widget = self.main_widget

    def exit_program(self, button):
        raise urwid.ExitMainLoop()

    def run(self):
        self.main_loop = urwid.MainLoop(self.main_widget)
        self.main_loop.run()


def main():
    app = RepoSnapGUI()
    app.run()


if __name__ == "__main__":
    main()
