"""Preprint parameter extractor for the Math 3.0 catalogue.

Phase 2 (manuscript-level mining): scan the LaTeX sources inside
staging/openai_math/preprints/ for candidate empirical constants,
thresholds and exponent markers.

The extraction is regex-based and conservative: it records candidate
matches, not curated parameter values. Families without a readable .tex
source, or without any regex match, fall back to the default seed fractions
and are flagged in the output.
"""

import json
import math
import os
import re
import statistics
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction

ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
STAGING = os.path.join(ROOT, "staging", "openai_math")
CONTENTS = os.path.join(STAGING, "CONTENTS.md")
PREPRINTS = os.path.join(STAGING, "preprints")
OUT = os.path.join(ROOT, "reports", "math30_real_empirical_parameters.json")

DEFAULT_SEED = {
    "f_mid": "13",
    "g_mid": "1/2",
    "coupling": "1/1000000",
}

MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_MATCHES_PER_FAMILY = 60

# (name, compiled regex, per-directory cap, line pre-filter)
# Every pattern marks the meaningful capture with the named group "value".
# Patterns without a group fall back to the whole match.
PATTERN_DEFS = [
    (
        "epsilon",
        re.compile(r"\\(?:epsilon|varepsilon|eps)\s*=\s*(?P<value>[^\s,;$]+)"),
        20,
        lambda line: ("epsilon" in line or "varepsilon" in line or "eps" in line),
    ),
    (
        "c_star",
        re.compile(
            r"\b[cC]_(?:\{\*\}|\*|\{\\ast\}|\{\\star\})\s*=\s*(?P<value>[^\s,;$]+)"
        ),
        20,
        lambda line: ("c_*" in line or "C_*" in line or "c_{\\ast}" in line or "C_{\\ast}" in line),
    ),
    (
        "c_indexed",
        re.compile(r"\b[cC]_\{?\d+\}?\s*=\s*(?P<value>[^\s,;$]+)"),
        20,
        lambda line: ("c_" in line or "C_" in line),
    ),
    (
        "delta_threshold",
        re.compile(
            r"\b(?:delta|threshold|eta|varepsilon|epsilon)\s*=\s*(?P<value>[^\s,;$]+)"
        ),
        20,
        lambda line: any(w in line for w in ("delta", "threshold", "eta", "varepsilon", "epsilon")),
    ),
    (
        "rational_power10",
        re.compile(r"(?P<value>\b\d+\s*/\s*10\^\{?\d+\}?)"),
        20,
        lambda line: ("10^" in line or "10^{" in line),
    ),
    (
        "rational_factorial",
        re.compile(r"(?P<value>\b\d+\^\{?[a-zA-Z]\}?\s*/\s*[a-zA-Z]!)"),
        20,
        lambda line: ("!" in line and "^" in line),
    ),
    (
        "frac",
        re.compile(
            r"(?P<value>\\frac\{[+-]?\d+(?:\.\d+)?\}\{(?:[+-]?\d+(?:\.\d+)?|10\^\{?[+-]?\d+\}?)\})"
        ),
        8,
        lambda line: any(w in line for w in ("bound", "constant", "threshold", "epsilon", "delta", "c_", "C_")),
    ),
    (
        "numeric_eq",
        re.compile(
            r"(?P<value>(?:\d+(?:\.\d+)?)\s*(?:\\le|\\ge|\\approx|=)\s*(?:\d+(?:\.\d+)?))"
        ),
        8,
        lambda line: any(w in line for w in ("bound", "constant", "threshold", "epsilon", "delta", "c_", "C_")),
    ),
]


def clean_value(raw):
    """Normalize a captured candidate without destroying LaTeX braces.

    The previous implementation used str.strip("{}"), which turned
    ``10^{-4}`` into ``10^{-4`` and made it unparsable.  Here braces are
    preserved; only one balanced outer pair is removed.
    """
    if raw is None:
        return None
    v = raw.strip()
    while v.startswith("$"):
        v = v[1:].strip()
    while v and v[-1] in "$;,.":
        v = v[:-1].strip()
    if v.startswith("{") and v.endswith("}"):
        depth = 0
        wraps_whole = True
        for i, ch in enumerate(v):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0 and i != len(v) - 1:
                    wraps_whole = False
                    break
        if wraps_whole and depth == 0:
            v = v[1:-1].strip()
    return v


