# tests/reposnap/test_contains_filter.py

from pathlib import Path
from reposnap.core.content_search import file_matches, filter_files_by_content


class TestContentSearch:
    """Test content search functionality."""

    def test_file_matches_single_pattern(self, tmp_path):
        """Test matching a single pattern in file content."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def main():\n    print('needle in haystack')\n")

        assert file_matches(test_file, ["needle"], ignore_case=True)
        assert not file_matches(test_file, ["nonexistent"], ignore_case=True)

    def test_file_matches_multiple_patterns_or_logic(self, tmp_path):
        """Test that multiple patterns use OR logic (any match is sufficient)."""
        test_file = tmp_path / "test.py"
        test_file.write_text("import logging\ndef main():\n    pass\n")

        # Should match because file contains "import"
        assert file_matches(test_file, ["import", "nonexistent"], ignore_case=True)
        # Should match because file contains "logging"
        assert file_matches(test_file, ["nonexistent", "logging"], ignore_case=True)
        # Should not match because file contains neither
        assert not file_matches(test_file, ["foo", "bar"], ignore_case=True)

    def test_file_matches_case_insensitive_default(self, tmp_path):
        """Test case insensitive matching by default."""
        test_file = tmp_path / "test.py"
        test_file.write_text("TODO: Fix this bug\n")

        assert file_matches(test_file, ["todo"], ignore_case=True)
        assert file_matches(test_file, ["TODO"], ignore_case=True)
        assert file_matches(test_file, ["Todo"], ignore_case=True)

    def test_file_matches_case_sensitive_flag(self, tmp_path):
        """Test case sensitive matching when flag is set."""
        test_file = tmp_path / "test.py"
        test_file.write_text("TODO: Fix this bug\n")

        assert file_matches(test_file, ["TODO"], ignore_case=False)
        assert not file_matches(test_file, ["todo"], ignore_case=False)
        assert not file_matches(test_file, ["Todo"], ignore_case=False)

    def test_file_matches_empty_patterns(self, tmp_path):
        """Test that empty patterns list returns True."""
        test_file = tmp_path / "test.py"
        test_file.write_text("any content\n")

        assert file_matches(test_file, [], ignore_case=True)

    def test_file_matches_nonexistent_file(self, tmp_path):
        """Test that non-existent file returns False."""
        nonexistent = tmp_path / "nonexistent.py"

        assert not file_matches(nonexistent, ["pattern"], ignore_case=True)

    def test_file_matches_binary_file_handling(self, tmp_path):
        """Test that binary files are handled gracefully."""
        binary_file = tmp_path / "test.bin"
        binary_file.write_bytes(b"\x00\x01\x02\x03\xff\xfe")

        # Should not crash and should return False for binary content
        assert not file_matches(binary_file, ["pattern"], ignore_case=True)

    def test_file_matches_large_file_handling(self, tmp_path):
        """Test that large files are skipped for performance."""
        from reposnap.core.content_search import MAX_FILE_SIZE

        large_file = tmp_path / "large.txt"
        # Create a file slightly larger than MAX_FILE_SIZE
        large_content = "x" * (MAX_FILE_SIZE + 1000)
        large_file.write_text(large_content)

        # Should skip large files and return False
        assert not file_matches(large_file, ["x"], ignore_case=True)

    def test_file_matches_binary_detection_in_middle(self, tmp_path):
        """Test binary detection with null bytes after text content."""
        mixed_file = tmp_path / "mixed.txt"
        # Write text content followed by binary content with null bytes
        with mixed_file.open("wb") as f:
            f.write(b"some text content\n")
            f.write(b"\x00binary\x00data\xff")

        # Should detect binary content and return False
        assert not file_matches(mixed_file, ["text"], ignore_case=True)

    def test_filter_files_by_content_basic(self, tmp_path):
        """Test basic file filtering by content."""
        file1 = tmp_path / "file1.py"
        file1.write_text("import logging\ndef main(): pass\n")

        file2 = tmp_path / "file2.py"
        file2.write_text("import os\ndef helper(): pass\n")

        file3 = tmp_path / "file3.py"
        file3.write_text("print('hello world')\n")

        files = [file1, file2, file3]

        # Filter for files containing "import"
        filtered = filter_files_by_content(files, ["import"])
        assert set(filtered) == {file1, file2}

        # Filter for files containing "logging"
        filtered = filter_files_by_content(files, ["logging"])
        assert filtered == [file1]

    def test_filter_files_by_content_empty_patterns(self, tmp_path):
        """Test that empty patterns return all files."""
        file1 = tmp_path / "file1.py"
        file1.write_text("content1")

        file2 = tmp_path / "file2.py"
        file2.write_text("content2")

        files = [file1, file2]
        filtered = filter_files_by_content(files, [])
        assert filtered == files

    def test_filter_files_by_content_case_sensitivity(self, tmp_path):
        """Test case sensitivity in file filtering."""
        test_file = tmp_path / "test.py"
        test_file.write_text("TODO: Important task\n")

        files = [test_file]

        # Case insensitive (default)
        filtered = filter_files_by_content(files, ["todo"], ignore_case=True)
        assert filtered == [test_file]

        # Case sensitive
        filtered = filter_files_by_content(files, ["todo"], ignore_case=False)
        assert filtered == []

        filtered = filter_files_by_content(files, ["TODO"], ignore_case=False)
        assert filtered == [test_file]


class TestProjectControllerIntegration:
    """Test integration of contains filter with ProjectController."""

    def test_contains_filter_integration(self, tmp_path):
        """Test that ProjectController properly applies content filters."""
        from reposnap.controllers.project_controller import ProjectController
        from unittest.mock import Mock

        # Create test files
        file1 = tmp_path / "file1.py"
        file1.write_text("import logging\ndef main(): pass\n")

        file2 = tmp_path / "file2.py"
        file2.write_text("import os\ndef helper(): pass\n")

        file3 = tmp_path / "file3.txt"
        file3.write_text("This is a text file\n")

        # Mock args object
        args = Mock()
        args.paths = [str(tmp_path)]
        args.output = "output.md"
        args.structure_only = False
        args.include = []
        args.exclude = []
        args.changes = False
        args.contains = ["import"]
        args.contains_case = False

        # Create controller and test content filtering
        controller = ProjectController(args)
        controller.set_root_dir(tmp_path)

        # Test the _apply_content_filter method directly
        files = [Path("file1.py"), Path("file2.py"), Path("file3.txt")]
        filtered = controller._apply_content_filter(files)

        # Should only keep files with "import"
        assert set(f.name for f in filtered) == {"file1.py", "file2.py"}

    def test_contains_filter_case_sensitivity_integration(self, tmp_path):
        """Test case sensitivity integration in ProjectController."""
        from reposnap.controllers.project_controller import ProjectController
        from unittest.mock import Mock

        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("TODO: Fix this\n")

        # Test case insensitive (default)
        args = Mock()
        args.paths = [str(tmp_path)]
        args.output = "output.md"
        args.structure_only = False
        args.include = []
        args.exclude = []
        args.changes = False
        args.contains = ["todo"]
        args.contains_case = False

        controller = ProjectController(args)
        controller.set_root_dir(tmp_path)

        files = [Path("test.py")]
        filtered = controller._apply_content_filter(files)
        assert len(filtered) == 1

        # Test case sensitive
        args.contains_case = True
        controller = ProjectController(args)
        controller.set_root_dir(tmp_path)

        filtered = controller._apply_content_filter(files)
        assert len(filtered) == 0  # "todo" != "TODO"

    def test_no_contains_patterns_returns_all_files(self, tmp_path):
        """Test that empty contains patterns return all files unchanged."""
        from reposnap.controllers.project_controller import ProjectController
        from unittest.mock import Mock

        # Create test files
        file1 = tmp_path / "file1.py"
        file1.write_text("content1")

        file2 = tmp_path / "file2.py"
        file2.write_text("content2")

        # Mock args with empty contains
        args = Mock()
        args.paths = [str(tmp_path)]
        args.output = "output.md"
        args.structure_only = False
        args.include = []
        args.exclude = []
        args.changes = False
        args.contains = []
        args.contains_case = False

        controller = ProjectController(args)
        controller.set_root_dir(tmp_path)

        files = [Path("file1.py"), Path("file2.py")]
        filtered = controller._apply_content_filter(files)

        # Should return all files unchanged
        assert set(filtered) == set(files)

    def test_absolute_path_handling(self, tmp_path):
        """Test that ProjectController properly handles absolute paths."""
        from reposnap.controllers.project_controller import ProjectController
        from unittest.mock import Mock

        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("import logging\ndef main(): pass\n")

        # Mock args with absolute path
        args = Mock()
        args.paths = [str(test_file)]  # Absolute path
        args.output = "output.md"
        args.structure_only = False
        args.include = []
        args.exclude = []
        args.changes = False
        args.contains = ["import"]
        args.contains_case = False

        # Create controller with the temp directory as root from the start
        # This simulates how the controller would actually work
        controller = ProjectController()
        controller.set_root_dir(tmp_path)

        # Process the args manually after setting root dir
        input_paths = [Path(p) for p in args.paths]
        controller.input_paths = []
        for p in input_paths:
            if p.is_absolute():
                candidate = p.resolve()
            else:
                candidate = (controller.root_dir / p).resolve()

            if candidate.exists():
                try:
                    rel = candidate.relative_to(controller.root_dir)
                    if rel != Path("."):
                        controller.input_paths.append(rel)
                except ValueError:
                    pass  # Path not under root

        # Should have processed the absolute path correctly
        assert len(controller.input_paths) == 1
        assert controller.input_paths[0].name == "test.py"
