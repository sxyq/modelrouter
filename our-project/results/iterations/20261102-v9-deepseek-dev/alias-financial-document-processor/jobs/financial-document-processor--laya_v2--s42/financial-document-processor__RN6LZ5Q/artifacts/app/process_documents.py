#!/usr/bin/env python3
"""Classify mixed JPG/PDF documents, move them, and summarize invoices."""

from __future__ import annotations

import csv
import re
import shutil
import subprocess
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

DOCUMENTS_DIR = Path("/app/documents")
INVOICES_DIR = Path("/app/invoices")
OTHER_DIR = Path("/app/other")
SUMMARY_PATH = INVOICES_DIR / "summary.csv"


def extract_text(path: Path) -> str:
    """Return embedded PDF text or OCR text for an image."""
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        result = subprocess.run(
            ["pdftotext", "-layout", str(path), "-"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout
    if suffix in {".jpg", ".jpeg", ".png", ".tif", ".tiff"}:
        result = subprocess.run(
            ["tesseract", str(path), "stdout", "--psm", "6"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout
    return ""


def is_invoice(text: str) -> bool:
    """Classify based on invoice-specific document language."""
    lower = text.lower()
    if re.search(r"\binvoice\b", lower):
        return True
    # Fallback indicators for invoice layouts that do not print a heading.
    has_amount_due = "amount due" in lower or "balance due" in lower
    has_bill_to = "bill to" in lower
    has_total = re.search(r"(?<!sub)\btotal\b", lower) is not None
    return has_total and (has_amount_due or has_bill_to)


def parse_amount(raw: str) -> Decimal | None:
    """Parse a currency-like number, supporting both 1,234.56 and 1 234,56."""
    s = raw.strip()
    s = re.sub(r"(?i)\b(?:usd|eur|gbp|cad|aud|inr|jpy)\b", "", s)
    s = s.replace("$", "").replace("€", "").replace("£", "")
    s = re.sub(r"[^0-9,.\-]", "", s)
    if not s or not re.search(r"\d", s):
        return None

    if "," in s and "." in s:
        # The rightmost separator is the decimal separator.
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        compact = s.replace(" ", "")
        # A trailing comma with 1-2 digits is a decimal comma; otherwise it is
        # a thousands separator.
        if re.search(r",\d{1,2}$", compact):
            s = compact.replace(",", ".")
        else:
            s = compact.replace(",", "")
    elif "." in s:
        # Handle multiple dots as thousands separators if the last group is
        # not a conventional one/two-digit decimal.
        if s.count(".") > 1:
            if re.search(r"\.\d{1,2}$", s):
                s = s.replace(".", "", s.count(".") - 1)
            else:
                s = s.replace(".", "")
        else:
            s = s.replace(" ", "")
    else:
        s = s.replace(" ", "")
    try:
        return Decimal(s)
    except InvalidOperation:
        return None


def currency_amounts(line: str) -> list[Decimal]:
    """Extract amount values from a line, respecting $ delimiters when present."""
    values: list[Decimal] = []
    if "$" in line:
        for part in line.split("$")[1:]:
            match = re.match(r"\s*([0-9][0-9\s.,]*)", part)
            if match:
                value = parse_amount(match.group(1))
                if value is not None:
                    values.append(value)
        if values:
            return values

    # No currency delimiter: extract numeric candidates. A space may be a
    # thousands separator, so consume groups of three digits when present.
    pattern = re.compile(r"(?<![\d.,])[-+]?\d[\d]*(?:[ \u00a0]\d{3})*(?:[.,]\d{1,2})?(?![\d])")
    for match in pattern.finditer(line):
        token = match.group(0)
        # Ignore percentages such as the 10 in "VAT [%] 10%".
        if match.end() < len(line) and line[match.end()] == "%":
            continue
        value = parse_amount(token)
        if value is not None:
            values.append(value)
    return values


def extract_amounts(text: str) -> tuple[Decimal, Decimal]:
    """Extract (total including tax, VAT). Missing VAT is represented as 0."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    total_values: list[Decimal] = []

    # Prefer a "Total"/"TotalPrice"/"Grand Total" line over "Amount Due".
    for line in lines:
        lower = line.lower()
        if "subtotal" in lower or "sub total" in lower:
            continue
        total_match = re.search(
            r"\b(?:grand\s+total|total\s*price|total)\b", lower
        )
        if total_match:
            # Prefer amounts appearing after the label (e.g. "TotalPrice 4031.0"),
            # not digits embedded in the label itself.
            vals = currency_amounts(line[total_match.end():])
            if not vals:
                vals = currency_amounts(line)
            if vals:
                total_values = vals
                break

    # Fall back to amount/balance due only when no total line was found.
    if not total_values:
        for line in lines:
            lower = line.lower()
            if "amount due" in lower or "balance due" in lower:
                vals = currency_amounts(line)
                if vals:
                    total_values = vals
                    break

    if not total_values:
        raise ValueError("could not find a total amount")

    if len(total_values) >= 3:
        # Summary tables commonly list: net worth, VAT, gross worth.
        vat = total_values[-2]
        total = total_values[-1]
    elif len(total_values) == 2:
        # Ambiguous two-value layouts: the last amount is generally the final
        # amount, while a separately labelled VAT line is handled below.
        total = total_values[-1]
        vat = Decimal("0")
    else:
        total = total_values[0]
        vat = Decimal("0")

    if len(total_values) < 3:
        # Look for an explicitly labelled VAT/Tax/GST amount.
        for line in lines:
            lower = line.lower()
            if re.search(r"\b(?:vat|tax|gst)\b", lower):
                vals = currency_amounts(line)
                # Remove percentage-like values and values that duplicate total.
                candidates = [v for v in vals if v != total]
                if candidates:
                    vat = candidates[-1]
                    break

    return total, vat


def format_amount(value: Decimal) -> str:
    return f"{value:.2f}"


def main() -> int:
    INVOICES_DIR.mkdir(parents=True, exist_ok=True)
    OTHER_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(p for p in DOCUMENTS_DIR.iterdir() if p.is_file())
    rows: list[tuple[str, Decimal, Decimal]] = []
    moves: list[tuple[Path, Path, str]] = []

    for path in files:
        text = extract_text(path)
        if is_invoice(text):
            total, vat = extract_amounts(text)
            rows.append((path.name, total, vat))
            moves.append((path, INVOICES_DIR / path.name, "invoice"))
        else:
            moves.append((path, OTHER_DIR / path.name, "other"))

    # Move only after all invoices have parsed successfully.
    for source, destination, _kind in moves:
        if destination.exists():
            raise FileExistsError(f"destination already exists: {destination}")
        shutil.move(str(source), str(destination))

    total_sum = sum((row[1] for row in rows), Decimal("0"))
    vat_sum = sum((row[2] for row in rows), Decimal("0"))

    with SUMMARY_PATH.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["filename", "total_amount", "vat_amount"])
        for filename, total, vat in rows:
            writer.writerow([filename, format_amount(total), format_amount(vat)])
        writer.writerow(["total", format_amount(total_sum), format_amount(vat_sum)])

    print(f"invoices: {len(rows)}")
    for filename, total, vat in rows:
        print(f"  {filename}: total={format_amount(total)} vat={format_amount(vat)}")
    print(f"other: {len(moves) - len(rows)}")
    print(f"summary: {SUMMARY_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
