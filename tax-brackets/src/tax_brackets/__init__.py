from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np

CURRENT_YEAR = "2025"


def calculate_generic_tax(income_array, brackets):
    """Calculates total tax liability for an arbitrary number of brackets."""
    tax = np.zeros_like(income_array, dtype=float)

    for i in range(len(brackets)):
        lower_bound, rate = brackets[i]
        upper_bound = brackets[i + 1][0] if i < len(brackets) - 1 else np.inf

        taxable_in_bracket = np.maximum(
            0, np.minimum(income_array, upper_bound) - lower_bound
        )
        tax += taxable_in_bracket * rate

    return tax


def calculate_effective_rate(income_array, brackets):
    """
    Calculates the effective tax rate (Total Tax / Total Income) as a percentage.
    """
    total_tax = calculate_generic_tax(income_array, brackets)
    # Divide by income and multiply by 100 to get a percentage
    return (total_tax / income_array) * 100


def calculate_marginal_rate(income_array, brackets):
    """
    Determines the current marginal tax rate (the bracket tier) for each income.
    """
    marginal_rates = np.zeros_like(income_array, dtype=float)

    for lower_bound, rate in brackets:
        # For every income greater than or equal to the bracket's lower bound,
        # update the marginal rate. Because the brackets list is sorted ascending,
        # higher brackets will naturally overwrite lower ones as the loop progresses.
        mask = income_array >= lower_bound
        marginal_rates[mask] = rate * 100

    return marginal_rates


def get_cpi_adjustment(amount: float, original_cpi: float, target_cpi: float) -> float:
    if original_cpi == 0:
        raise ValueError("Original CPI cannot be zero.")

    return (amount * target_cpi) / original_cpi


def main() -> None:
    print("Hello from tax-brackets!")

    # Load Consumer Price Index data
    cpi_u = {
        (y := x.split(","))[0]: float(y[1])
        for x in Path("cpi-u.csv").read_text().splitlines()[1:]
    }

    # Load tax bracket data
    raw_tax_brackets = [
        x.split(",")
        for x in Path("historical_income_tax.csv").read_text().splitlines()[1:]
    ]

    # Convert raw bracket data to dictionaries
    brackets: defaultdict[tuple[str, str], list[tuple[float, float]]] = defaultdict(
        list
    )

    max_cut_point = 0
    for raw_bracket in raw_tax_brackets:
        year, status, rate, cut_point = raw_bracket

        # adjust cut-point for inflation
        adjusted_cut_point = get_cpi_adjustment(
            float(cut_point), cpi_u[year], cpi_u[CURRENT_YEAR]
        )

        # Keep track of maximum inflation adjusted cut point seen
        max_cut_point = max(max_cut_point, adjusted_cut_point)

        brackets[(year, status)].append((adjusted_cut_point, float(rate)))

    # Break out filing statuses into seperate dictionaries
    single_brackets = {key: brackets[key] for key in brackets if key[1] == "S"}
    mfj_brackets = {key: brackets[key] for key in brackets if key[1] == "MFJ"}
    mfs_brackets = {key: brackets[key] for key in brackets if key[1] == "MFS"}
    hoh_brackets = {key: brackets[key] for key in brackets if key[1] == "HOH"}

    # Start at $1 to avoid dividing by zero
    incomes = np.linspace(1, 1_000_000, 2000)

    # calculate tax rates
    lines_data = {}
    for (year, status), year_brackets in single_brackets.items():
        # effective_rates = calculate_effective_rate(incomes, year_brackets)
        marginal_rates = calculate_marginal_rate(incomes, year_brackets)

        lines_data[int(year)] = (incomes, marginal_rates)

    # Setup figure
    fig, ax = plt.subplots(figsize=(12, 7))

    # Setup color map and normalizer for the year value.
    cmap = plt.get_cmap("plasma")
    norm = plt.Normalize(min(lines_data.keys()), max(lines_data.keys()))

    # plot each year
    for year, (x, y) in lines_data.items():
        line_color = cmap(norm(year))
        ax.plot(x, y, color=line_color, linewidth=1)

    # Chart Formatting

    # add the color bar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    fig.colorbar(sm, ax=ax, label="Year")

    plt.title(
        "Marginal Tax Rates",
        fontsize=16,
        fontweight="bold",
    )
    plt.xlabel("Taxable Income ($), 2025 dollars", fontsize=12)
    plt.ylabel("Tax Rate (%)", fontsize=12)

    # Add commas to the X-axis numbers
    plt.gca().xaxis.set_major_formatter(
        matplotlib.ticker.StrMethodFormatter("{x:,.0f}")
    )

    plt.grid(True, linestyle=":", alpha=0.7)
    plt.tight_layout()

    plt.show()


if __name__ == "__main__":
    main()
