# tests/reposnap/test_gui.py

import pytest
import urwid
from unittest.mock import patch, MagicMock
from urwid import ExitMainLoop
from reposnap.interfaces.gui import RepoSnapGUI
from pathlib import Path


@pytest.fixture
def gui_app():
    app = RepoSnapGUI()
    app.main_loop = MagicMock()
    app.main_loop.widget = None  # Initialize the widget attribute
    return app


def test_initial_state(gui_app):
    assert isinstance(gui_app.main_widget, gui_app.main_widget.__class__)
    assert gui_app.root_dir == Path('.').resolve()


def test_scan_button(gui_app):
    with patch.object(gui_app.controller, 'set_root_dir') as mock_set_root_dir, \
         patch.object(gui_app.controller, 'collect_file_tree') as mock_collect_file_tree, \
         patch.object(gui_app.controller, 'get_file_tree') as mock_get_file_tree:

        mock_get_file_tree.return_value = MagicMock(structure={
            'dir1': {
                'file1.py': None,
                'dir2': {
                    'file2.py': None
                }
            },
            'file3.py': None
        })

        # Simulate pressing the "Scan" button
        gui_app.on_scan(None)

        mock_set_root_dir.assert_called_once_with(gui_app.root_dir)
        mock_collect_file_tree.assert_called_once()
        mock_get_file_tree.assert_called_once()
        assert gui_app.file_tree is not None

        # Ensure that main_widget is updated without errors
        assert isinstance(gui_app.main_widget, urwid.Frame)


def test_render_button(gui_app):
    with patch.object(gui_app.controller, 'generate_output_from_selected') as mock_generate_output:
        # Simulate setting up the file tree
        gui_app.file_tree = MagicMock()
        gui_app.file_tree.structure = {}
        gui_app.selected_files = {'file1.py', 'dir/file2.py'}

        # Build the file tree menu to initialize widgets
        gui_app.build_file_tree_menu()

        # Simulate pressing the "Render" button
        gui_app.on_render(None)

        mock_generate_output.assert_called_once_with(gui_app.selected_files)
        # Check that the main_widget has been updated to the result menu
        assert 'Markdown generated at' in gui_app.main_widget.body.base_widget.text


def test_exit_program(gui_app):
    with pytest.raises(ExitMainLoop):
        gui_app.exit_program(None)


def test_toggle_children(gui_app):
    # Setup the file tree structure
    gui_app.file_tree = MagicMock()
    gui_app.file_tree.structure = {
        'dir1': {
            'file1.py': None,
            'dir2': {
                'file2.py': None
            }
        },
        'file3.py': None
    }

    # Build the file tree menu to initialize widgets
    gui_app.build_file_tree_menu()

    # Simulate toggling a parent checkbox
    listbox = gui_app.main_widget.body.original_widget.body
    parent_padding = listbox[0]  # The first item is Padding wrapping the checkbox
    parent_checkbox = parent_padding.original_widget
    gui_app.on_checkbox_change(parent_checkbox, True)

    # Check that child checkboxes are also toggled
    child_padding = listbox[1]
    child_checkbox = child_padding.original_widget
    assert child_checkbox.get_state() is True

    # Check that selected_files contains both parent and child paths
    expected_selected_files = {'dir1', 'dir1/file1.py', 'dir1/dir2', 'dir1/dir2/file2.py'}
    assert gui_app.selected_files == expected_selected_files
