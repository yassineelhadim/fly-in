#!/usr/bin/env python3
import random
import shutil
import string
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


ROOT = Path(__file__).resolve().parent


def run_case(case_name: str, content: str, timeout: int = 8) -> Tuple[int, str, str]:
    temp_dir = ROOT / "maps" / "__tmp_harness__"
    temp_dir.mkdir(parents=True, exist_ok=True)
    case_path = temp_dir / case_name
    case_path.write_text(content, encoding="utf-8")

    try:
        result = subprocess.run(
            [sys.executable, str(ROOT / "main.py"), str(case_path)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return -999, "TIMEOUT", ""

    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()
    combined = "\n".join(filter(None, [stdout, stderr]))
    return result.returncode, combined, str(case_path)


def cleanup_temp_dir() -> None:
    temp_dir = ROOT / "maps" / "__tmp_harness__"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


def run_targeted_cases() -> List[Tuple[str, int, str]]:
    cases: Dict[str, str] = {
        "valid_minimal.txt": """nb_drones: 1
start_hub: s 0 0
end_hub: e 1 0
connection: s-e
""",
        "missing_nb_drones.txt": """start_hub: s 0 0
end_hub: e 1 0
connection: s-e
""",
        "zero_drones.txt": """nb_drones: 0
start_hub: s 0 0
end_hub: e 1 0
connection: s-e
""",
        "negative_drones.txt": """nb_drones: -3
start_hub: s 0 0
end_hub: e 1 0
connection: s-e
""",
        "duplicate_start.txt": """nb_drones: 1
start_hub: s 0 0
start_hub: s2 0 1
end_hub: e 1 0
connection: s-e
""",
        "duplicate_zone_name.txt": """nb_drones: 1
start_hub: s 0 0
hub: s 0 1
end_hub: e 1 0
connection: s-e
""",
        "unknown_zone_in_connection.txt": """nb_drones: 1
start_hub: s 0 0
end_hub: e 1 0
connection: s-x
""",
        "duplicate_connection_reverse.txt": """nb_drones: 1
start_hub: s 0 0
hub: a 1 0
end_hub: e 2 0
connection: s-a
connection: a-s
connection: a-e
""",
        "invalid_connection_syntax.txt": """nb_drones: 1
start_hub: s 0 0
end_hub: e 1 0
connection: s-e-x
""",
        "invalid_metadata.txt": """nb_drones: 1
start_hub: s 0 0 [zone]
end_hub: e 1 0
connection: s-e
""",
        "invalid_zone_type.txt": """nb_drones: 1
start_hub: s 0 0 [zone=teleport]
end_hub: e 1 0
connection: s-e
""",
        "invalid_coords.txt": """nb_drones: 1
start_hub: s x 0
end_hub: e 1 0
connection: s-e
""",
        "invalid_max_drones.txt": """nb_drones: 1
start_hub: s 0 0 [max_drones=0]
end_hub: e 1 0
connection: s-e
""",
        "invalid_link_capacity.txt": """nb_drones: 1
start_hub: s 0 0
end_hub: e 1 0
connection: s-e [max_link_capacity=0]
""",
        "blocked_path_no_solution.txt": """nb_drones: 2
start_hub: s 0 0
hub: b 1 0 [zone=blocked]
end_hub: e 2 0
connection: s-b
connection: b-e
""",
        "disconnected_graph_no_solution.txt": """nb_drones: 2
start_hub: s 0 0
hub: a 1 0
end_hub: e 4 0
hub: z 5 0
connection: s-a
connection: e-z
""",
        "loop_graph.txt": """nb_drones: 3
start_hub: s 0 0
hub: a 1 0
hub: b 2 0
hub: c 1 1
end_hub: e 3 0
connection: s-a
connection: a-b
connection: b-c
connection: c-a
connection: b-e
""",
        "end_capacity_one_many_drones.txt": """nb_drones: 6
start_hub: s 0 0 [max_drones=99]
hub: a 1 0 [max_drones=1]
end_hub: e 2 0 [max_drones=1]
connection: s-a [max_link_capacity=1]
connection: a-e [max_link_capacity=1]
""",
        "invalid_color.txt": """nb_drones: 1
start_hub: s 0 0 [color=notacolor]
end_hub: e 1 0
connection: s-e
""",
    }

    results: List[Tuple[str, int, str]] = []
    for case_name in sorted(cases):
        code, combined, _ = run_case(case_name, cases[case_name])
        preview = " | ".join(combined.splitlines()[:3])
        results.append((case_name, code, preview))
    return results


def run_fuzz_cases(count: int = 40, timeout: int = 2) -> List[Tuple[int, str]]:
    random.seed(42)
    chars = string.ascii_letters + string.digits + ":-_[]#= \n"
    results: List[Tuple[int, str]] = []

    for index in range(count):
        content = "".join(random.choice(chars) for _ in range(random.randint(10, 400)))
        case_name = f"fuzz_{index:02d}.txt"
        code, combined, _ = run_case(case_name, content, timeout=timeout)
        summary = "TRACEBACK" if "Traceback (most recent call last):" in combined else (
            "TIMEOUT" if code == -999 else f"exit={code}"
        )
        results.append((code, summary))
    return results


def main() -> None:
    print("Starting map parsing/algo harness...")
    try:
        targeted_results = run_targeted_cases()
        print("\n=== TARGETED CASES ===")
        for case_name, code, preview in targeted_results:
            print(f"{case_name}: exit={code}")
            if preview:
                print(f"  {preview}")

        fuzz_results = run_fuzz_cases()
        print("\n=== FUZZ SUMMARY ===")
        print(f"total={len(fuzz_results)}")
        print(f"timeouts={sum(1 for code, _ in fuzz_results if code == -999)}")
        print(f"tracebacks={sum(1 for code, summary in fuzz_results if summary == 'TRACEBACK')}")
        print(f"success_exit0={sum(1 for code, summary in fuzz_results if code == 0)}")
        print(f"error_exit1={sum(1 for code, summary in fuzz_results if code == 1)}")
    finally:
        cleanup_temp_dir()


if __name__ == "__main__":
    main()
