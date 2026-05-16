import os
import tempfile
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from search_engine import search_files

def test_nonexistent_folder():
    print("\n=== TEST VALIDATION: non-existent folder ===")
    results = search_files("Z:/nonexistent/folder/12345", "anything")
    if results == []:
        print("[OK] Program returned empty list without crashing.")
        return True
    else:
        print("[FAIL] Expected empty list, got something else.")
        return False

def test_empty_query():
    print("\n--- Empty search query ---")
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.txt")
        with open(path, "w") as f:
            f.write("data")
        results = search_files(tmpdir, "")
        if results == []:
            print("[OK] Empty query returns empty list.")
            return True
        else:
            print("[FAIL] Empty query should not find anything.")
            return False

def test_binary_file_skip():
    print("\n--- Binary files should not break search ---")
    with tempfile.TemporaryDirectory() as tmpdir:
        binpath = os.path.join(tmpdir, "binary.bin")
        with open(binpath, "wb") as f:
            f.write(b'\x00\x01\x02\x03')
        txtpath = os.path.join(tmpdir, "text.txt")
        with open(txtpath, "w") as f:
            f.write("hello")
        results = search_files(tmpdir, "hello")
        if len(results) == 1 and results[0][0] == txtpath:
            print("[OK] Search skipped binary file and found text file.")
            return True
        else:
            print("[FAIL] Binary file caused problem or result mismatch.")
            return False

if __name__ == "__main__":
    ok1 = test_nonexistent_folder()
    ok2 = test_empty_query()
    ok3 = test_binary_file_skip()
    sys.exit(0 if (ok1 and ok2 and ok3) else 1)