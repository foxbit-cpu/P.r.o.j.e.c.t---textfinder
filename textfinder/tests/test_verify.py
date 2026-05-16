import os
import tempfile
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from search_engine import search_files

def test_verify_basic():
    print("\n=== TEST VERIFICATION: search by content ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = os.path.join(tmpdir, "hello.txt")
        with open(file1, "w", encoding="utf-8") as f:
            f.write("Hello world")
        file2 = os.path.join(tmpdir, "python.txt")
        with open(file2, "w", encoding="utf-8") as f:
            f.write("Python is great")
        subdir = os.path.join(tmpdir, "sub")
        os.mkdir(subdir)
        file3 = os.path.join(subdir, "secret.txt")
        with open(file3, "w", encoding="utf-8") as f:
            f.write("Hello again, secret word: apple")

        results = search_files(tmpdir, "hello")
        found_paths = [p for p, _ in results]
        print("Found files:", [os.path.basename(p) for p in found_paths])
        print("Expected: hello.txt and secret.txt")
        if file1 in found_paths and file3 in found_paths and file2 not in found_paths:
            print("[OK] Test passed: search found correct files.")
            return True
        else:
            print("[FAIL] Test failed: file list does not match.")
            return False

def test_verify_case_insensitive():
    print("\n--- Additional: case insensitivity ---")
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "case.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write("Hello World")
        results_lower = search_files(tmpdir, "hello")
        results_upper = search_files(tmpdir, "HELLO")
        if len(results_lower) == 1 and len(results_upper) == 1:
            print("[OK] Search is case-insensitive.")
            return True
        else:
            print("[FAIL] Case insensitivity does not work.")
            return False

if __name__ == "__main__":
    ok1 = test_verify_basic()
    ok2 = test_verify_case_insensitive()
    sys.exit(0 if (ok1 and ok2) else 1)