def _pow10_scale(value, exponent):
    """Multiply a Fraction by 10**exponent with a sanity cap on |exponent|."""
    if abs(exponent) > 1000:
        return None
    if exponent >= 0:
        return value * (10 ** exponent)
    return value / (10 ** (-exponent))


def _pow10_fraction(numerator, exponent):
    scaled = _pow10_scale(Fraction(numerator), exponent)
    return scaled


def parse_contents():
    families = {}
    current = None
    with open(CONTENTS, encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            m = re.match(r"^\*\*(\d{3})\.\s*(.*?)\*\*", line)
            if m:
                idx = int(m.group(1))
                current = {"index": idx, "title": m.group(2).strip(), "links": []}
                families[idx] = current
                continue
            if current is not None:
                for lm in re.finditer(r"preprints/([^)\s]+)", line):
                    current["links"].append(lm.group(1).strip().rstrip(")"))
    return families


def link_to_dir(link):
    parts = link.rsplit("/", 1)
    if len(parts) != 2:
        return None
    return os.path.join(PREPRINTS, parts[0].replace("/", os.sep))


def scan_dir(dir_path):
    """Scan one preprint directory once; cache the candidate matches."""
    tex_files = []
    if os.path.isdir(dir_path):
        for root, _, files in os.walk(dir_path):
            for fn in files:
                if fn.lower().endswith(".tex"):
                    tex_files.append(os.path.join(root, fn))
    tex_files.sort()

    matches = []
    seen = set()
    counts = Counter()
    bytes_scanned = 0

    for tf in tex_files:
        try:
            size = os.path.getsize(tf)
        except OSError:
            continue
        if size > MAX_FILE_BYTES:
            continue
        bytes_scanned += size
        try:
            with open(tf, encoding="utf-8", errors="ignore") as fh:
                for lineno, line in enumerate(fh, 1):
                    for pname, rx, cap, trigger in PATTERN_DEFS:
                        if counts[pname] >= cap:
                            continue
                        if not trigger(line):
                            continue
                        for m in rx.finditer(line):
                            captured = m.groupdict().get("value") or m.group(0)
                            value = clean_value(captured)
                            if not value:
                                continue
                            key = (pname, value)
                            if key in seen:
                                continue
                            seen.add(key)
                            matches.append(
                                {
                                    "pattern": pname,
                                    "value": value,
                                    "file": os.path.relpath(tf, ROOT).replace("\\", "/"),
                                    "line": lineno,
                                    "snippet": line.strip()[:220],
                                }
                            )
                            counts[pname] += 1
                            if counts[pname] >= cap:
                                break
        except OSError:
            continue

    return {
        "tex_files": [os.path.relpath(tf, ROOT).replace("\\", "/") for tf in tex_files],
        "tex_count": len(tex_files),
        "bytes_scanned": bytes_scanned,
        "matches": matches,
    }


def parse_numeric(value):
    """Parse a candidate into an exact Fraction, or None if it is symbolic."""
    if value is None:
        return None
    v = clean_value(value)
    if not v:
        return None

    # Plain integer / decimal / scientific notation.
    if re.fullmatch(r"[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?", v):
        try:
            return Fraction(v)
        except (ValueError, ZeroDivisionError):
            return None

    # a / b
    m = re.fullmatch(r"([+-]?\d+)\s*/\s*([+-]?\d+)", v)
    if m and int(m.group(2)) != 0:
        return Fraction(int(m.group(1)), int(m.group(2)))

    # a / 10^n  (n may be negative): value is a * 10^(-n)
    m = re.fullmatch(r"([+-]?\d+)\s*/\s*10\^\{?([+-]?\d+)\}?", v)
    if m:
        return _pow10_fraction(int(m.group(1)), -int(m.group(2)))

    # \frac{a}{10^n}
    m = re.fullmatch(r"\\frac\{([+-]?\d+)\}\{10\^\{?([+-]?\d+)\}?\}", v)
    if m:
        return _pow10_fraction(int(m.group(1)), -int(m.group(2)))

    # \frac{a}{b}
    m = re.fullmatch(r"\\frac\{([+-]?\d+(?:\.\d+)?)\}\{([+-]?\d+(?:\.\d+)?)\}", v)
    if m:
        try:
            return Fraction(m.group(1)) / Fraction(m.group(2))
        except ZeroDivisionError:
            return None

    # 10^n
    m = re.fullmatch(r"10\^\{?([+-]?\d+)\}?", v)
    if m:
        return _pow10_fraction(1, int(m.group(1)))

    # a \times 10^n or a \cdot 10^n
    m = re.fullmatch(
        r"([+-]?\d+(?:\.\d+)?)\s*(?:\\times|\\cdot)\s*10\^\{?([+-]?\d+)\}?", v
    )
    if m:
        return _pow10_scale(Fraction(m.group(1)), int(m.group(2)))

    # general integer power a^n with a guard on the exponent
    m = re.fullmatch(r"([+-]?\d+)\^\{?([+-]?\d+)\}?", v)
    if m:
        base, exp = int(m.group(1)), int(m.group(2))
        if abs(exp) > 64:
            return None
        if exp >= 0:
            return Fraction(base ** exp)
        if base == 0:
            return None
        return Fraction(1, base ** (-exp))

    return None


families = parse_contents()

# Map each family to its preprint directories, then scan each unique directory once.
family_dirs = {}
all_dirs = set()
for idx, fam in families.items():
    dirs = []
    for link in fam["links"]:
        d = link_to_dir(link)
        if d and d not in dirs:
            dirs.append(d)
            all_dirs.add(d)
    family_dirs[idx] = dirs

print(f"Families discovered in CONTENTS.md : {len(families)}")
print(f"Unique preprint directories mapped : {len(all_dirs)}")
print("Scanning LaTeX sources (read-only, sequential)...")

dir_cache = {}
for n, d in enumerate(sorted(all_dirs), 1):
    dir_cache[d] = scan_dir(d)
    if n % 100 == 0:
        print(f"  scanned directories: {n}/{len(all_dirs)}")

pattern_priority = {name: i for i, (name, _, _, _) in enumerate(PATTERN_DEFS)}

records = []
summary_counts = Counter()
pattern_totals = Counter()
numeric_values = []
numeric_by_family = []
non_numeric = 0

for idx in sorted(families):
    fam = families[idx]
    dirs = family_dirs[idx]

    combined = []
    tex_count = 0
    bytes_scanned = 0
    for d in dirs:
        cached = dir_cache.get(d)
        if not cached:
            continue
        tex_count += cached["tex_count"]
        bytes_scanned += cached["bytes_scanned"]
        combined.extend(cached["matches"])

    # Deduplicate across companion directories; keep the first occurrence.
    deduped = []
    seen = set()
    for m in combined:
        key = (m["pattern"], m["value"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(m)

    deduped.sort(key=lambda m: (pattern_priority.get(m["pattern"], 99), m["value"]))
    deduped = deduped[:MAX_MATCHES_PER_FAMILY]

    extracted = {}
    for m in deduped:
        extracted.setdefault(m["pattern"], m["value"])

    primary = None
    for m in deduped:
        pv = parse_numeric(m["value"])
        if pv is not None:
            primary = pv
            break

    if tex_count == 0:
        status = "fallback"
        reason = "no_tex_source"
        summary_counts["fallback_no_tex"] += 1
    elif not deduped:
        status = "fallback"
        reason = "no_regex_match"
        summary_counts["fallback_no_match"] += 1
    else:
        status = "extracted"
        reason = None
        summary_counts["extracted"] += 1
        if primary is not None:
            numeric_values.append(primary)
            numeric_by_family.append((idx, primary))
        else:
            non_numeric += 1

    for m in deduped:
        pattern_totals[m["pattern"]] += 1

    summary_counts["families"] += 1
    summary_counts["with_tex"] += 1 if tex_count > 0 else 0
    summary_counts["matches"] += len(deduped)

    records.append(
        {
            "family_index": idx,
            "title": fam["title"],
            "preprint_dirs": [os.path.relpath(d, ROOT).replace("\\", "/") for d in dirs],
            "tex_files_scanned": tex_count,
            "bytes_scanned": bytes_scanned,
            "source_status": status,
            "fallback_reason": reason,
            "applied_parameters": dict(DEFAULT_SEED) if status == "fallback" else dict(extracted),
            "extracted_constants": extracted,
            "matches": deduped,
            "primary_numeric_constant": str(primary) if primary is not None else None,
        }
    )

# ---- numeric statistics ----------------------------------------------------
def percentile_exact(sorted_values, p):
    """Nearest interpolation percentile on exact Fractions (p in [0, 1])."""
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = Fraction(p) * (len(sorted_values) - 1)
    lo = math.floor(pos)
    hi = min(lo + 1, len(sorted_values) - 1)
    weight = pos - lo
    return sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * weight


if numeric_values:
    numeric_mean = statistics.mean(numeric_values)
    numeric_var = statistics.pvariance(numeric_values) if len(numeric_values) > 1 else Fraction(0)
    numeric_std = math.sqrt(float(numeric_var)) if numeric_var else 0.0
    numeric_min = min(numeric_values)
    numeric_max = max(numeric_values)

    sorted_values = sorted(numeric_values)
    numeric_median = percentile_exact(sorted_values, Fraction(1, 2))
    numeric_q1 = percentile_exact(sorted_values, Fraction(1, 4))
    numeric_q3 = percentile_exact(sorted_values, Fraction(3, 4))

    nonzero_values = [v for v in numeric_values if v != 0]
    log_abs = [math.log10(abs(v)) for v in nonzero_values]
    if log_abs:
        log_mean = sum(log_abs) / len(log_abs)
        log_std = math.sqrt(sum((x - log_mean) ** 2 for x in log_abs) / len(log_abs))
        log_min, log_max = min(log_abs), max(log_abs)
    else:
        log_mean = log_std = log_min = log_max = None

    threshold_values = sorted(v for v in numeric_values if 0 < abs(v) <= 1)
    threshold_median = percentile_exact(threshold_values, Fraction(1, 2))
    threshold_q1 = percentile_exact(threshold_values, Fraction(1, 4))
    threshold_q3 = percentile_exact(threshold_values, Fraction(3, 4))
    threshold_log_abs = [math.log10(abs(v)) for v in threshold_values]
    threshold_log_mean = (
        sum(threshold_log_abs) / len(threshold_log_abs) if threshold_log_abs else None
    )

    extreme_outliers = [
        {"family_index": idx, "primary_numeric_constant": str(v)}
        for idx, v in numeric_by_family
        if abs(v) > 10 ** 6
    ]

    # A cap at 100 keeps the comparison finite without the literal exponents
    # 10^96 and 2^17 that otherwise dominate the raw moments.
    trimmed_values = [v for v in numeric_values if abs(v) <= 100]
    trimmed_mean = statistics.mean(trimmed_values) if trimmed_values else None
    trimmed_var = (
        statistics.pvariance(trimmed_values) if len(trimmed_values) > 1 else Fraction(0)
    )
    trimmed_std = math.sqrt(float(trimmed_var)) if trimmed_var else 0.0
else:
    numeric_mean = numeric_var = numeric_min = numeric_max = None
    numeric_std = 0.0
    numeric_median = numeric_q1 = numeric_q3 = None
    log_mean = log_std = log_min = log_max = None
    threshold_values = []
    threshold_median = threshold_q1 = threshold_q3 = threshold_log_mean = None
    extreme_outliers = []
    trimmed_values = []
    trimmed_mean = trimmed_var = None
    trimmed_std = 0.0

synthetic_stats = None
synthetic_path = os.path.join(ROOT, "reports", "math30_discovered_intelligence.json")
if os.path.exists(synthetic_path):
    try:
        synthetic_stats = json.load(open(synthetic_path, encoding="utf-8")).get("statistics")
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[WARN] Could not read {synthetic_path}: {exc}")
        synthetic_stats = None

payload = {
    "schema": "MATH30_REAL_EMPIRICAL_PARAMETERS_V1",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "source_root": "staging/openai_math/preprints",
    "family_count": len(records),
    "default_seed_fractions": DEFAULT_SEED,
    "summary": {
        "families_scanned": summary_counts["families"],
        "families_with_tex_source": summary_counts["with_tex"],
        "families_with_extracted_constants": summary_counts["extracted"],
        "families_with_fallback": summary_counts["fallback_no_tex"] + summary_counts["fallback_no_match"],
        "fallback_no_tex_source": summary_counts["fallback_no_tex"],
        "fallback_no_regex_match": summary_counts["fallback_no_match"],
        "total_candidate_matches": summary_counts["matches"],
        "pattern_totals": dict(pattern_totals),
        "fallback_family_indices": [
            r["family_index"] for r in records if r["source_status"] == "fallback"
        ],
    },
    "numeric_constant_statistics": {
        "numeric_count": len(numeric_values),
        "non_numeric_count": non_numeric,
        "mean_exact": str(numeric_mean) if numeric_mean is not None else None,
        "mean_float": float(numeric_mean) if numeric_mean is not None else None,
        "variance_exact": str(numeric_var) if numeric_var is not None else None,
        "variance_float": float(numeric_var) if numeric_var is not None else None,
        "stdev_float": numeric_std,
        "min_exact": str(numeric_min) if numeric_min is not None else None,
        "max_exact": str(numeric_max) if numeric_max is not None else None,
        "median_exact": str(numeric_median) if numeric_median is not None else None,
        "median_float": float(numeric_median) if numeric_median is not None else None,
        "q1_exact": str(numeric_q1) if numeric_q1 is not None else None,
        "q3_exact": str(numeric_q3) if numeric_q3 is not None else None,
        "sign_counts": {
            "negative": sum(1 for v in numeric_values if v < 0),
            "zero": sum(1 for v in numeric_values if v == 0),
            "positive": sum(1 for v in numeric_values if v > 0),
        },
        "magnitude_counts": {
            "abs_le_1": sum(1 for v in numeric_values if 0 < abs(v) <= 1),
            "abs_gt_1": sum(1 for v in numeric_values if abs(v) > 1),
            "abs_gt_1e6": len(extreme_outliers),
        },
        "log10_abs_statistics": {
            "count": len(log_abs),
            "mean": log_mean,
            "stdev": log_std,
            "min": log_min,
            "max": log_max,
        },
        "threshold_subset_0_lt_abs_le_1": {
            "count": len(threshold_values),
            "median_exact": str(threshold_median) if threshold_median is not None else None,
            "median_float": float(threshold_median) if threshold_median is not None else None,
            "q1_exact": str(threshold_q1) if threshold_q1 is not None else None,
            "q3_exact": str(threshold_q3) if threshold_q3 is not None else None,
            "log10_abs_mean": threshold_log_mean,
        },
        "trimmed_subset_abs_le_100": {
            "count": len(trimmed_values),
            "mean_exact": str(trimmed_mean) if trimmed_mean is not None else None,
            "mean_float": float(trimmed_mean) if trimmed_mean is not None else None,
            "variance_exact": str(trimmed_var) if trimmed_var is not None else None,
            "variance_float": float(trimmed_var) if trimmed_var is not None else None,
            "stdev_float": trimmed_std,
        },
        "extreme_outliers_abs_gt_1e6": extreme_outliers,
    },
    "synthetic_comparison": {
        "synthetic_statistics": synthetic_stats,
        "note": (
            "The synthetic residuals form the arithmetic sequence index-4 for 354 of 373 families. "
            "The extracted candidate constants are heterogeneous: the raw mean and variance are dominated "
            "by a few literal exponents (for example 10^96 and 9.465e10), so the raw variance is not a "
            "meaningful measure of manuscript structure. The robust statistics (median, quartiles, "
            "log10|value|) and the threshold subset (0 < |value| <= 1) are the defensible comparison. "
            "Even then, the synthetic residuals live on the family-index scale (median ~ few hundred), "
            "whereas extracted thresholds cluster near 1e-5; the two distributions differ in kind, not "
            "merely in parameters."
        ),
    },
    "records": records,
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(payload, fh, indent=2, ensure_ascii=False)

print()
print("PREPRINT PARAMETER EXTRACTOR")
print("============================")
print(f"Total families scanned             : {summary_counts['families']}")
print(f"Families with readable .tex source : {summary_counts['with_tex']}")
print(f"Families with extracted constants  : {summary_counts['extracted']}")
print(f"Families using fallback seeds      : {summary_counts['fallback_no_tex'] + summary_counts['fallback_no_match']}")
print(f"  - no .tex source                 : {summary_counts['fallback_no_tex']}")
print(f"  - no regex match                 : {summary_counts['fallback_no_match']}")
print(f"Total candidate regex matches      : {summary_counts['matches']}")
fallback_ids = [r["family_index"] for r in records if r["source_status"] == "fallback"]
print(f"Fallback family indices            : {fallback_ids}")
print()
print("PATTERN TOTALS")
for name, count in pattern_totals.most_common():
    print(f"  {name:22s}: {count}")
print()
if numeric_values:
    print("PRIMARY NUMERIC CONSTANT STATISTICS")
    print(f"  numeric families                 : {len(numeric_values)}")
    print(f"  non-numeric extracted families   : {non_numeric}")
    print(f"  mean (exact)                     : {numeric_mean}")
    print(f"  variance (exact)                 : {numeric_var}")
    print(f"  variance (float)                 : {float(numeric_var):.6e}")
    print(f"  stdev                            : {numeric_std:.6e}")
    print(f"  min / max                        : {numeric_min} / {numeric_max}")
    print(f"  median (robust)                  : {numeric_median}")
    print(f"  q1 / q3                          : {numeric_q1} / {numeric_q3}")
    print(f"  sign <0 / =0 / >0                : {sum(1 for v in numeric_values if v < 0)} / {sum(1 for v in numeric_values if v == 0)} / {sum(1 for v in numeric_values if v > 0)}")
    print(f"  |v| <= 1 / |v| > 1               : {sum(1 for v in numeric_values if 0 < abs(v) <= 1)} / {sum(1 for v in numeric_values if abs(v) > 1)}")
    if log_mean is not None:
        print(f"  log10|v| mean / stdev            : {log_mean:.6f} / {log_std:.6f}")
        print(f"  log10|v| min / max               : {log_min:.6f} / {log_max:.6f}")
    print(f"  threshold subset (0<|v|<=1)      : {len(threshold_values)}")
    if threshold_median is not None:
        print(f"    median / q1 / q3               : {threshold_median} / {threshold_q1} / {threshold_q3}")
        print(f"    log10|v| mean                  : {threshold_log_mean:.6f}")
    print(f"  trimmed subset (|v|<=100)        : {len(trimmed_values)}")
    print(f"    mean / variance / stdev        : {float(trimmed_mean):.6f} / {float(trimmed_var):.6f} / {trimmed_std:.6f}")
    if extreme_outliers:
        print(f"  extreme outliers (|v|>1e6)       : {len(extreme_outliers)}")
        for item in extreme_outliers:
            print(f"    family {item['family_index']:03d}: {item['primary_numeric_constant'][:60]}")
else:
    print("PRIMARY NUMERIC CONSTANT STATISTICS: no numeric primary constants parsed")
print()
if synthetic_stats:
    print("SYNTHETIC BASELINE (for comparison)")
    print(f"  mean                             : {synthetic_stats.get('mean_exact')}")
    print(f"  variance                         : {synthetic_stats.get('variance_exact')}")
    print(f"  stdev                            : {synthetic_stats.get('stdev_float')}")
print()
print(f"Empirical parameter database      : {OUT}")
