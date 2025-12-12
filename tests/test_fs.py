from fs_explorer.fs import (
    describe_dir_content,
    read_file,
    grep_file_content,
    glob_paths,
)


def test_describe_dir_content() -> None:
    description = describe_dir_content("tests/testfiles")
    assert (
        description
        == "Content of tests/testfiles\nFILES:\n- tests/testfiles/file1.txt\n- tests/testfiles/file2.md\nSUBFOLDERS:\n- tests/testfiles/last"
    )
    description = describe_dir_content("tests/testfile")
    assert description == f"No such directory: tests/testfile"
    description = describe_dir_content("tests/testfiles/last")
    assert (
        description
        == "Content of tests/testfiles/last\nFILES:\n- tests/testfiles/last/lastfile.txt\nThis folder does not have any sub-folders"
    )


def test_read_file() -> None:
    content = read_file("tests/testfiles/file1.txt")
    assert content.strip() == "this is a test"
    content = read_file("tests/testfiles/file2.txt")
    assert content.strip() == "No such file: tests/testfiles/file2.txt"


def test_grep_file_content() -> None:
    result = grep_file_content("tests/testfiles/file2.md", r"(are|is) a test")
    assert result == "MATCHES for (are|is) a test in tests/testfiles/file2.md:\n\n- is"
    result = grep_file_content("tests/testfiles/last/lastfile.txt", r"test")
    assert result == "No matches found"
    result = grep_file_content("tests/testfiles/file2.txt", r"test")
    assert result == "No such file: tests/testfiles/file2.txt"


def test_glob_paths() -> None:
    result = glob_paths("tests/testfiles", "file?.*")
    assert (
        result
        == "MATCHES for file?.* in tests/testfiles:\n\n- ./tests/testfiles/file1.txt\n- ./tests/testfiles/file2.md"
    )
    result = glob_paths("tests/testfiles", "test*")
    assert result == "No matches found"
