import os
import time
import tracemalloc
import sys

# Переключаемся в папку, где лежит этот скрипт
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

sys.path.insert(0, os.path.dirname(script_dir))  # добавляем родительскую папку для импорта search_engine
from search_engine import search_files

def measure(folder, description):
    print(f"\nMeasuring: {description} (folder: {folder})")
    tracemalloc.start()
    start = time.perf_counter()
    results = search_files(folder, "special_keyword", whole_word=False)
    end = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    elapsed = end - start
    print(f"  Time: {elapsed:.3f} sec")
    print(f"  Peak memory: {peak / 1024 / 1024:.2f} MB")
    print(f"  Files found: {len(results)}")
    return elapsed, peak

if __name__ == "__main__":
    base = "test_load"
    counts = [10, 100, 1000]
    results = []
    for c in counts:
        folder = os.path.join(base, f"files_{c}")
        if not os.path.exists(folder):
            print(f"Please generate test data first: python generate_text_files.py {folder} {c}")
            continue
        elapsed, peak = measure(folder, f"{c} files")
        results.append((c, elapsed, peak))
    print("\nPerformance Table:")
    print("| File count | Time (sec) | Peak memory (MB) |")
    print("|------------|------------|------------------|")
    for c, e, p in results:
        print(f"| {c} | {e:.3f} | {p/1024/1024:.2f} |")