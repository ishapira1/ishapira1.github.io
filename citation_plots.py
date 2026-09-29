"""Create citation-growth plots from Google Scholar's relative added dates."""

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


REFERENCE_DATE = pd.Timestamp("2026-08-22")
OUTPUT_DIR = Path(__file__).resolve().parent / "citation_plots"

# One value per Google Scholar result, in the order supplied by the user.
DAYS_AGO = [
    8,
    14,
    16,
    20,
    41,
    44,
    52,
    56,
    57,
    57,
    66,
    67,
    68,
    70,
    71,
    84,
    86,
    91,
    94,
    99,
    100,
    106,
    110,
    116,
    126,
    131,
    133,
    136,
    137,
    137,
    142,
    143,
    146,
    147,
    157,
    160,
    163,
    165,
    222,
]

TEAL = "#73b3ab"
ORANGE = "#d4651a"


def style_axis(ax: plt.Axes, title: str, xlabel: str, ylabel: str) -> None:
    """Apply the shared publication-style formatting."""
    ax.set_title(title, fontsize=20, pad=18, weight="semibold")
    ax.set_xlabel(xlabel, fontsize=15, labelpad=10)
    ax.set_ylabel(ylabel, fontsize=15, labelpad=10)
    ax.tick_params(axis="both", labelsize=12)
    ax.grid(axis="y", color="#d9d9d9", linewidth=0.8)
    ax.grid(axis="x", visible=False)
    sns.despine(ax=ax)


def add_legend_below(fig: plt.Figure, ax: plt.Axes) -> None:
    """Move the legend below the full plotting area without covering labels."""
    handles, labels = ax.get_legend_handles_labels()
    axis_legend = ax.get_legend()
    if axis_legend is not None:
        axis_legend.remove()
    fig.legend(
        handles,
        labels,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.01),
        frameon=True,
        fontsize=12,
    )


def make_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return the event-level, daily cumulative, and monthly datasets."""
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

    start_date = citations["date_added"].min().to_period("M").start_time
    daily_index = pd.date_range(start_date, REFERENCE_DATE, freq="D")
    daily_counts = citations.groupby("date_added").size().reindex(daily_index, fill_value=0)
    cumulative = daily_counts.cumsum().rename("cumulative_citations").reset_index()
    cumulative = cumulative.rename(columns={"index": "date"})

    month_index = pd.period_range(
        citations["date_added"].min().to_period("M"),
        REFERENCE_DATE.to_period("M"),
        freq="M",
    )
    monthly_counts = (
        citations.assign(month=citations["date_added"].dt.to_period("M"))
        .groupby("month")
        .size()
        .reindex(month_index, fill_value=0)
        .rename("citations")
        .reset_index()
        .rename(columns={"index": "month"})
    )
    monthly_counts["month_label"] = monthly_counts["month"].dt.strftime("%b %Y")

    return citations, cumulative, monthly_counts


def plot_cumulative(cumulative: pd.DataFrame) -> None:
    """Save the daily cumulative citation count."""
    fig, ax = plt.subplots(figsize=(11, 6.5))
    sns.lineplot(
        data=cumulative,
        x="date",
        y="cumulative_citations",
        color=TEAL,
        linewidth=3,
        drawstyle="steps-post",
        label="Cumulative citations",
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
    ax.set_ylim(0, len(DAYS_AGO) + 3)
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    style_axis(
        ax,
        "Cumulative citations over time",
        "Google Scholar date added",
        "Cumulative number of citations",
    )
    fig.autofmt_xdate(rotation=35, ha="right")
    fig.tight_layout(rect=(0, 0.16, 1, 1))
    add_legend_below(fig, ax)
    fig.savefig(OUTPUT_DIR / "cumulative_citations.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_monthly(monthly: pd.DataFrame) -> None:
    """Save the monthly citation bar chart."""
    fig, ax = plt.subplots(figsize=(11, 6.5))
    bars = sns.barplot(
        data=monthly,
        x="month_label",
        y="citations",
        color=ORANGE,
        label="Citations per month",
        ax=ax,
    )
    for container in bars.containers:
        bars.bar_label(container, fontsize=12, padding=4)
    ax.set_ylim(0, monthly["citations"].max() + 2)
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    style_axis(
        ax,
        "Citations added per month",
        "Month",
        "Number of citations",
    )
    ax.tick_params(axis="x", rotation=35)
    for label in ax.get_xticklabels():
        label.set_horizontalalignment("right")
    fig.tight_layout(rect=(0, 0.16, 1, 1))
    add_legend_below(fig, ax)
    fig.savefig(OUTPUT_DIR / "citations_per_month.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(context="notebook")
    sns.set_style("white")

    citations, cumulative, monthly = make_data()
    citations.to_csv(OUTPUT_DIR / "citation_dates.csv", index=False)
    monthly[["month_label", "citations"]].to_csv(
        OUTPUT_DIR / "citations_per_month.csv", index=False
    )
    plot_cumulative(cumulative)
    plot_monthly(monthly)

    print(f"Created {len(citations)} citation records.")
    print(monthly[["month_label", "citations"]].to_string(index=False))


if __name__ == "__main__":
    main()
