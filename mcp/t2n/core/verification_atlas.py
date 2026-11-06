#!/usr/bin/env python3
"""OpenAI Math verification provenance atlas.

Builds a version-aware, disk-verified cross-index of the local OpenAI Math
catalogue: 751 preprint directories, 722 unique manuscript stems, 373 result
families, 176 formalized manuscripts, 208 main-result declarations and 419
comparator configurations.

The tool is read-only over the catalogue. It writes three derived artifacts:

  reports/openai_math_verification_atlas.json
  exports/openai_math_verification_atlas.html
  exports/openai_math_verification_atlas.svg

No binary floats are used. Counts are integers; percentages are exact integer
basis-point strings. SHA-256 digests use LF-normalised bytes so that Windows
checkouts and POSIX checkouts agree.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from fractions import Fraction
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("FATAL: PyYAML is required for this atlas builder.", file=sys.stderr)
    raise

ROOT = Path(__file__).resolve().parents[3]
STAGING = ROOT / "staging" / "openai_math"
PREPRINTS = STAGING / "preprints"
LEAN = STAGING / "lean"
CONTENTS = STAGING / "CONTENTS.md"
HISTORY = STAGING / "history.md"
EMPIRICAL = ROOT / "reports" / "math30_real_empirical_parameters.json"
FORMALIZATION = LEAN / "formalization.yaml"
MANIFEST = ROOT / "manifest.json"

DATE_RE = re.compile(
    r"-(January|February|March|April|May|June|July|August|September|October|"
    r"November|December)-(\d{1,2})-(\d{4})$",
    re.IGNORECASE,
)
MONTHS = {
    name.lower(): index
    for index, name in enumerate(
        [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ],
        start=1,
    )
}
TAGS = re.compile(r"<[^>]+>")
MARKDOWN_LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")
PLACEHOLDER_RE = re.compile(r"\b(sorry|admit|axiom|Abort)\b")


def sha256_file(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def lf_size(path: Path) -> int:
    return len(path.read_bytes().replace(b"\r\n", b"\n"))


def strip_date(name: str) -> str:
    return DATE_RE.sub("", name)


def parse_date(name: str):
    match = DATE_RE.search(name)
    if not match:
        return None
    return (int(match.group(3)), MONTHS[match.group(1).lower()], int(match.group(2)))


def date_key(name: str):
    parsed = parse_date(name)
    return parsed if parsed is not None else (0, 0, 0)


def iso_date(parsed) -> str | None:
    if parsed is None:
        return None
    return f"{parsed[0]:04d}-{parsed[1]:02d}-{parsed[2]:02d}"


def parse_long_date(value: str) -> str | None:
    match = re.match(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", value or "")
    if match is None:
        return None
    month = MONTHS.get(match.group(1).lower())
    if month is None:
        return None
    return f"{int(match.group(3)):04d}-{month:02d}-{int(match.group(2)):02d}"


def pct(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "0.00%"
    basis = (numerator * 10000 + denominator // 2) // denominator
    return f"{basis // 100}.{basis % 100:02d}%"


def width_pct(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "0.00%"
    basis = (numerator * 10000 + denominator // 2) // denominator
    return f"{basis // 100}.{basis % 100:02d}%"


def clean_title(value: str) -> str:
    value = MARKDOWN_LINK.sub(r"\1", value or "")
    return html.unescape(TAGS.sub("", value)).strip()


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def assert_no_floats(value, path: str = "root") -> None:
    if isinstance(value, float):
        raise TypeError(f"binary float leaked at {path}: {value!r}")
    if isinstance(value, dict):
        for key, child in value.items():
            assert_no_floats(child, f"{path}/{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_no_floats(child, f"{path}[{index}]")


def strip_lean_comments(source: str) -> str:
    """Remove Lean line and block comments for token scanning.

    This is deliberately conservative: nested block comments are not modelled.
    It is sufficient for the repository's generated sources, and the result is
    reported as a token scan, not as a kernel check.
    """
    source = re.sub(r"/-.*?-/", " ", source, flags=re.DOTALL)
    source = re.sub(r"--[^\n]*", " ", source)
    return source


def declaration_present(declaration: str, cleaned: str) -> bool:
    if declaration in cleaned:
        return True
    short = declaration.rsplit(".", 1)[-1]
    return re.search(r"\b" + re.escape(short) + r"\b", cleaned) is not None


def build_ledger() -> dict:
    empirical = load_json(EMPIRICAL)
    formalization = yaml.safe_load(FORMALIZATION.read_text(encoding="utf-8"))
    families = empirical["records"]

    all_dirs = sorted([p.name for p in PREPRINTS.iterdir() if p.is_dir()])
    dirs_by_stem = defaultdict(list)
    for name in all_dirs:
        dirs_by_stem[strip_date(name)].append(name)

    family_dirs = {}
    family_stems = {}
    stem_family = {}
    collisions = []
    for record in families:
        index = record["family_index"]
        names = [Path(p).name for p in record.get("preprint_dirs", [])]
        stems = {strip_date(name) for name in names}
        family_dirs[index] = names
        family_stems[index] = stems
        for stem in stems:
            if stem in stem_family and stem_family[stem] != index:
                collisions.append((stem, stem_family[stem], index))
            stem_family[stem] = index

    unmapped_dirs = [name for name in all_dirs if strip_date(name) not in stem_family]
    mapped_dirs = len(all_dirs) - len(unmapped_dirs)
    versioned_stems = {stem: names for stem, names in dirs_by_stem.items() if len(names) > 1}
    extra_dirs = sum(len(names) - 1 for names in versioned_stems.values())

    formalized_sources = []
    formalized_families = set()
    version_lag = []
    for source in formalization.get("sources", []):
        source_dir = Path(source["id"]).parent.name
        stem = strip_date(source_dir)
        family_index = stem_family.get(stem)
        parsed = parse_date(source_dir)
        siblings = dirs_by_stem.get(stem, [source_dir])
        latest = max(siblings, key=date_key)
        lag_days = None
        if parsed is not None and latest != source_dir:
            latest_parsed = parse_date(latest)
            if latest_parsed is not None:
                lag_days = (date(*latest_parsed) - date(*parsed)).days
        entry = {
            "title": clean_title(source.get("title", "")),
            "source_dir": source_dir,
            "stem": stem,
            "family_index": family_index,
            "source_date": "-".join(f"{part:02d}" if i else str(part) for i, part in enumerate(parsed)) if parsed else None,
            "latest_dir": latest,
            "latest_date": "-".join(f"{part:02d}" if i else str(part) for i, part in enumerate(parse_date(latest))) if parse_date(latest) else None,
            "lag_days": lag_days,
        }
        formalized_sources.append(entry)
        if family_index is not None:
            formalized_families.add(family_index)
        if lag_days is not None and lag_days > 0:
            version_lag.append(entry)

    # Main-result audit.
    main_results = []
    referenced_comparators = set()
    placeholder_total = 0
    declaration_failures = []
    file_failures = []
    comparator_failures = []
    theorem_failures = []
    solution_mismatches = []
    for item in formalization.get("status", {}).get("main_results", []):
        rel_file = item["file"]
        rel_comparator = item["comparator_config"]
        declaration = item["declaration"]
        file_path = LEAN / rel_file
        comparator_path = LEAN / rel_comparator
        referenced_comparators.add(rel_comparator)

        file_exists = file_path.exists()
        comparator_exists = comparator_path.exists()
        declaration_found = False
        placeholder_hits = 0
        file_sha = None
        file_bytes = None
        file_lines = None
        category = rel_file.split("/")[1] if rel_file.count("/") >= 2 else "OAI"

        if file_exists:
            text = file_path.read_text(encoding="utf-8", errors="replace")
            cleaned = strip_lean_comments(text)
            declaration_found = declaration_present(declaration, cleaned)
            placeholder_hits = len(PLACEHOLDER_RE.findall(cleaned))
            file_sha = sha256_file(file_path)
            file_bytes = lf_size(file_path)
            file_lines = text.count("\n") + 1
        else:
            file_failures.append(declaration)
        if not declaration_found:
            declaration_failures.append(declaration)
        if not comparator_exists:
            comparator_failures.append(declaration)

        theorem_match = False
        solution_module = None
        challenge_module = None
        permitted_axioms = []
        if comparator_exists:
            config = json.loads(comparator_path.read_text(encoding="utf-8"))
            theorem_match = declaration in config.get("theorem_names", [])
            solution_module = config.get("solution_module")
            challenge_module = config.get("challenge_module")
            permitted_axioms = config.get("permitted_axioms", [])
            expected = rel_file[:-5].replace("/", ".") if rel_file.endswith(".lean") else rel_file.replace("/", ".")
            if solution_module != expected:
                solution_mismatches.append(
                    {"declaration": declaration, "solution_module": solution_module, "file_module": expected}
                )
        if not theorem_match:
            theorem_failures.append(declaration)
        placeholder_total += placeholder_hits

        main_results.append(
            {
                "declaration": declaration,
                "file": rel_file,
                "category": category,
                "file_exists": file_exists,
                "file_sha256": file_sha,
                "file_bytes": file_bytes,
                "file_lines": file_lines,
                "declaration_found": declaration_found,
                "placeholder_hits": placeholder_hits,
                "comparator_config": rel_comparator,
                "comparator_exists": comparator_exists,
                "theorem_match": theorem_match,
                "solution_module": solution_module,
                "challenge_module": challenge_module,
                "permitted_axioms": permitted_axioms,
            }
        )

    all_comparators = {
        str(path.relative_to(LEAN)).replace("\\", "/")
        for path in (LEAN / "ComparatorChallenges").rglob("*.json")
    }
    top_level_comparators = {
        str(path.relative_to(LEAN)).replace("\\", "/")
        for path in (LEAN / "ComparatorChallenges").glob("*.json")
    }
    nested_comparators = all_comparators - top_level_comparators
    unreferenced_comparators = sorted(all_comparators - referenced_comparators)

    comparator_solution_ok = 0
    comparator_challenge_ok = 0
    comparator_theorem_text_ok = 0
    comparator_theorem_text_missing = []
    comparator_records = []
    for rel in sorted(all_comparators):
        config = json.loads((LEAN / rel).read_text(encoding="utf-8"))
        solution_module = config.get("solution_module", "")
        challenge_module = config.get("challenge_module", "")
        solution_path = LEAN / (solution_module.replace(".", "/") + ".lean")
        challenge_path = LEAN / (challenge_module.replace(".", "/") + ".lean")
        if solution_path.exists():
            comparator_solution_ok += 1
        if challenge_path.exists():
            comparator_challenge_ok += 1
        theorems = config.get("theorem_names", [])
        if solution_path.exists():
            cleaned = strip_lean_comments(solution_path.read_text(encoding="utf-8", errors="replace"))
            missing = [
                name
                for name in theorems
                if name not in cleaned
                and re.search(r"\b" + re.escape(name.rsplit(".", 1)[-1]) + r"\b", cleaned) is None
            ]
        else:
            missing = theorems
        if not missing:
            comparator_theorem_text_ok += 1
        else:
            comparator_theorem_text_missing.append({"config": rel, "missing": missing})
        comparator_records.append(
            {
                "config": rel,
                "referenced_by_main_results": rel in referenced_comparators,
                "solution_module": solution_module,
                "challenge_module": challenge_module,
                "solution_exists": solution_path.exists(),
                "challenge_exists": challenge_path.exists(),
                "theorem_count": len(theorems),
                "theorem_text_found": not missing,
                "theorem_text_missing": missing,
            }
        )

    # Local Math 3.0 seal chain: report -> certificate -> Lean certificate.
    local_chain_ok = 0
    local_records = []
    local_missing = {"reports": [], "certificates": [], "lean": []}
    for index in range(1, 374):
        report_path = ROOT / "reports" / f"openai_family_{index:03d}.json"
        cert_path = ROOT / "reports" / "certificates" / f"openai_family_{index:03d}_certificate.json"
        lean_path = ROOT / "lean" / "spec_v4" / "certificates" / f"OpenaiFamily{index:03d}Certificate.lean"
        exists = {
            "report": report_path.exists(),
            "certificate": cert_path.exists(),
            "lean": lean_path.exists(),
        }
        if not exists["report"]:
            local_missing["reports"].append(index)
        if not exists["certificate"]:
            local_missing["certificates"].append(index)
        if not exists["lean"]:
            local_missing["lean"].append(index)

        chain_ok = False
        report_sha = None
        cert_sha = None
        if all(exists.values()):
            report_sha = sha256_file(report_path)
            cert_sha = sha256_file(cert_path)
            certificate = json.loads(cert_path.read_text(encoding="utf-8"))
            lean_source = lean_path.read_text(encoding="utf-8", errors="replace")
            source_match = re.search(r'sourceSha256 := "([0-9a-f]{64})"', lean_source)
            cert_match = re.search(r'certificateSha256 := "([0-9a-f]{64})"', lean_source)
            chain_ok = (
                certificate.get("source_sha256") == report_sha
                and certificate.get("source_size_bytes") == lf_size(report_path)
                and source_match is not None
                and source_match.group(1) == report_sha
                and cert_match is not None
                and cert_match.group(1) == cert_sha
            )
            if chain_ok:
                local_chain_ok += 1
        local_records.append(
            {
                "index": index,
                "report": exists["report"],
                "certificate": exists["certificate"],
                "lean": exists["lean"],
                "chain_ok": chain_ok,
                "report_sha256": report_sha,
                "certificate_sha256": cert_sha,
            }
        )

    # Family records, enriched with formalization and local seal state.
    formalized_by_family = defaultdict(list)
    for entry in formalized_sources:
        if entry["family_index"] is not None:
            formalized_by_family[entry["family_index"]].append(entry)

    family_indices = {record["family_index"] for record in families}
    local_by_label = {record["index"]: record for record in local_records}
    local_orphan_labels = sorted(set(local_by_label) - family_indices)
    local_unsealed_families = sorted(family_indices - set(local_by_label))
    local_aligned_chain_ok = sum(
        1 for index in family_indices if local_by_label.get(index, {}).get("chain_ok")
    )

    family_records = []
    for record in families:
        index = record["family_index"]
        names = family_dirs[index]
        stems = sorted(family_stems[index])
        formal_sources = formalized_by_family.get(index, [])
        local = local_by_label.get(index)
        primary = record.get("primary_numeric_constant")
        family_records.append(
            {
                "index": index,
                "title": clean_title(record.get("title", "")),
                "manuscript_dirs": names,
                "manuscript_count": len(names),
                "unique_manuscripts": len(stems),
                "version_extra": len(names) - len(stems),
                "stems": stems,
                "formalized": bool(formal_sources),
                "formalized_source_count": len(formal_sources),
                "formalization_dirs": [entry["source_dir"] for entry in formal_sources],
                "candidate_matches": len(record.get("matches", [])),
                "primary_numeric_constant": primary,
                "source_status": record.get("source_status"),
                "tex_files_scanned": record.get("tex_files_scanned", 0),
                "bytes_scanned": record.get("bytes_scanned", 0),
                "local_label": index if local is not None else None,
                "local_report": bool(local and local["report"]),
                "local_certificate": bool(local and local["certificate"]),
                "local_lean": bool(local and local["lean"]),
                "local_chain_ok": bool(local and local["chain_ok"]),
                "extreme_constant": index in (140, 266),
            }
        )

    unformalized_families = [item for item in family_records if not item["formalized"]]
    verification_debt = sorted(
        unformalized_families,
        key=lambda item: (
            -item["candidate_matches"],
            -item["manuscript_count"],
            -item["tex_files_scanned"],
            item["index"],
        ),
    )[:25]

    category_counts = Counter(item["category"] for item in main_results)
    categories = [
        {"name": name, "main_results": count, "percent": pct(count, len(main_results))}
        for name, count in category_counts.most_common()
    ]

    all_axiom_sets = Counter(tuple(sorted(item["permitted_axioms"])) for item in main_results)
    axiom_sets = [
        {"axioms": list(key), "main_results": value}
        for key, value in all_axiom_sets.most_common()
    ]

    extraction = empirical.get("summary", {})
    numeric_stats = empirical.get("numeric_constant_statistics", {})

    contents_text = CONTENTS.read_text(encoding="utf-8", errors="replace")
    contents_manuscript_links = re.findall(r"\]\((preprints/[^)]+\.pdf)\)", contents_text)
    contents_all_pdf_links = re.findall(r"\]\(([^)]+\.pdf)\)", contents_text)
    contents_overview_links = [
        link for link in contents_all_pdf_links if not link.startswith("preprints/")
    ]
    contents_family_entries = re.findall(r"^\*\*(\d{3})\.", contents_text, re.MULTILINE)
    linked_dirs = {link.split("/")[1] for link in contents_manuscript_links}
    linked_stems = {strip_date(name) for name in linked_dirs}
    unlinked_dirs = sorted(set(all_dirs) - linked_dirs)
    unlinked_stems = sorted({strip_date(name) for name in unlinked_dirs})
    orphan_stems = sorted(set(unlinked_stems) - set(stem_family))
    unlinked_version_dirs = [
        name for name in unlinked_dirs if len(dirs_by_stem[strip_date(name)]) > 1
    ]

    readme_text = (STAGING / "README.md").read_text(encoding="utf-8", errors="replace")
    readme_claim_match = re.search(r"(\d+)\s+manuscripts", readme_text)
    readme_claim = int(readme_claim_match.group(1)) if readme_claim_match else None

    history_text = HISTORY.read_text(encoding="utf-8", errors="replace")
    history_ratio = re.search(r"(\d+)\s*/\s*(\d+)\s*=\s*~?\s*(\d+)%", history_text)
    history_formalized = int(history_ratio.group(1)) if history_ratio else None
    history_total = int(history_ratio.group(2)) if history_ratio else None
    history_percent = int(history_ratio.group(3)) if history_ratio else None
    history_new_match = re.search(r"added two new manuscripts", history_text, re.IGNORECASE)
    history_new_manuscripts = 2 if history_new_match else 0
    history_projected_total = (
        history_total + history_new_manuscripts if history_total is not None else None
    )

    unmapped_records = []
    for name in sorted(unmapped_dirs):
        readme = PREPRINTS / name / "README.md"
        title = ""
        notice_text = ""
        if readme.exists():
            notice_text = readme.read_text(encoding="utf-8", errors="replace")
            for line in notice_text.splitlines():
                if line.startswith("# "):
                    title = clean_title(line[2:])
                    break
        unmapped_records.append(
            {
                "dir": name,
                "stem": strip_date(name),
                "title": title,
                "withdrawal_notice": bool(re.search(r"withdraw", notice_text, re.IGNORECASE)),
            }
        )

    withdrawal_records = []
    for name in all_dirs:
        readme = PREPRINTS / name / "README.md"
        if not readme.exists():
            continue
        text = readme.read_text(encoding="utf-8", errors="replace")
        if not re.search(r"withdraw", text, re.IGNORECASE):
            continue
        title = ""
        for line in text.splitlines():
            if line.startswith("# "):
                title = clean_title(line[2:])
                break
        withdrawn_match = re.search(
            r"Withdrawn on\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})", text, re.IGNORECASE
        )
        withdrawn_raw = withdrawn_match.group(1) if withdrawn_match else None
        references = sorted(
            {
                ref
                for ref in re.findall(r"preprints/([^/)]+)/", text)
                if ref != name
            }
        )
        withdrawal_records.append(
            {
                "dir": name,
                "stem": strip_date(name),
                "title": title,
                "catalogue_linked": name in linked_dirs,
                "withdrawn_on_raw": withdrawn_raw,
                "withdrawn_on": parse_long_date(withdrawn_raw) if withdrawn_raw else None,
                "archived_manuscript_declared": "Pre-withdrawal PDF" in text,
                "pdf_files": sorted(path.name for path in (PREPRINTS / name).glob("*.pdf")),
                "references_withdrawn": references,
                "readme_sha256": sha256_file(readme),
                "readme_bytes": lf_size(readme),
            }
        )
    withdrawal_records.sort(key=lambda item: item["dir"])
    withdrawal_edges = [
        {"from": record["dir"], "to": reference}
        for record in withdrawal_records
        for reference in record["references_withdrawn"]
    ]
    withdrawal_roots = [
        record["dir"] for record in withdrawal_records if not record["references_withdrawn"]
    ]
    withdrawal_dates = sorted(
        {record["withdrawn_on"] for record in withdrawal_records if record["withdrawn_on"]}
    )
    withdrawn_orphan_count = sum(
        1 for record in withdrawal_records if not record["catalogue_linked"]
    )
    withdrawn_orphan_dirs = {
        record["dir"] for record in withdrawal_records if not record["catalogue_linked"]
    }
    active_orphan_dirs = [
        name
        for name in unlinked_dirs
        if name not in withdrawn_orphan_dirs and strip_date(name) in set(orphan_stems)
    ]
    one_extra_stem = active_orphan_dirs[0] if len(active_orphan_dirs) == 1 else None
    one_extra_text = one_extra_stem if one_extra_stem is not None else "ambiguous"

    catalogue_alignment = {
        "readme_claim_manuscripts": readme_claim,
        "contents_manuscript_links": len(contents_manuscript_links),
        "contents_overview_links": len(contents_overview_links),
        "contents_total_pdf_links": len(contents_all_pdf_links),
        "contents_family_entries": len(contents_family_entries),
        "linked_directories": len(linked_dirs),
        "linked_stems": len(linked_stems),
        "linked_version_extra_directories": len(linked_dirs) - len(linked_stems),
        "disk_directories": len(all_dirs),
        "disk_stems": len(dirs_by_stem),
        "unlinked_directories": len(unlinked_dirs),
        "unlinked_version_extra_directories": len(unlinked_version_dirs),
        "unlinked_orphan_stems": len(orphan_stems),
        "withdrawn_orphan_stems": withdrawn_orphan_count,
        "active_orphan_stems": len(active_orphan_dirs),
        "one_extra_stem": one_extra_stem,
        "linked_stems_plus_withdrawn": len(linked_stems) + withdrawn_orphan_count,
        "history_formalized_topline": history_formalized,
        "history_topline_total": history_total,
        "history_topline_percent": history_percent,
        "history_new_manuscripts": history_new_manuscripts,
        "history_projected_total": history_projected_total,
        "contents_sha256": sha256_file(CONTENTS),
        "history_sha256": sha256_file(HISTORY),
        "reconciliation_status": "inferred_from_counts",
        "reconciliation_note": (
            "Neither README.md nor history.md publishes a 721-row list. The 718 linked "
            "stems + 3 withdrawn notices identity is the most economical local "
            "reconciliation, not an official statement about which rows were counted."
        ),
        "reconciliation": (
            f"The most economical reconciliation is: README claims {readme_claim} manuscripts. history.md records "
            f"{history_formalized}/{history_total} = {history_percent}% top-line formalization "
            f"and two new manuscripts, giving {history_total} + {history_new_manuscripts} = "
            f"{history_projected_total}. CONTENTS.md has {len(contents_manuscript_links)} "
            f"manuscript PDF links ({len(linked_stems)} stems after "
            f"{len(linked_dirs) - len(linked_stems)} linked version duplicates) plus "
            f"{len(contents_overview_links)} overview link, so 721 is also the total PDF-link "
            f"count. On disk there are {len(all_dirs)} directories and {len(dirs_by_stem)} stems: "
            f"{len(linked_stems)} linked + {withdrawn_orphan_count} withdrawn + "
            f"{len(active_orphan_dirs)} active orphan. The single active orphan is "
            f"{one_extra_text}. The count identity is {len(linked_stems)} + "
            f"{withdrawn_orphan_count} = {len(linked_stems) + withdrawn_orphan_count}, "
            f"and the +1 is {one_extra_text}, not a missing catalogue paper."
        ),
    }

    manifest_rows = len(load_json(MANIFEST))
    formalized_stem_set = {entry["stem"] for entry in formalized_sources}
    versioned_stem_set = set(versioned_stems)
    single_version_stems = len(dirs_by_stem) - len(versioned_stem_set)
    versioned_formalized = len(formalized_stem_set & versioned_stem_set)
    single_version_formalized = len(formalized_stem_set - versioned_stem_set)
    versioning = {
        "versioned_stems": len(versioned_stem_set),
        "versioned_formalized": versioned_formalized,
        "versioned_formalized_percent": pct(versioned_formalized, len(versioned_stem_set)),
        "single_version_stems": single_version_stems,
        "single_version_formalized": single_version_formalized,
        "single_version_formalized_percent": pct(single_version_formalized, single_version_stems),
    }

    formalized_stem_map = defaultdict(list)
    for entry in formalized_sources:
        formalized_stem_map[entry["stem"]].append(entry)
    version_drift = []
    for stem, names in sorted(
        versioned_stems.items(), key=lambda item: min(date_key(name) for name in item[1])
    ):
        ordered = sorted(names, key=date_key)
        newest = ordered[-1]
        oldest = ordered[0]
        newest_parsed = parse_date(newest)
        oldest_parsed = parse_date(oldest)
        span_days = None
        if newest_parsed is not None and oldest_parsed is not None:
            span_days = (date(*newest_parsed) - date(*oldest_parsed)).days
        sources = sorted(formalized_stem_map.get(stem, []), key=lambda entry: entry["source_dir"])
        source_dates = [
            parse_date(entry["source_dir"]) for entry in sources if parse_date(entry["source_dir"])
        ]
        lag_days = None
        if source_dates and newest_parsed is not None:
            lag_days = (date(*newest_parsed) - date(*max(source_dates))).days
        version_drift.append(
            {
                "stem": stem,
                "family_index": stem_family.get(stem),
                "versions": [
                    {"dir": name, "date": iso_date(parse_date(name))} for name in ordered
                ],
                "version_count": len(ordered),
                "oldest": oldest,
                "latest": newest,
                "span_days": span_days,
                "formalized": bool(sources),
                "formalized_source_dirs": [entry["source_dir"] for entry in sources],
                "formalized_against_latest": any(
                    entry["source_dir"] == newest for entry in sources
                ),
                "formalization_lag_days": lag_days,
            }
        )
    versioning["formalized_against_older"] = sum(
        1 for row in version_drift if row["formalized"] and not row["formalized_against_latest"]
    )
    versioning["max_span_days"] = max(
        (row["span_days"] for row in version_drift if row["span_days"] is not None), default=0
    )
    versioning["latest_release_date_counts"] = dict(
        sorted(
            Counter(
                row["versions"][-1]["date"]
                for row in version_drift
                if row["versions"] and row["versions"][-1]["date"] is not None
            ).items()
        )
    )
    coverage = {
        "preprint_directories": len(all_dirs),
        "unique_manuscript_stems": len(dirs_by_stem),
        "families": len(families),
        "family_stems": len(stem_family),
        "mapped_directories": mapped_dirs,
        "unmapped_directories": len(unmapped_dirs),
        "versioned_stems": len(versioned_stems),
        "extra_version_directories": extra_dirs,
        "formalized_sources": len(formalized_sources),
        "formalized_families": len(formalized_families),
        "main_result_declarations": len(main_results),
        "comparator_configs": len(all_comparators),
        "referenced_comparator_configs": len(referenced_comparators),
        "unreferenced_comparator_configs": len(unreferenced_comparators),
        "local_family_reports": 373 - len(local_missing["reports"]),
        "local_certificates": 373 - len(local_missing["certificates"]),
        "local_lean_certificates": 373 - len(local_missing["lean"]),
        "local_hash_chain_pass": local_chain_ok,
        "local_aligned_families": len(family_indices & set(local_by_label)),
        "local_orphan_labels": local_orphan_labels,
        "local_unsealed_families": local_unsealed_families,
        "manifest_rows": manifest_rows,
    }
    coverage["percentages"] = {
        "families_formalized": pct(len(formalized_families), len(families)),
        "manuscripts_formalized": pct(len(formalized_sources), len(dirs_by_stem)),
        "directories_in_family_map": pct(mapped_dirs, len(all_dirs)),
        "comparator_configs_referenced": pct(len(referenced_comparators), len(all_comparators)),
        "local_hash_chain": pct(local_chain_ok, 373),
        "local_aligned_families": pct(local_aligned_chain_ok, len(families)),
    }

    return {
        "schema": "OPENAI_MATH_VERIFICATION_ATLAS_V1",
        "generated_at": date.today().isoformat(),
        "workspace": str(ROOT),
        "sources": {
            "empirical_database": str(EMPIRICAL.relative_to(ROOT)),
            "empirical_sha256": sha256_file(EMPIRICAL),
            "formalization_catalog": str(FORMALIZATION.relative_to(ROOT)),
            "formalization_sha256": sha256_file(FORMALIZATION),
            "manifest": str(MANIFEST.relative_to(ROOT)),
            "manifest_rows": manifest_rows,
            "manifest_note": (
                "manifest.json is a workspace ledger that includes this atlas; its digest "
                "is omitted from the atlas to avoid a circular seal."
            ),
            "contents": str(CONTENTS.relative_to(ROOT)),
            "contents_sha256": sha256_file(CONTENTS),
            "history": str(HISTORY.relative_to(ROOT)),
            "history_sha256": sha256_file(HISTORY),
        },
        "coverage": coverage,
        "catalogue_alignment": catalogue_alignment,
        "withdrawal_provenance": {
            "notices": len(withdrawal_records),
            "withdrawn_dates": withdrawal_dates,
            "roots": withdrawal_roots,
            "edges": withdrawal_edges,
            "formalized_withdrawn_sources": [
                record["dir"]
                for record in withdrawal_records
                if record["stem"] in formalized_stem_set
            ],
            "family_mapped_withdrawn": [
                record["dir"]
                for record in withdrawal_records
                if record["stem"] in stem_family
            ],
            "official_history_statement": (
                "history.md (October 7, 2026) states that a sign error in the Weil-classes "
                "paper invalidated the construction used by two dependent papers and that "
                "all three manuscripts were withdrawn."
            ),
            "records": withdrawal_records,
            "note": (
                "Withdrawal status is transcribed from each manuscript README and from "
                "history.md. It is not an independent verification of the stated error. "
                "No withdrawn record has a Lean source in formalization.yaml or a family index."
            ),
        },
        "versioning": versioning,
        "version_drift": version_drift,
        "formalization": {
            "project": formalization.get("project", {}),
            "review_status": formalization.get("review", {}).get("status"),
            "automation": formalization.get("automation", {}),
            "sources": len(formalization.get("sources", [])),
            "related_libraries": len(formalization.get("related_formalizations", [])),
            "main_results": len(main_results),
            "version_lag_count": len(version_lag),
            "axiom_sets": axiom_sets,
        },
        "main_result_audit": {
            "declarations": len(main_results),
            "file_exists": len(main_results) - len(file_failures),
            "declaration_found": len(main_results) - len(declaration_failures),
            "comparator_exists": len(main_results) - len(comparator_failures),
            "theorem_names_match": len(main_results) - len(theorem_failures),
            "placeholder_tokens": placeholder_total,
            "solution_module_file_mismatch": len(solution_mismatches),
            "solution_module_note": "Not treated as a failure; solution modules may aggregate declarations.",
            "failures": {
                "missing_files": file_failures,
                "missing_declarations": declaration_failures,
                "missing_comparators": comparator_failures,
                "theorem_mismatches": theorem_failures,
            },
        },
        "comparator_audit": {
            "total_configs": len(all_comparators),
            "top_level_configs": len(top_level_comparators),
            "nested_configs": len(nested_comparators),
            "nested_config_paths": sorted(nested_comparators),
            "referenced_configs": len(referenced_comparators),
            "unreferenced_configs": len(unreferenced_comparators),
            "solution_modules_exist": comparator_solution_ok,
            "challenge_modules_exist": comparator_challenge_ok,
            "theorem_text_found": comparator_theorem_text_ok,
            "theorem_text_not_found": len(comparator_theorem_text_missing),
            "theorem_text_missing": comparator_theorem_text_missing,
            "all_referenced_exist": len(comparator_failures) == 0,
            "note": "Theorem text is searched in the declared solution module; aggregation/imports can hide a declaration from a text scan.",
            "records": comparator_records,
        },
        "local_seals": {
            "labels": 373,
            "chain_ok": local_chain_ok,
            "aligned_families": len(family_indices & set(local_by_label)),
            "aligned_chain_ok": local_aligned_chain_ok,
            "orphan_labels": local_orphan_labels,
            "unsealed_families": local_unsealed_families,
            "missing": local_missing,
            "method": "LF-normalised SHA-256 over report, certificate and Lean certificate constants.",
            "alignment_note": (
                "Local artifacts are keyed 001-373. The catalogue uses indices 1-378 with gaps "
                "45, 61, 70, 123, 163, so 5 local labels have no family and 5 families 374-378 "
                "have no local seal. Label-index alignment for the remaining 368 is assumed, "
                "not proven by a title field."
            ),
        },
        "categories": categories,
        "families": family_records,
        "unformalized_families": len(unformalized_families),
        "verification_debt": verification_debt,
        "main_results": main_results,
        "version_lag": version_lag,
        "unmapped_stems": unmapped_records,
        "unreferenced_comparators": unreferenced_comparators,
        "extraction": {
            "families_scanned": extraction.get("families_scanned"),
            "families_with_extracted_constants": extraction.get("families_with_extracted_constants"),
            "families_with_fallback": extraction.get("families_with_fallback"),
            "total_candidate_matches": extraction.get("total_candidate_matches"),
            "median_exact": numeric_stats.get("median_exact"),
            "min_exact": numeric_stats.get("min_exact"),
            "max_exact": numeric_stats.get("max_exact"),
            "log10_abs_min": str(numeric_stats.get("log10_abs_statistics", {}).get("min")),
            "log10_abs_max": str(numeric_stats.get("log10_abs_statistics", {}).get("max")),
            "extreme_outliers": numeric_stats.get("extreme_outliers_abs_gt_1e6", []),
            "candidate_match_note": "4,434 is the candidate regex-match count, not the count of parsed numeric constants.",
        },
        "method": {
            "version_stem": "Directory name with trailing '-Month-D-YYYY' removed.",
            "declaration_check": "Full dotted name or terminal identifier found after stripping Lean comments.",
            "placeholder_check": "Token scan for sorry, admit, axiom, Abort after stripping Lean comments.",
            "local_seal_check": "LF-normalised SHA-256 chain report -> certificate -> Lean string constants.",
            "scope": "Presence, linkage and token hygiene; not kernel compilation and not mathematical proof.",
        },
        "limitations": [
            "The official formalization catalogue marks review status as unchecked.",
            "Declaration presence is a text check, not a Lean kernel check.",
            "Unreferenced comparator configs are not asserted invalid; they may cover definitions or alternatives.",
            "Local Math 3.0 seals are cryptographic integrity seals, not proofs of the manuscripts.",
            "No Beal or Euler/Navier-Stokes theorem is proved by this atlas.",
        ],
    }


def render_html(ledger: dict) -> str:
    c = ledger["coverage"]
    pcts = c["percentages"]
    families_json = json.dumps(ledger["families"], ensure_ascii=False).replace("</", "<\\/")

    def card(label, value, note=""):
        return (
            '<div class="card"><div class="card-label">'
            + html.escape(label)
            + '</div><div class="card-value">'
            + html.escape(str(value))
            + '</div><div class="card-note">'
            + html.escape(note)
            + "</div></div>"
        )

    cards = "".join(
        [
            card("Families", c["families"], "result families"),
            card("Manuscript stems", c["unique_manuscript_stems"], f'{pcts["manuscripts_formalized"]} formalized'),
            card("Formalized manuscripts", c["formalized_sources"], f'{pcts["families_formalized"]} of families'),
            card("Main-result declarations", c["main_result_declarations"], "208 audited"),
            card("Comparator configs", c["comparator_configs"], f'{c["unreferenced_comparator_configs"]} unreferenced'),
            card("Local seal chain", f'{c["local_aligned_families"]}/{c["families"]}', "aligned labels; 5 orphan labels"),
        ]
    )

    funnel_rows = [
        ("Preprint directories", c["preprint_directories"], 751),
        ("Unique manuscript stems", c["unique_manuscript_stems"], 751),
        ("Families", c["families"], 751),
        ("Formalized manuscripts", c["formalized_sources"], 751),
        ("Formalized families", c["formalized_families"], 751),
        ("Main-result declarations", c["main_result_declarations"], 751),
        ("Comparator configs", c["comparator_configs"], 751),
    ]
    funnel = "".join(
        f'<div class="funnel-row"><div class="funnel-label">{html.escape(label)}</div>'
        f'<div class="funnel-track"><div class="funnel-bar" style="width:{width_pct(value, 751)}"></div></div>'
        f'<div class="funnel-value">{value}</div></div>'
        for label, value, _ in funnel_rows
    )

    cat_max = max((row["main_results"] for row in ledger["categories"]), default=1)
    category_rows = "".join(
        f'<div class="funnel-row"><div class="funnel-label">{html.escape(row["name"])}</div>'
        f'<div class="funnel-track"><div class="funnel-bar alt" style="width:{width_pct(row["main_results"], cat_max)}"></div></div>'
        f'<div class="funnel-value">{row["main_results"]}</div></div>'
        for row in ledger["categories"]
    )

    lag_rows = "".join(
        "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            row["family_index"],
            html.escape(row["title"]),
            html.escape(row["source_dir"]),
            html.escape(row["latest_dir"]),
        )
        for row in ledger["version_lag"]
    ) or '<tr><td colspan="4">None.</td></tr>'

    unmapped_rows = "".join(
        "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            html.escape(row["stem"]),
            html.escape(row["title"]),
            html.escape(row["dir"]),
            "withdrawal" if row["withdrawal_notice"] else "active",
        )
        for row in ledger["unmapped_stems"]
    ) or '<tr><td colspan="4">None.</td></tr>'

    withdrawal_rows = "".join(
        "<tr><td>{}</td><td>{}</td><td class=\"mono\">{}</td><td class=\"mono\">{}</td><td>{}</td></tr>".format(
            html.escape(str(row["withdrawn_on"] or row["withdrawn_on_raw"] or "")),
            html.escape(row["title"]),
            html.escape(row["dir"]),
            html.escape(", ".join(row["references_withdrawn"]) or "-"),
            "yes" if row["archived_manuscript_declared"] else "no",
        )
        for row in ledger["withdrawal_provenance"]["records"]
    ) or '<tr><td colspan="5">None.</td></tr>'

    drift_rows = "".join(
        "<tr><td>{}</td><td class=\"mono\">{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            row["family_index"] if row["family_index"] is not None else "-",
            html.escape(row["stem"]),
            row["version_count"],
            html.escape(row["oldest"]),
            html.escape(row["latest"]),
            row["span_days"] if row["span_days"] is not None else "-",
            "yes" if row["formalized"] else "no",
            "yes" if row["formalized_against_latest"] else ("no" if row["formalized"] else "-"),
        )
        for row in ledger["version_drift"]
    ) or '<tr><td colspan="8">None.</td></tr>'

    unref = ledger["unreferenced_comparators"]
    unref_preview = "".join(f"<li>{html.escape(name)}</li>" for name in unref[:40])
    unref_more = f"<p class=\"muted\">Showing 40 of {len(unref)}. Full list in the JSON ledger.</p>" if len(unref) > 40 else ""

    main_rows = "".join(
        "<tr><td>{}</td><td class=\"mono\">{}</td><td>{}</td><td class=\"ok\">{}</td><td class=\"ok\">{}</td><td class=\"ok\">{}</td><td class=\"ok\">{}</td></tr>".format(
            html.escape(row["declaration"]),
            html.escape(row["file"]),
            html.escape(row["category"]),
            "yes" if row["file_exists"] else "no",
            "yes" if row["declaration_found"] else "no",
            "yes" if row["comparator_exists"] else "no",
            "yes" if row["theorem_match"] else "no",
        )
        for row in ledger["main_results"]
    )

    extraction = ledger["extraction"]
    debt_rows = "".join(
        "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            item["index"],
            html.escape(item["title"]),
            item["manuscript_count"],
            item["candidate_matches"],
            item["tex_files_scanned"],
        )
        for item in ledger["verification_debt"][:20]
    ) or '<tr><td colspan="5">None.</td></tr>'
    outlier_rows = "".join(
        "<tr><td>{}</td><td class=\"mono\">{}</td></tr>".format(
            row.get("family_index"), html.escape(str(row.get("primary_numeric_constant")))
        )
        for row in extraction.get("extreme_outliers", [])
    ) or '<tr><td colspan="2">None.</td></tr>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OpenAI Math Verification Provenance Atlas</title>
<style>
:root {{
  --bg:#0b0f14; --panel:#111821; --panel2:#16212d; --line:#243243;
  --text:#dbe7f3; --muted:#8fa3b8; --accent:#4cc9f0; --ok:#5ee6a8;
  --warn:#ffb703; --bad:#ff6b6b; --grid:#1c2a3a;
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--text); font:14px/1.5 "Segoe UI",system-ui,sans-serif; }}
header {{ padding:34px 28px 18px; border-bottom:1px solid var(--line); background:linear-gradient(180deg,#0e1620,#0b0f14); }}
h1 {{ margin:0; font-size:26px; letter-spacing:.04em; }}
.sub {{ color:var(--muted); margin-top:6px; }}
.wrap {{ max-width:1280px; margin:0 auto; padding:24px 28px 80px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:12px; }}
.card {{ background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:14px; }}
.card-label {{ color:var(--muted); font-size:11px; text-transform:uppercase; letter-spacing:.12em; }}
.card-value {{ font-size:28px; font-weight:700; margin-top:4px; }}
.card-note {{ color:var(--muted); font-size:12px; margin-top:2px; }}
h2 {{ margin:34px 0 10px; font-size:18px; letter-spacing:.03em; }}
h3 {{ margin:22px 0 8px; font-size:14px; color:var(--accent); letter-spacing:.06em; text-transform:uppercase; }}
.panel {{ background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:16px; }}
.funnel-row {{ display:grid; grid-template-columns:220px 1fr 70px; gap:10px; align-items:center; margin:7px 0; }}
.funnel-label {{ color:var(--muted); font-size:12px; }}
.funnel-track {{ height:14px; background:var(--panel2); border-radius:7px; overflow:hidden; }}
.funnel-bar {{ height:100%; background:linear-gradient(90deg,#2a9d8f,#4cc9f0); border-radius:7px; }}
.funnel-bar.alt {{ background:linear-gradient(90deg,#6a4c93,#ffb703); }}
.funnel-value {{ text-align:right; font-variant-numeric:tabular-nums; }}
table {{ width:100%; border-collapse:collapse; font-size:12px; }}
th, td {{ text-align:left; padding:7px 8px; border-bottom:1px solid var(--line); vertical-align:top; }}
th {{ color:var(--muted); font-weight:600; text-transform:uppercase; letter-spacing:.08em; font-size:10px; position:sticky; top:0; background:var(--panel); }}
tr:hover td {{ background:#0f1720; }}
.mono {{ font-family:ui-monospace,Consolas,monospace; font-size:11px; word-break:break-all; }}
.ok {{ color:var(--ok); }}
.warn {{ color:var(--warn); }}
.bad {{ color:var(--bad); }}
.muted {{ color:var(--muted); }}
.controls {{ display:flex; gap:8px; flex-wrap:wrap; margin:10px 0; align-items:center; }}
input[type=search] {{ background:var(--panel2); border:1px solid var(--line); color:var(--text); padding:9px 11px; border-radius:8px; min-width:280px; }}
button {{ background:var(--panel2); color:var(--text); border:1px solid var(--line); padding:8px 11px; border-radius:8px; cursor:pointer; font-size:12px; }}
button.active {{ border-color:var(--accent); color:var(--accent); }}
.grid373 {{ display:grid; grid-template-columns:repeat(30,1fr); gap:3px; margin-top:10px; }}
.cell {{ aspect-ratio:1/1; border-radius:2px; background:var(--grid); border:1px solid #223247; }}
.cell.formalized {{ background:#1f6f5c; border-color:#2f9d80; }}
.cell.local {{ background:#2b4c6f; border-color:#3d6f9e; }}
.cell.both {{ background:#5ee6a8; border-color:#9ff5cf; }}
.legend {{ display:flex; gap:16px; flex-wrap:wrap; color:var(--muted); font-size:12px; margin-top:10px; }}
.swatch {{ display:inline-block; width:12px; height:12px; border-radius:2px; margin-right:6px; vertical-align:-1px; }}
.tabs {{ display:flex; gap:6px; flex-wrap:wrap; margin:16px 0 0; }}
.tab {{ padding:9px 13px; border:1px solid var(--line); border-radius:8px; cursor:pointer; color:var(--muted); font-size:12px; }}
.tab.active {{ color:var(--accent); border-color:var(--accent); }}
.section {{ display:none; }} .section.active {{ display:block; }}
pre {{ background:#0a1118; border:1px solid var(--line); border-radius:8px; padding:12px; overflow:auto; font-size:11px; }}
details {{ margin-top:8px; }} summary {{ cursor:pointer; color:var(--accent); }}
.pill {{ display:inline-block; padding:2px 7px; border-radius:999px; font-size:10px; border:1px solid var(--line); }}
</style>
</head>
<body>
<header>
  <h1>OpenAI Math · Verification Provenance Atlas</h1>
  <div class="sub">Version-aware cross-index of 373 result families, 722 manuscript stems, 176 formalized manuscripts and 208 main-result declarations. Built from local disk only.</div>
</header>
<div class="wrap">
  <div class="grid">{cards}</div>

  <div class="tabs">
    <div class="tab active" data-tab="overview">Overview</div>
    <div class="tab" data-tab="families">Families</div>
    <div class="tab" data-tab="main">Main results</div>
    <div class="tab" data-tab="gaps">Gaps &amp; discrepancies</div>
    <div class="tab" data-tab="method">Method</div>
  </div>

  <section id="overview" class="section active">
    <h2>Coverage funnel</h2>
    <div class="panel">{funnel}</div>
    <h2>Catalogue reconciliation: the 721 vs 722 question</h2>
    <div class="panel">
      <table>
        <tbody>
          <tr><td>README claim</td><td><b>{ledger["catalogue_alignment"]["readme_claim_manuscripts"]}</b> manuscripts</td></tr>
          <tr><td>history.md ratio</td><td><b>{ledger["catalogue_alignment"]["history_formalized_topline"]}/{ledger["catalogue_alignment"]["history_topline_total"]}</b> = {ledger["catalogue_alignment"]["history_topline_percent"]}% top-line formalization, plus <b>{ledger["catalogue_alignment"]["history_new_manuscripts"]}</b> new manuscripts</td></tr>
          <tr><td>history.md projected total</td><td><b>{ledger["catalogue_alignment"]["history_topline_total"]} + {ledger["catalogue_alignment"]["history_new_manuscripts"]} = {ledger["catalogue_alignment"]["history_projected_total"]}</b></td></tr>
          <tr><td>CONTENTS.md manuscript PDF links</td><td><b>{ledger["catalogue_alignment"]["contents_manuscript_links"]}</b></td></tr>
          <tr><td>CONTENTS.md overview PDF links</td><td><b>{ledger["catalogue_alignment"]["contents_overview_links"]}</b></td></tr>
          <tr><td>CONTENTS.md total PDF links</td><td><b>{ledger["catalogue_alignment"]["contents_total_pdf_links"]}</b></td></tr>
          <tr><td>Linked directories → unique stems</td><td><b>{ledger["catalogue_alignment"]["linked_directories"]}</b> → <b>{ledger["catalogue_alignment"]["linked_stems"]}</b> ({ledger["catalogue_alignment"]["linked_version_extra_directories"]} version extras)</td></tr>
          <tr><td>Disk directories → unique stems</td><td><b>{ledger["catalogue_alignment"]["disk_directories"]}</b> → <b>{ledger["catalogue_alignment"]["disk_stems"]}</b></td></tr>
          <tr><td>Unlinked directories</td><td><b>{ledger["catalogue_alignment"]["unlinked_directories"]}</b> = {ledger["catalogue_alignment"]["unlinked_version_extra_directories"]} older versions + {ledger["catalogue_alignment"]["unlinked_orphan_stems"]} orphan stems</td></tr>
          <tr><td>Linked stems + withdrawn</td><td><b>{ledger["catalogue_alignment"]["linked_stems"]} + {ledger["catalogue_alignment"]["withdrawn_orphan_stems"]} = {ledger["catalogue_alignment"]["linked_stems_plus_withdrawn"]}</b></td></tr>
          <tr><td>Orphan stems</td><td><b>{ledger["catalogue_alignment"]["withdrawn_orphan_stems"]}</b> withdrawal notices + <b>{ledger["catalogue_alignment"]["active_orphan_stems"]}</b> active manuscript</td></tr>
          <tr><td>One extra stem</td><td class="mono">{html.escape(str(ledger["catalogue_alignment"]["one_extra_stem"]))}</td></tr>
        </tbody>
      </table>
      <p class="muted">{html.escape(ledger["catalogue_alignment"]["reconciliation"])}</p>
      <p class="muted"><b>Status:</b> {html.escape(ledger["catalogue_alignment"]["reconciliation_status"])}. {html.escape(ledger["catalogue_alignment"]["reconciliation_note"])}</p>
    </div>
    <h2>Versioning vs formalization</h2>
    <div class="panel">
      <p><b>{ledger["versioning"]["versioned_stems"]}</b> manuscript stems have multiple dated directories; <b>{ledger["versioning"]["versioned_formalized"]}</b> are formalized ({ledger["versioning"]["versioned_formalized_percent"]}). Among single-version stems, <b>{ledger["versioning"]["single_version_formalized"]}/{ledger["versioning"]["single_version_stems"]}</b> are formalized ({ledger["versioning"]["single_version_formalized_percent"]}).</p>
      <p><b>{ledger["versioning"]["formalized_against_older"]}</b> formalized versioned stems target an older release; the maximum version span is <b>{ledger["versioning"]["max_span_days"]}</b> days.</p>
      <p class="muted">This is a descriptive association, not a causal claim; the versioned subset is only 28 stems.</p>
    </div>
    <h2>Formalization coverage by Lean category</h2>
    <div class="panel">{category_rows}</div>
    <h2>Family status grid</h2>
    <div class="panel">
      <div class="grid373" id="family-grid"></div>
      <div class="legend">
        <span><span class="swatch" style="background:#5ee6a8"></span>formalized + local seal</span>
        <span><span class="swatch" style="background:#1f6f5c"></span>formalized only</span>
        <span><span class="swatch" style="background:#2b4c6f"></span>local seal only</span>
        <span><span class="swatch" style="background:#1c2a3a"></span>neither</span>
      </div>
    </div>
  </section>

  <section id="families" class="section">
    <h2>Family ledger</h2>
    <div class="controls">
      <input id="family-search" type="search" placeholder="Search 373 families by title or index…">
      <button class="filter active" data-filter="all">All</button>
      <button class="filter" data-filter="formalized">Formalized</button>
      <button class="filter" data-filter="unformalized">Unformalized</button>
      <button class="filter" data-filter="versioned">Versioned</button>
      <button class="filter" data-filter="extreme">Extreme constant</button>
      <span class="muted" id="family-count"></span>
    </div>
    <div class="panel" style="max-height:70vh;overflow:auto">
      <table><thead><tr><th>#</th><th>Title</th><th>Dirs</th><th>Stems</th><th>Extra versions</th><th>Formalized</th><th>Matches</th><th>Local seal</th></tr></thead>
      <tbody id="family-body"></tbody></table>
    </div>
  </section>

  <section id="main" class="section">
    <h2>Main-result declaration audit</h2>
    <div class="panel">
      <p>Declarations: <b>{ledger["main_result_audit"]["declarations"]}</b> · files exist: <b class="ok">{ledger["main_result_audit"]["file_exists"]}</b> · declarations found: <b class="ok">{ledger["main_result_audit"]["declaration_found"]}</b> · comparators exist: <b class="ok">{ledger["main_result_audit"]["comparator_exists"]}</b> · theorem names match: <b class="ok">{ledger["main_result_audit"]["theorem_names_match"]}</b> · placeholder tokens: <b class="ok">{ledger["main_result_audit"]["placeholder_tokens"]}</b></p>
      <p class="muted">Solution module differs from declaration file for {ledger["main_result_audit"]["solution_module_file_mismatch"]} declarations; this is recorded but not treated as failure.</p>
      <p class="muted">Comparator inventory: <b>{ledger["comparator_audit"]["total_configs"]}</b> configs (<b>{ledger["comparator_audit"]["top_level_configs"]}</b> top-level + <b>{ledger["comparator_audit"]["nested_configs"]}</b> nested) · solution modules exist: <b>{ledger["comparator_audit"]["solution_modules_exist"]}</b> · challenge modules exist: <b>{ledger["comparator_audit"]["challenge_modules_exist"]}</b> · theorem names textually found: <b>{ledger["comparator_audit"]["theorem_text_found"]}</b> · not textually found (aggregation/imports): <b>{ledger["comparator_audit"]["theorem_text_not_found"]}</b>.</p>
    </div>
    <div class="panel" style="max-height:70vh;overflow:auto;margin-top:12px">
      <table><thead><tr><th>Declaration</th><th>File</th><th>Category</th><th>File</th><th>Decl</th><th>Comparator</th><th>Theorem</th></tr></thead>
      <tbody>{main_rows}</tbody></table>
    </div>
  </section>

  <section id="gaps" class="section">
    <h2>Withdrawal provenance</h2>
    <div class="panel">
      <p><b>{ledger["withdrawal_provenance"]["notices"]}</b> unlinked manuscripts are withdrawal notices dated <span class="mono">{html.escape(", ".join(ledger["withdrawal_provenance"]["withdrawn_dates"]))}</span>. Root notice: <span class="mono">{html.escape(", ".join(ledger["withdrawal_provenance"]["roots"]))}</span>.</p>
      <table><thead><tr><th>Withdrawn</th><th>Title</th><th>Directory</th><th>References</th><th>Archived manuscript</th></tr></thead><tbody>{withdrawal_rows}</tbody></table>
      <p class="muted">{html.escape(ledger["withdrawal_provenance"]["note"])}</p>
    </div>
    <h2>Version drift (all 28 versioned stems)</h2>
    <div class="panel"><table><thead><tr><th>Family</th><th>Stem</th><th>Versions</th><th>Oldest</th><th>Latest</th><th>Span (days)</th><th>Formalized</th><th>Against latest</th></tr></thead><tbody>{drift_rows}</tbody></table></div>
    <h2>Version lag among formalized manuscripts</h2>
    <div class="panel"><table><thead><tr><th>Family</th><th>Title</th><th>Formalized source</th><th>Latest release</th></tr></thead><tbody>{lag_rows}</tbody></table></div>
    <h2>Manuscript stems outside the family map</h2>
    <div class="panel"><table><thead><tr><th>Stem</th><th>Title</th><th>Directory</th><th>Status</th></tr></thead><tbody>{unmapped_rows}</tbody></table></div>
    <h2>Unreferenced comparator configurations</h2>
    <div class="panel"><p><b>{len(unref)}</b> comparator JSON files are not referenced by <span class="mono">status.main_results</span>.</p><details><summary>Show first 40</summary><ul>{unref_preview}</ul></details>{unref_more}</div>
    <h2>Local seal alignment</h2>
    <div class="panel">
      <p>{ledger["local_seals"]["chain_ok"]}/373 labels pass the cryptographic chain, but only <b>{ledger["local_seals"]["aligned_families"]}/{c["families"]}</b> catalogue families share a label with a local record. The catalogue index range is 1–378 with gaps; the local pipeline is contiguous 001–373.</p>
      <p><b>Orphan local labels:</b> <span class="mono">{html.escape(", ".join(str(x) for x in ledger["local_seals"]["orphan_labels"]))}</span></p>
      <p><b>Catalogue families without a local seal:</b> <span class="mono">{html.escape(", ".join(str(x) for x in ledger["local_seals"]["unsealed_families"]))}</span></p>
      <p class="muted">{html.escape(ledger["local_seals"]["alignment_note"])}</p>
    </div>
    <h2>Largest unformalized families</h2>
    <div class="panel">
      <p><b>{ledger["unformalized_families"]}</b> of {ledger["coverage"]["families"]} families have no formalized manuscript. Ranked by candidate constant matches, then manuscript count.</p>
      <table><thead><tr><th>#</th><th>Title</th><th>Dirs</th><th>Matches</th><th>TeX files</th></tr></thead><tbody>{debt_rows}</tbody></table>
    </div>
    <h2>Extraction extremes</h2>
    <div class="panel"><table><thead><tr><th>Family</th><th>Primary numeric constant</th></tr></thead><tbody>{outlier_rows}</tbody></table></div>
  </section>

  <section id="method" class="section">
    <h2>Method and scope</h2>
    <div class="panel">
      <p><b>Version stem.</b> Directory name with the trailing <span class="mono">-Month-D-YYYY</span> suffix removed. This groups releases of the same manuscript.</p>
      <p><b>Family map.</b> The 373 family records in <span class="mono">reports/math30_real_empirical_parameters.json</span> provide the preprint directories. Stems are matched to those directories.</p>
      <p><b>Catalogue reconciliation.</b> <span class="mono">CONTENTS.md</span> links are parsed directly. The README's 721 claim is compared against manuscript links, overview links, linked stems and unlinked disk stems. Withdrawal status is read from unlinked manuscript READMEs.</p>
      <p><b>Formalization map.</b> The 176 sources in <span class="mono">staging/openai_math/lean/formalization.yaml</span> are mapped by source-directory stem to families.</p>
      <p><b>Declaration audit.</b> Each of the 208 <span class="mono">status.main_results</span> entries is checked for file existence, terminal or full dotted declaration presence after comment stripping, comparator existence, and theorem-name membership in the comparator JSON. Placeholder tokens are counted after comment stripping.</p>
      <p><b>Local seal chain.</b> For labels 001–373, the report SHA-256, certificate SHA-256 and the two Lean string constants are recomputed over LF-normalised bytes. The catalogue is indexed 1–378 with five gaps, so only 368 labels align with a catalogue family; 5 labels are orphaned and 5 families are unsealed.</p>
      <p><b>What this is not.</b> This is not a Lean build, not a kernel check, and not a proof of any manuscript. The official catalogue itself marks review status as <span class="mono">{html.escape(str(ledger["formalization"]["review_status"]))}</span>.</p>
    </div>
    <h2>Reproduce</h2>
    <pre>C:\\Python314\\python.exe mcp\\t2n\\core\\verification_atlas.py</pre>
    <h2>Source seals</h2>
    <pre>formalization.yaml  {ledger["sources"]["formalization_sha256"]}
empirical database {ledger["sources"]["empirical_sha256"]}
manifest.json      {ledger["sources"]["manifest_rows"]} rows (digest omitted: circular ledger)
CONTENTS.md        {ledger["sources"]["contents_sha256"]}
history.md         {ledger["sources"]["history_sha256"]}</pre>
  </section>
</div>

<script>
const FAMILIES = {families_json};
const grid = document.getElementById('family-grid');
for (const f of FAMILIES) {{
  const d = document.createElement('div');
  d.className = 'cell ' + (f.formalized && f.local_chain_ok ? 'both' : f.formalized ? 'formalized' : f.local_chain_ok ? 'local' : '');
  d.title = '#' + String(f.index).padStart(3,'0') + ' ' + f.title + ' | formalized: ' + f.formalized + ' | local seal: ' + f.local_chain_ok;
  grid.appendChild(d);
}}
const body = document.getElementById('family-body');
const search = document.getElementById('family-search');
const countEl = document.getElementById('family-count');
let filter = 'all';
function render() {{
  const q = search.value.toLowerCase();
  body.textContent = '';
  let shown = 0;
  for (const f of FAMILIES) {{
    const hay = (String(f.index).padStart(3,'0') + ' ' + f.title).toLowerCase();
    if (q && !hay.includes(q)) continue;
    if (filter === 'formalized' && !f.formalized) continue;
    if (filter === 'unformalized' && f.formalized) continue;
    if (filter === 'versioned' && f.version_extra <= 0) continue;
    if (filter === 'extreme' && !f.extreme_constant) continue;
    shown++;
    const tr = document.createElement('tr');
    const cells = [
      String(f.index).padStart(3,'0'),
      f.title,
      f.manuscript_count,
      f.unique_manuscripts,
      f.version_extra,
      f.formalized ? ('yes (' + f.formalized_source_count + ')') : 'no',
      f.candidate_matches,
      f.local_chain_ok ? 'ok' : 'missing'
    ];
    for (const value of cells) {{
      const td = document.createElement('td');
      td.textContent = value;
      tr.appendChild(td);
    }}
    body.appendChild(tr);
  }}
  countEl.textContent = shown + ' shown';
}}
search.addEventListener('input', render);
document.querySelectorAll('.filter').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('.filter').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    filter = btn.dataset.filter;
    render();
  }});
}});
document.querySelectorAll('.tab').forEach(tab => {{
  tab.addEventListener('click', () => {{
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(tab.dataset.tab).classList.add('active');
  }});
}});
render();
</script>
</body>
</html>
"""


