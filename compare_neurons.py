import os
import sys
import time
import math
import random
import shutil
import argparse
import subprocess
from pathlib import Path


def find_repo_root() -> Path:
    candidates = [
        Path(__file__).resolve().parent,
        Path(__file__).resolve().parent / "Stochastic-Neuron-Verilog-",
        Path.cwd(),
        Path.cwd() / "Stochastic-Neuron-Verilog-",
    ]
    for c in candidates:
        if (c / "Classical Neuron").is_dir() and (c / "Stochastic Neuron").is_dir():
            return c
    raise FileNotFoundError(
        "Could not locate the 'Stochastic-Neuron-Verilog-' repository directory. "
        "Please ensure 'Classical Neuron' and 'Stochastic Neuron' directories exist."
    )


def check_prerequisites():
    for tool in ["iverilog", "vvp"]:
        if shutil.which(tool) is None:
            sys.exit(
                f"[ERROR] Required tool '{tool}' not found in PATH.\n"
                f"Please install Icarus Verilog (e.g., 'sudo apt install iverilog')."
            )


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", type=int, required=True)
    parser.add_argument("-x", type=float, nargs="+", required=True)
    parser.add_argument("-w", type=float, nargs="+", required=True)
    parser.add_argument("-b", type=float, required=True)
    parser.add_argument("--cycles", type=int, required=True)
    return parser.parse_args()


def run_classical_neuron(repo_dir: Path, n: int, x: list, w: list, bias: float):
    classical_dir = repo_dir / "Classical Neuron"
    inputs_file = classical_dir / "classical_inputs.txt"
    sim_binary = classical_dir / "classical_sim"

    with open(inputs_file, "w") as f:
        f.write(f"{n}\n")
        f.write(" ".join(f"{val:.8f}" for val in x) + "\n")
        f.write(" ".join(f"{val:.8f}" for val in w) + "\n")
        f.write(f"{bias:.8f}\n")

    t_comp_start = time.perf_counter()
    compile_cmd = [
        "iverilog",
        "-g2012",
        f"-Ptb_classical_neuron_32bit.N={max(n, 100)}",
        "-o",
        str(sim_binary),
        "design.sv",
        "testbench.sv",
    ]
    comp_res = subprocess.run(
        compile_cmd, cwd=classical_dir, capture_output=True, text=True
    )
    t_comp_end = time.perf_counter()

    if comp_res.returncode != 0:
        raise RuntimeError(f"Classical Neuron compilation failed:\n{comp_res.stderr}")

    t_sim_start = time.perf_counter()
    sim_res = subprocess.run(
        ["vvp", str(sim_binary)],
        cwd=classical_dir,
        capture_output=True,
        text=True,
    )
    t_sim_end = time.perf_counter()

    if sim_res.returncode != 0:
        raise RuntimeError(f"Classical Neuron simulation failed:\n{sim_res.stderr}")

    raw_z = None
    dec_z = None
    bin_y = None
    dec_y = None

    for line in sim_res.stdout.splitlines():
        line_clean = line.strip()
        if line_clean.startswith("Raw output z"):
            raw_z = line_clean.split("=")[-1].strip()
        elif line_clean.startswith("Decimal z"):
            dec_z = float(line_clean.split("=")[-1].strip())
        elif line_clean.startswith("Neuron y (bin)"):
            bin_y = line_clean.split("=")[-1].strip()
        elif line_clean.startswith("Decimal y"):
            dec_y = float(line_clean.split("=")[-1].strip())

    timing = {
        "compile_time": t_comp_end - t_comp_start,
        "sim_time": t_sim_end - t_sim_start,
        "total_time": (t_comp_end - t_comp_start) + (t_sim_end - t_sim_start),
    }

    results = {
        "raw_z": raw_z,
        "decimal_z": dec_z,
        "binary_y": bin_y,
        "decimal_y": dec_y,
        "stdout": sim_res.stdout,
    }

    return results, timing


