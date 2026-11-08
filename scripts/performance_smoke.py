import json
import statistics
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"
SAMPLES = 40
MAX_P95_MS = 500
REPORT = Path("reports/performance-smoke.json")


def request_health():
    request = urllib.request.Request(f"{BASE_URL}/health", headers={"Accept": "application/json"})
    started = time.perf_counter()
    with urllib.request.urlopen(request, timeout=5) as response:
        body = json.loads(response.read().decode("utf-8"))
        elapsed_ms = (time.perf_counter() - started) * 1000
        if response.status != 200 or body.get("status") != "ok":
            raise RuntimeError(f"Unexpected health response: {response.status} {body}")
        return elapsed_ms


def percentile(values, percentile_value):
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(round((percentile_value / 100) * (len(ordered) - 1)))))
    return ordered[index]


def main():
    try:
        request_health()
        samples = [request_health() for _ in range(SAMPLES)]
    except (OSError, urllib.error.URLError, RuntimeError, TimeoutError) as error:
        print(f"Performance smoke check failed: {error}", file=sys.stderr)
        return 1

    p95 = percentile(samples, 95)
    result = {
        "endpoint": "GET /health",
        "samples": SAMPLES,
        "min_ms": round(min(samples), 2),
        "median_ms": round(statistics.median(samples), 2),
        "p95_ms": round(p95, 2),
        "max_ms": round(max(samples), 2),
        "threshold_p95_ms": MAX_P95_MS,
        "status": "passed" if p95 <= MAX_P95_MS else "failed",
        "note": "Local smoke threshold, not a load or capacity benchmark."
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