def render_svg(ledger: dict) -> str:
    c = ledger["coverage"]
    fams = ledger["families"]
    width, height = 1400, 1080
    cols = 30
    cell = 26
    gap = 4
    grid_x = 40
    grid_y = 620
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#0b0f14"/>',
        '<style>text{font-family:Consolas,monospace;fill:#dbe7f3}.muted{fill:#8fa3b8}.big{font-size:30px;font-weight:700}.label{font-size:13px}.small{font-size:11px}</style>',
        '<text x="40" y="52" class="big">OPENAI MATH · VERIFICATION PROVENANCE ATLAS</text>',
        '<text x="40" y="78" class="label muted">373 families · 722 manuscript stems · 176 formalized manuscripts · 208 main-result declarations · 419 comparator configs · 3 withdrawal notices · 1 unlinked active stem</text>',
    ]
    funnel = [
        ("preprint directories", c["preprint_directories"]),
        ("unique manuscript stems", c["unique_manuscript_stems"]),
        ("result families", c["families"]),
        ("formalized manuscripts", c["formalized_sources"]),
        ("formalized families", c["formalized_families"]),
        ("main-result declarations", c["main_result_declarations"]),
        ("comparator configs", c["comparator_configs"]),
    ]
    max_value = 751
    y = 130
    for label, value in funnel:
        bar_w = (value * 900 + max_value // 2) // max_value
        parts.append(f'<text x="40" y="{y + 14}" class="label muted">{html.escape(label)}</text>')
        parts.append(f'<rect x="300" y="{y}" width="900" height="18" fill="#16212d" rx="9"/>')
        parts.append(f'<rect x="300" y="{y}" width="{bar_w}" height="18" fill="#2a9d8f" rx="9"/>')
        parts.append(f'<text x="1220" y="{y + 14}" class="label">{value}</text>')
        y += 42

    parts.append('<text x="40" y="540" class="label">FAMILY STATUS GRID</text>')
    parts.append('<text x="40" y="562" class="small muted">green = formalized + local seal · teal = formalized only · blue = local seal only · grey = neither</text>')
    for i, fam in enumerate(fams):
        row = i // cols
        col = i % cols
        x = grid_x + col * (cell + gap)
        py = grid_y + row * (cell + gap)
        if fam["formalized"] and fam["local_chain_ok"]:
            fill, stroke = "#5ee6a8", "#9ff5cf"
        elif fam["formalized"]:
            fill, stroke = "#1f6f5c", "#2f9d80"
        elif fam["local_chain_ok"]:
            fill, stroke = "#2b4c6f", "#3d6f9e"
        else:
            fill, stroke = "#1c2a3a", "#223247"
        parts.append(
            f'<rect x="{x}" y="{py}" width="{cell}" height="{cell}" rx="3" fill="{fill}" stroke="{stroke}"/>'
            f'<title>#{fam["index"]:03d} {html.escape(fam["title"])}</title>'
        )
    legend_y = height - 40
    parts.append(f'<text x="40" y="{legend_y}" class="small muted">Local seal labels: {c["local_hash_chain_pass"]}/373 · aligned families: {c["local_aligned_families"]}/{c["families"]} · main results: {ledger["main_result_audit"]["declaration_found"]}/{ledger["main_result_audit"]["declarations"]} found · placeholders: {ledger["main_result_audit"]["placeholder_tokens"]}</text>')
    parts.append(f'<text x="1000" y="{legend_y}" class="small muted">manifest rows: {c["manifest_rows"]} · generated: {ledger["generated_at"]}</text>')
    alignment = ledger["catalogue_alignment"]
    parts.append(
        f'<text x="40" y="{height - 18}" class="small muted">Catalogue: '
        f'{alignment["contents_manuscript_links"]} manuscript links + '
        f'{alignment["contents_overview_links"]} overview = '
        f'{alignment["contents_total_pdf_links"]} PDF links · '
        f'{alignment["linked_stems"]} linked + {alignment["withdrawn_orphan_stems"]} withdrawn = '
        f'{alignment["linked_stems_plus_withdrawn"]} · +1 active orphan = '
        f'{alignment["disk_stems"]} stems</text>'
    )
    parts.append("</svg>")
    return "".join(parts)


def render_markdown(ledger: dict) -> str:
    c = ledger["coverage"]
    audit = ledger["main_result_audit"]
    lines = [
        "# OpenAI Math · Verification Provenance Atlas",
        "",
        f"Generated from local disk on {ledger['generated_at']}.",
        "",
        "## Headline",
        "",
        f"- {c['preprint_directories']} preprint directories compress to {c['unique_manuscript_stems']} unique manuscript stems across {c['families']} result families.",
        f"- {c['formalized_sources']} manuscripts are formalized, covering {c['formalized_families']}/{c['families']} families ({c['percentages']['families_formalized']}); {ledger['unformalized_families']} families remain unformalized.",
        f"- {c['main_result_declarations']} main-result declarations audited: {audit['file_exists']} files exist, {audit['declaration_found']} declarations found, {audit['comparator_exists']} comparators exist, {audit['theorem_names_match']} theorem names match, {audit['placeholder_tokens']} placeholder tokens.",
        f"- {c['comparator_configs']} comparator configs exist; {c['referenced_comparator_configs']} are referenced by `status.main_results`, leaving {c['unreferenced_comparator_configs']} unreferenced.",
        f"- Local seal labels: {c['local_hash_chain_pass']}/373 pass the LF-normalised SHA-256 report → certificate → Lean chain. Only {c['local_aligned_families']}/{c['families']} catalogue families share a label; 5 labels are orphaned and 5 families are unsealed.",
        f"- Catalogue reconciliation: {ledger['catalogue_alignment']['contents_manuscript_links']} manuscript PDF links + {ledger['catalogue_alignment']['contents_overview_links']} overview link = {ledger['catalogue_alignment']['contents_total_pdf_links']} PDF links. Disk has {c['preprint_directories']} directories and {c['unique_manuscript_stems']} stems, including {ledger['catalogue_alignment']['withdrawn_orphan_stems']} withdrawal notices and {ledger['catalogue_alignment']['active_orphan_stems']} active unlinked manuscript.",
        "",
        "## Findings",
        "",
        "1. **Versioning is real.** 28 manuscript stems have multiple dated directories; 29 directories are extra releases. Only 3 formalized stems are versioned (3/28, 10.71%) versus 173/694 single-version stems (24.93%). Two of the three formalized versioned stems are formalized against an older release (Taming: Sep 23 vs Oct 6; Quasi-RH: Sep 30 vs Oct 5).",
        f"2. **Coverage is partial.** {c['formalized_families']} of {c['families']} families have at least one formalized manuscript ({c['percentages']['families_formalized']}). The remaining families have no Lean source in the official catalogue.",
        "3. **The 208 catalogued declarations are internally linked.** Files, declarations, comparator configs and theorem-name lists all match, with zero `sorry`/`admit`/`axiom`/`Abort` tokens in the declaration files.",
        f"4. **Comparator inventory is larger than the catalogue.** {c['comparator_configs']} configs ({ledger['comparator_audit']['top_level_configs']} top-level + {ledger['comparator_audit']['nested_configs']} nested) exist but only {c['referenced_comparator_configs']} are named by `status.main_results`; {c['unreferenced_comparator_configs']} are not catalogued there. All {c['comparator_configs']} solution and challenge modules exist; {ledger['comparator_audit']['theorem_text_found']} theorem sets are textually found in the declared solution module, while {ledger['comparator_audit']['theorem_text_not_found']} are hidden by aggregation/imports. This is an inventory gap, not proof that the extra configs are wrong.",
        f"5. **Four manuscript stems fall outside the 373-family map, and three are retractions.** Three are withdrawal notices dated {', '.join(ledger['withdrawal_provenance']['withdrawn_dates'])}: Kuga–Satake correspondences, Weil classes on split abelian eightfolds, and the rational Hodge conjecture for products of K3 surfaces. The remaining stem, *Sharp integral fillings in CAT(0) spaces*, is an active unlinked manuscript. The root notice is the Weil-classes paper; the other two notices cite its sign error in the stabilization-trace argument. Each notice says the withdrawal concerns the proof, not the truth of the statement.",
        "6. **The local Math 3.0 seal chain is intact but misaligned.** All 373 labels 001–373 pass their report→certificate→Lean cryptographic chain, but the catalogue is indexed 1–378 with gaps 45, 61, 70, 123 and 163. Five local labels are orphaned; families 374–378 have no local seal; only 368 labels align. The underlying coordinates are also generated by a deterministic formula, not extracted from the manuscripts.",
        f"7. **Verification debt is concentrated.** {ledger['unformalized_families']} families have no formalized manuscript. The largest unformalized clusters include family {ledger['verification_debt'][0]['index']} ({ledger['verification_debt'][0]['candidate_matches']} candidate matches), family {ledger['verification_debt'][1]['index']} ({ledger['verification_debt'][1]['candidate_matches']}) and family {ledger['verification_debt'][2]['index']} ({ledger['verification_debt'][2]['candidate_matches']}). The full ranked list is in the JSON ledger.",
        f"8. **The 721 vs 722 discrepancy is most economically explained by one active orphan stem.** history.md records {ledger['catalogue_alignment']['history_formalized_topline']}/{ledger['catalogue_alignment']['history_topline_total']} = {ledger['catalogue_alignment']['history_topline_percent']}% top-line formalization and two new manuscripts, so {ledger['catalogue_alignment']['history_topline_total']} + {ledger['catalogue_alignment']['history_new_manuscripts']} = {ledger['catalogue_alignment']['history_projected_total']}. The catalogue links 718 unique active stems; adding the 3 withdrawn notices gives 721. The remaining stem is *{ledger['catalogue_alignment']['one_extra_stem']}*, the single active orphan and the +1 to 722. Independently, `CONTENTS.md` has 720 manuscript PDF links plus 1 overview link = 721 PDF links, so 721 is also a PDF-link count. The atlas reports both identities instead of forcing a false one-stem explanation.",
        "",
        "## Catalogue reconciliation",
        "",
        f"- README claim: {ledger['catalogue_alignment']['readme_claim_manuscripts']} manuscripts.",
        f"- history.md: {ledger['catalogue_alignment']['history_formalized_topline']}/{ledger['catalogue_alignment']['history_topline_total']} = {ledger['catalogue_alignment']['history_topline_percent']}% top-line formalization; plus {ledger['catalogue_alignment']['history_new_manuscripts']} new manuscripts gives {ledger['catalogue_alignment']['history_projected_total']}.",
        f"- CONTENTS.md: {ledger['catalogue_alignment']['contents_manuscript_links']} manuscript links + {ledger['catalogue_alignment']['contents_overview_links']} overview link = {ledger['catalogue_alignment']['contents_total_pdf_links']} PDF links.",
        f"- Linked directories: {ledger['catalogue_alignment']['linked_directories']}; linked stems: {ledger['catalogue_alignment']['linked_stems']}; linked version extras: {ledger['catalogue_alignment']['linked_version_extra_directories']}.",
        f"- Disk directories: {ledger['catalogue_alignment']['disk_directories']}; disk stems: {ledger['catalogue_alignment']['disk_stems']}.",
        f"- Unlinked directories: {ledger['catalogue_alignment']['unlinked_directories']} = {ledger['catalogue_alignment']['unlinked_version_extra_directories']} older versions + {ledger['catalogue_alignment']['unlinked_orphan_stems']} orphan stems.",
        f"- Orphan stems: {ledger['catalogue_alignment']['withdrawn_orphan_stems']} withdrawal notices + {ledger['catalogue_alignment']['active_orphan_stems']} active manuscript.",
        f"- Linked stems + withdrawn = {ledger['catalogue_alignment']['linked_stems']} + {ledger['catalogue_alignment']['withdrawn_orphan_stems']} = {ledger['catalogue_alignment']['linked_stems_plus_withdrawn']}; the one extra active stem is `{ledger['catalogue_alignment']['one_extra_stem']}`.",
        f"- Status: **{ledger['catalogue_alignment']['reconciliation_status']}**. {ledger['catalogue_alignment']['reconciliation_note']}",
        "",
        "## Scope and limitations",
        "",
        "- The official `formalization.yaml` sets `review.status: unchecked`.",
        "- The declaration audit checks text presence, not Lean kernel acceptance.",
        "- Unreferenced comparator configs may cover definitions or alternative formalizations; they are reported as uncatalogued, not invalid.",
        "- Withdrawal status is transcribed from README notices; the stated sign error is not independently re-verified here.",
        "- The local 373-family seals are integrity seals, not proofs of the manuscripts.",
        "- No Beal, Euler, Navier–Stokes, or other open problem is proved here.",
        "",
        "## Artifacts",
        "",
        "- `reports/openai_math_verification_atlas.json` — full ledger.",
        "- `exports/openai_math_verification_atlas.html` — interactive dashboard.",
        "- `exports/openai_math_verification_atlas.svg` — static coverage plate.",
        "- Builder: `mcp/t2n/core/verification_atlas.py`.",
        "",
        "## Reproduce",
        "",
        "```powershell",
        "C:\\Python314\\python.exe mcp\\t2n\\core\\verification_atlas.py",
        "```",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    for required in (PREPRINTS, LEAN, CONTENTS, HISTORY, EMPIRICAL, FORMALIZATION, MANIFEST):
        if not required.exists():
            print(f"FATAL: missing required path: {required}", file=sys.stderr)
            return 2
    ledger = build_ledger()
    assert_no_floats(ledger)
    out_json = ROOT / "reports" / "openai_math_verification_atlas.json"
    out_html = ROOT / "exports" / "openai_math_verification_atlas.html"
    out_svg = ROOT / "exports" / "openai_math_verification_atlas.svg"
    out_md = ROOT / "exports" / "OPENAI_MATH_VERIFICATION_ATLAS.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    out_html.write_text(render_html(ledger), encoding="utf-8", newline="\n")
    out_svg.write_text(render_svg(ledger), encoding="utf-8", newline="\n")
    out_md.write_text(render_markdown(ledger), encoding="utf-8", newline="\n")
    c = ledger["coverage"]
    print("ATLAS_BUILD_OK")
    print(f"families={c['families']} stems={c['unique_manuscript_stems']} dirs={c['preprint_directories']}")
    print(f"formalized_manuscripts={c['formalized_sources']} formalized_families={c['formalized_families']}")
    print(f"main_results={c['main_result_declarations']} placeholders={ledger['main_result_audit']['placeholder_tokens']}")
    print(f"comparators={c['comparator_configs']} referenced={c['referenced_comparator_configs']} unreferenced={c['unreferenced_comparator_configs']}")
    print(f"local_chain={c['local_hash_chain_pass']}/373")
    print(f"wrote {out_json.relative_to(ROOT)}")
    print(f"wrote {out_html.relative_to(ROOT)}")
    print(f"wrote {out_svg.relative_to(ROOT)}")
    print(f"wrote {out_md.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
