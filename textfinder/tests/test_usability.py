import os
import tempfile
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from search_engine import search_files

def test_supported_extensions():
    print("\n=== TEST USABILITY: supported extensions ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        txt = os.path.join(tmpdir, "file.txt")
        with open(txt, "w") as f:
            f.write("test")
        py = os.path.join(tmpdir, "script.py")
        with open(py, "w") as f:
            f.write("test")
        unknown = os.path.join(tmpdir, "file.xyz")
        with open(unknown, "w") as f:
            f.write("test")
        results = search_files(tmpdir, "test")
        found = [p for p,_ in results]
        print("Found files:", [os.path.basename(p) for p in found])
        if txt in found and py in found and unknown not in found:
            print("[OK] .txt and .py are processed, .xyz is ignored.")
            return True
        else:
            print("[FAIL] Extension handling is incorrect.")
            return False

def test_whole_word_mode():
    print("\n--- Whole word mode test ---")
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write("project projecting project")
        normal = search_files(tmpdir, "project", whole_word=False)
        whole = search_files(tmpdir, "project", whole_word=True)
        print("Normal search found", len(normal), "file(s)")
        print("Whole word search found", len(whole), "file(s)")
        # Create a file with only "projecting" (no standalone "project")
        path2 = os.path.join(tmpdir, "test2.txt")
        with open(path2, "w", encoding="utf-8") as f:
            f.write("projecting")
        whole2 = search_files(tmpdir, "project", whole_word=True)
        if len(whole2) == 1:  # only the first file contains standalone "project"
            print("[OK] Whole word mode works correctly.")
            return True
        else:
            print("[FAIL] Whole word mode found", len(whole2), "files, expected 1.")
            return False

if __name__ == "__main__":
    ok1 = test_supported_extensions()
    ok2 = test_whole_word_mode()
    sys.exit(0 if (ok1 and ok2) else 1)