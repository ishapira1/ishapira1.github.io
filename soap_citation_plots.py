"""Create SOAP citation-growth plots from Google Scholar relative added dates."""

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from citation_plots import add_legend_below, style_axis


REFERENCE_DATE = pd.Timestamp("2026-08-22")
OUTPUT_DIR = Path(__file__).resolve().parent / "citation_plots"

# All 249 Google Scholar results supplied by the user, ordered by page.
DAYS_AGO = [
    7, 12, 12, 14, 16, 18, 18, 25, 26, 27,
    30, 30, 30, 35, 39, 40, 41, 42, 44, 44,
    45, 48, 49, 49, 53, 53, 55, 56, 56, 57,
    58, 58, 59, 59, 60, 60, 60, 63, 67, 67,
    71, 71, 73, 78, 78, 79, 79, 80, 80, 81,
    81, 81, 81, 84, 84, 84, 84, 85, 85, 85,
    85, 86, 86, 87, 87, 88, 88, 88, 88, 89,
    89, 92, 94, 94, 94, 94, 95, 95, 95, 98,
    99, 99, 100, 101, 101, 101, 102, 102, 103, 103,
    103, 103, 103, 104, 105, 105, 105, 105, 106, 106,
    106, 106, 106, 106, 106, 106, 106, 106, 107, 107,
    107, 107, 108, 109, 113, 114, 118, 120, 120, 122,
    123, 127, 128, 128, 133, 134, 134, 134, 136, 136,
    142, 143, 143, 144, 148, 149, 155, 156, 156, 157,
    157, 163, 163, 164, 165, 168, 172, 172, 173, 173,
    175, 175, 177, 177, 179, 181, 183, 183, 183, 186,
    187, 192, 192, 193, 195, 196, 197, 198, 199, 199,
    199, 199, 200, 201, 201, 202, 204, 204, 204, 204,
    205, 205, 205, 206, 206, 212, 215, 217, 218, 221,
    226, 240, 242, 243, 245, 246, 254, 257, 257, 259,
    259, 264, 270, 275, 277, 278, 285, 286, 294, 296,
    297, 299, 301, 303, 304, 306, 306, 309, 311, 311,
    311, 311, 312, 313, 313, 313, 316, 318, 318, 318,
    318, 318, 318, 324, 325, 325, 326, 326, 326, 327,
    330, 337, 337, 340, 352, 352, 359, 361, 365,
]

TEAL = "#73b3ab"
ORANGE = "#d4651a"


def make_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return event-level, daily cumulative, and monthly SOAP data."""
    citations = pd.DataFrame(
        {
            "citation_id": range(1, len(DAYS_AGO) + 1),
            "days_ago": DAYS_AGO,
        }
    )
    citations["date_added"] = REFERENCE_DATE - pd.to_timedelta(
        citations["days_ago"], unit="D"
    )
    citations = citations.sort_values(
        ["date_added", "citation_id"], ignore_index=True
    )

    daily_index = pd.date_range(citations["date_added"].min(), REFERENCE_DATE, freq="D")
    daily_counts = citations.groupby("date_added").size().reindex(daily_index, fill_value=0)
    cumulative = daily_counts.cumsum().rename("cumulative_citations").reset_index()
    cumulative = cumulative.rename(columns={"index": "date"})

    month_index = pd.period_range(
        citations["date_added"].min().to_period("M"),
        REFERENCE_DATE.to_period("M"),
        freq="M",
    )
    monthly = (
        citations.assign(month=citations["date_added"].dt.to_period("M"))
        .groupby("month")
        .size()
        .reindex(month_index, fill_value=0)
        .rename("citations")
        .reset_index()
        .rename(columns={"index": "month"})
    )
    monthly["partial_month"] = False
    monthly.loc[[0, len(monthly) - 1], "partial_month"] = True
    monthly["month_label"] = monthly["month"].dt.strftime("%b %Y")
    monthly.loc[monthly["partial_month"], "month_label"] += "*"
    return citations, cumulative, monthly


def plot_cumulative(cumulative: pd.DataFrame) -> None:
    """Save the cumulative SOAP citation chart."""
    fig, ax = plt.subplots(figsize=(12, 6.8))
    sns.lineplot(
        data=cumulative,
        x="date",
        y="cumulative_citations",
        color=TEAL,
        linewidth=3,
        drawstyle="steps-post",
        label="Cumulative SOAP citations",
        ax=ax,
    )
    ax.fill_between(
        cumulative["date"],
        cumulative["cumulative_citations"],
        step="post",
        color=TEAL,
        alpha=0.15,
    )
    ax.set_xlim(cumulative["date"].min(), REFERENCE_DATE)
    ax.set_ylim(0, len(DAYS_AGO) + 15)
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    style_axis(
        ax,
        "SOAP: cumulative citations added over the past year",
        "Google Scholar date added",
        "Cumulative number of citations",
    )
    fig.autofmt_xdate(rotation=35, ha="right")
    fig.tight_layout(rect=(0, 0.16, 1, 1))
    add_legend_below(fig, ax)
    fig.savefig(
        OUTPUT_DIR / "soap_cumulative_citations.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)


def plot_monthly(monthly: pd.DataFrame) -> None:
    """Save the monthly SOAP citation chart."""
    fig, ax = plt.subplots(figsize=(13, 7))
    bars = sns.barplot(
        data=monthly,
        x="month_label",
        y="citations",
        color=ORANGE,
        label="SOAP citations per month",
        ax=ax,
    )
    for container in bars.containers:
        bars.bar_label(container, fontsize=12, padding=4)
    ax.set_ylim(0, monthly["citations"].max() + 8)
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    style_axis(
        ax,
        "SOAP citations added per month",
        "Month (* partial month)",
        "Number of citations",
    )
    ax.tick_params(axis="x", rotation=40)
    for label in ax.get_xticklabels():
        label.set_horizontalalignment("right")
    fig.tight_layout(rect=(0, 0.16, 1, 1))
    add_legend_below(fig, ax)
    fig.savefig(
        OUTPUT_DIR / "soap_citations_per_month.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(context="notebook")
    sns.set_style("white")

    citations, cumulative, monthly = make_data()
    citations.to_csv(OUTPUT_DIR / "soap_citation_dates.csv", index=False)
    monthly[["month_label", "citations", "partial_month"]].to_csv(
        OUTPUT_DIR / "soap_citations_per_month.csv", index=False
    )
    plot_cumulative(cumulative)
    plot_monthly(monthly)

    print(f"Created {len(citations)} SOAP citation records.")
    print(monthly[["month_label", "citations"]].to_string(index=False))


if __name__ == "__main__":
    main()