def run_stochastic_neuron(repo_dir: Path, n: int, x: list, w: list, bias: float, cycles: int):
    stochastic_dir = repo_dir / "Stochastic Neuron"
    bitstream_dir = repo_dir / "bitstream"
    inputs_file = bitstream_dir / "inputs.txt"
    sim_binary = stochastic_dir / "neuron_sim"
    output_file = stochastic_dir / "output.txt"

    t_gen_start = time.perf_counter()
    batch_size = 50000
    remaining = cycles

    with open(inputs_file, "w") as f:
        while remaining > 0:
            batch = min(remaining, batch_size)
            lines = []
            for _ in range(batch):
                x_str = "".join("1" if random.random() < p else "0" for p in x)
                w_str = "".join("1" if random.random() < p else "0" for p in w)
                b_str = "1" if random.random() < bias else "0"
                lines.append(f"{x_str} {w_str} {b_str}\n")
            f.writelines(lines)
            remaining -= batch
    t_gen_end = time.perf_counter()

    t_comp_start = time.perf_counter()
    compile_cmd = [
        "iverilog",
        f"-Ptb_sc_neuron.N={n}",
        "-o",
        str(sim_binary),
        "sc_neuron_testbench.v",
    ]
    comp_res = subprocess.run(
        compile_cmd, cwd=stochastic_dir, capture_output=True, text=True
    )
    t_comp_end = time.perf_counter()

    if comp_res.returncode != 0:
        raise RuntimeError(f"Stochastic Neuron compilation failed:\n{comp_res.stderr}")

    t_sim_start = time.perf_counter()
    sim_res = subprocess.run(
        ["vvp", str(sim_binary)],
        cwd=stochastic_dir,
        capture_output=True,
        text=True,
    )
    t_sim_end = time.perf_counter()

    if sim_res.returncode != 0:
        raise RuntimeError(f"Stochastic Neuron simulation failed:\n{sim_res.stderr}")

    t_parse_start = time.perf_counter()
    with open(output_file, "r") as f:
        stream = f.read()
    ones = stream.count("1")
    zeros = stream.count("0")
    total_bits = ones + zeros
    empirical_p = (ones / total_bits) if total_bits > 0 else 0.0
    t_parse_end = time.perf_counter()

    timing = {
        "gen_time": t_gen_end - t_gen_start,
        "compile_time": t_comp_end - t_comp_start,
        "sim_time": t_sim_end - t_sim_start,
        "parse_time": t_parse_end - t_parse_start,
        "total_time": (
            (t_gen_end - t_gen_start)
            + (t_comp_end - t_comp_start)
            + (t_sim_end - t_sim_start)
            + (t_parse_end - t_parse_start)
        ),
    }

    results = {
        "ones_count": ones,
        "zeros_count": zeros,
        "total_bits": total_bits,
        "probability": empirical_p,
        "stdout": sim_res.stdout,
    }

    return results, timing


