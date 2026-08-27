"""Lightweight result object returned by every validator."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """Outcome of a single validation check.

    ``passed`` indicates whether the check succeeded; ``details`` holds
    optional human-readable diagnostics describing what failed, allowing
    callers to accumulate multiple results into one report.
    """

    passed: bool
    details: list[str] = field(default_factory=list)

    @property
    def message(self) -> str:
        """Concise, log-friendly summary of the outcome."""
        head = "passed" if self.passed else "failed"
        if not self.details:
            return f"Validation {head}"
        return f"Validation {head}: {self.details[0]}"


def merge_results(primary: ValidationResult, *others: ValidationResult) -> ValidationResult:
    """Combine results so the merged outcome fails iff any input failed.

    Diagnostic details are concatenated in argument order for a complete,
    auditable picture.
    """

    def _merge(left: ValidationResult, right: ValidationResult) -> ValidationResult:
        return ValidationResult(
            passed=left.passed and right.passed,
            details=[*left.details, *right.details],
        )

    combined: ValidationResult = primary
    for other in others:
        combined = _merge(combined, other)
    return combined
