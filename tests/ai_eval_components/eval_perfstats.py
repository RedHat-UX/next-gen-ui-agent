import json
import sys

import numpy as np

perf_stats: dict[str, list] = {"all": []}


def report_perf_stats(time_start: int, time_end: int, component: str):
    """Report performance for one evaluation run"""
    time = time_end - time_start
    perf_stats["all"].append(time)
    if component not in perf_stats:
        perf_stats[component] = []
    perf_stats[component].append(time)


def compute_perf_status(times: list[int]):
    """Compute performance stats from array of runtime times"""
    sd = np.array(times)
    ret = {
        "min": round(np.min(sd)),
        "mean": round(np.mean(sd)),
        "avg": round(np.average(sd)),
        "perc95": round(np.percentile(sd, 95)),
        "max": round(np.max(sd)),
    }
    return ret


def get_perf_stat_all():
    """Get performance stats over all components"""
    return compute_perf_status(perf_stats["all"])


def get_perf_stat_for_components():
    ret = {}
    for key in perf_stats:
        if key != "all":
            ret[key] = compute_perf_status(perf_stats[key])
    return ret


def print_perf_stats():
    """Print performance stats to stdout"""
    print("Performance stats [ms]:")
    json.dump(get_perf_stat_all(), sys.stdout, indent=2, separators=(",", ": "))
    print("\n\nPerformance stats per component [ms]:")
    json.dump(
        get_perf_stat_for_components(), sys.stdout, indent=2, separators=(",", ": ")
    )
    print("")


if __name__ == "__main__":
    # dev code only
    report_perf_stats(12, 25, "c1")
    report_perf_stats(149, 187, "c2")
    report_perf_stats(12, 28, "c1")

    print_perf_stats()