def main():
    check_prerequisites()
    repo_dir = find_repo_root()

    args = parse_arguments()

    n = args.n
    x_probs = args.x
    w_probs = args.w
    bias = args.b
    cycles = args.cycles

    if n <= 0:
        sys.exit("[ERROR] -n must be a positive integer.")
    if cycles <= 0:
        sys.exit("[ERROR] --cycles must be a positive integer.")
    if len(x_probs) != n or len(w_probs) != n:
        sys.exit(f"[ERROR] Expected {n} values for -x and -w, got {len(x_probs)} and {len(w_probs)}.")
    if any(p < 0.0 or p > 1.0 for p in x_probs + w_probs + [bias]):
        sys.exit("[ERROR] All probabilities for -x, -w, and -b must be between 0.0 and 1.0.")

    print("\n" + "=" * 65)
    print("                 BENCHMARK CONFIGURATION")
    print("=" * 65)
    print(f" Number of Active Inputs (N) : {n}")
    print(f" Input Probabilities (X)     : {x_probs}")
    print(f" Weight Probabilities (W)    : {w_probs}")
    print(f" Bias Probability (B)        : {bias}")
    print(f" Stochastic Bitstream Length : {cycles:,} cycles")
    print("=" * 65)

    print("\n[*] Simulating Classical Fixed-Point Neuron (SystemVerilog)...")
    res_classical, time_classical = run_classical_neuron(repo_dir, n, x_probs, w_probs, bias)
    print(f"    ✓ Classical simulation complete in {time_classical['total_time']:.4f}s")

    print("\n[*] Simulating Stochastic Computing Neuron (Verilog)...")
    res_stochastic, time_stochastic = run_stochastic_neuron(repo_dir, n, x_probs, w_probs, bias, cycles)
    print(f"    ✓ Stochastic simulation complete in {time_stochastic['total_time']:.4f}s")

    shift_bits = math.ceil(math.log2(n + 1))
    scale_factor = 2 ** shift_bits

    raw_sum_ideal = sum(xi * wi for xi, wi in zip(x_probs, w_probs)) + bias
    ideal_y = min(1.0, raw_sum_ideal / scale_factor)

    y_classical = res_classical["decimal_y"]
    y_stochastic = res_stochastic["probability"]

    err_classical_vs_ideal = abs(y_classical - ideal_y)
    err_stochastic_vs_ideal = abs(y_stochastic - ideal_y)
    diff_stochastic_vs_classical = abs(y_stochastic - y_classical)

    acc_classical_pct = max(0.0, (1.0 - (err_classical_vs_ideal / ideal_y)) * 100.0) if ideal_y > 0 else 100.0
    acc_stochastic_pct = max(0.0, (1.0 - (err_stochastic_vs_ideal / ideal_y)) * 100.0) if ideal_y > 0 else 100.0

    print("\n" + "=" * 65)
    print("                   OUTPUT & ACCURACY COMPARISON")
    print("=" * 65)
    print(f" Theoretical Target (Ideal Math)  : {ideal_y:.6f}  (Scale Factor: 1/{scale_factor})")
    print(f" Classical Neuron Output (Verilog): {y_classical:.6f}  (Binary: {res_classical['binary_y']})")
    print(f" Stochastic Neuron Output (Verilog): {y_stochastic:.6f}  (1s: {res_stochastic['ones_count']:,} / {res_stochastic['total_bits']:,})")
    print("-" * 65)
    print(" ACCURACY & ERROR METRICS:")
    print(f"   • Classical vs Ideal Absolute Error  : {err_classical_vs_ideal:.6e} ({acc_classical_pct:.4f}% accuracy)")
    print(f"   • Stochastic vs Ideal Absolute Error : {err_stochastic_vs_ideal:.6e} ({acc_stochastic_pct:.4f}% accuracy)")
    print(f"   • Stochastic vs Classical Difference: {diff_stochastic_vs_classical:.6e}")
    if y_classical > 0:
        rel_diff_pct = (diff_stochastic_vs_classical / y_classical) * 100.0
        print(f"   • Relative Discrepancy (SC vs Fixed) : {rel_diff_pct:.4f}%")
    print("=" * 65)

    print("\n" + "=" * 65)
    print("                   RUNTIME PERFORMANCE COMPARISON")
    print("=" * 65)
    print(f" {'Metric / Phase':<30} | {'Classical (32-bit)':<15} | {'Stochastic (SC)':<15}")
    print("-" * 65)
    print(f" {'Bitstream / Input Prep':<30} | {'N/A':<15} | {time_stochastic['gen_time']:<15.4f}s")
    print(f" {'Verilog Compilation (iverilog)':<30} | {time_classical['compile_time']:<15.4f}s | {time_stochastic['compile_time']:<15.4f}s")
    print(f" {'Hardware Simulation (vvp)':<30} | {time_classical['sim_time']:<15.4f}s | {time_stochastic['sim_time']:<15.4f}s")
    print(f" {'Output Analysis / Bit Counting':<30} | {'N/A':<15} | {time_stochastic['parse_time']:<15.4f}s")
    print("-" * 65)
    print(f" {'Total Execution Time':<30} | {time_classical['total_time']:<15.4f}s | {time_stochastic['total_time']:<15.4f}s")
    print("=" * 65)

    sim_ratio = (time_stochastic['sim_time'] / time_classical['sim_time']) if time_classical['sim_time'] > 0 else 0
    total_ratio = (time_stochastic['total_time'] / time_classical['total_time']) if time_classical['total_time'] > 0 else 0

    print(f"\n [Speedup Summary]")
    print(f"   • Simulation Speedup (Classical vs SC): {sim_ratio:.1f}x faster in simulation")
    print(f"   • Total End-to-End Speedup            : {total_ratio:.1f}x faster in overall execution\n")


if __name__ == "__main__":
    main()
