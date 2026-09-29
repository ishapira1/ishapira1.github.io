"""Read-only Google Analytics 4 MCP server for Codex."""

from __future__ import annotations

import os
import re
from typing import Any

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from mcp.server import MCPServer


PROPERTY_ID = os.environ.get("GA4_PROPERTY_ID", "").strip()
NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")

mcp = MCPServer(
    "GA4 Analytics",
    instructions=(
        "Read-only reporting access to one configured Google Analytics 4 "
        "property. Use run_ga4_report to answer traffic and engagement "
        "questions. Never attempt to modify Analytics configuration."
    ),
)


def _validate_names(names: list[str], label: str, maximum: int) -> None:
    if not names:
        raise ValueError(f"Provide at least one {label}.")
    if len(names) > maximum:
        raise ValueError(f"Provide no more than {maximum} {label}s.")

    invalid = [name for name in names if not NAME_PATTERN.fullmatch(name)]
    if invalid:
        raise ValueError(f"Invalid {label} names: {', '.join(invalid)}")


@mcp.tool()
def run_ga4_report(
    dimensions: list[str],
    metrics: list[str],
    start_date: str = "28daysAgo",
    end_date: str = "today",
    limit: int = 100,
) -> dict[str, Any]:
    """Run a read-only GA4 report for the configured property.

    Common dimensions include date, country, city, deviceCategory, pagePath,
    landingPage, sessionDefaultChannelGroup, and sessionSourceMedium.
    Common metrics include activeUsers, newUsers, sessions, engagedSessions,
    engagementRate, screenPageViews, and eventCount.
    """
    if not PROPERTY_ID:
        raise RuntimeError("GA4_PROPERTY_ID is not configured.")

    _validate_names(dimensions, "dimension", 9)
    _validate_names(metrics, "metric", 10)
    safe_limit = max(1, min(int(limit), 1_000))

    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name=name) for name in dimensions],
        metrics=[Metric(name=name) for name in metrics],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        limit=safe_limit,
    )
    response = BetaAnalyticsDataClient().run_report(request)

    rows: list[dict[str, str]] = []
    for row in response.rows:
        result: dict[str, str] = {}

        for header, value in zip(
            response.dimension_headers,
            row.dimension_values,
            strict=True,
        ):
            result[header.name] = value.value

        for header, value in zip(
            response.metric_headers,
            row.metric_values,
            strict=True,
        ):
            result[header.name] = value.value

        rows.append(result)

    return {
        "property_id": PROPERTY_ID,
        "date_range": {"start": start_date, "end": end_date},
        "row_count": response.row_count,
        "returned_rows": len(rows),
        "rows": rows,
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
