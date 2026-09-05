import code

import polars as pl

codebook = {
    "Mode": {
        "AR": "Alaska Railroad",
        "CC": "Cable Car",
        "CR": "Commuter Rail",
        "HR": "Heavy Rail",
        "YR": "Hybrid Rail",
        "IP": "Inclined Plane",
        "LR": "Light Rail",
        "MG": "Monorail/Automated Guideway",
        "SR": "Streetcar Rail",
        "TR": "Aerial Tramway",
        "CB": "Commuter Bus",
        "MB": "Bus",
        "RB": "Bus Rapid Transit",
        "DR": "Demand Response",
        "FB": "Ferryboat",
        "JT": "Jitney",
        "PB": "Público",
        "TB": "Trolleybus",
        "VP": "Vanpool",
    }
}


def main() -> None:
    print("Hello from transit-stats!")

    df_raw = pl.read_csv(
        "data/ntd-july-2026.csv", schema_overrides={"UACE CD": pl.String}
    )

    df_long = df_raw.unpivot(
        index=[
            "NTD ID",
            "Legacy NTD ID",
            "Agency",
            "Mode/Type of Service Status",
            "Reporter Type",
            "UACE CD",
            "UZA Name",
            "Mode",
            "TOS",
            "3 Mode",
        ],
        variable_name="Month/Year",
        value_name="utp_count",
    )

    df_long = (
        df_long.with_columns(
            pl.col("Month/Year")
            .str.splitn("/", 2)
            .struct.rename_fields(["month", "year"])
        )
        .unnest("Month/Year")
        .select(["NTD ID", "Agency", "UZA Name", "Mode", "year", "month", "utp_count"])
    ).with_columns(pl.col("Mode").replace(codebook["Mode"]).alias("Mode"))

    df_month_sum = df_long.group_by(
        ["NTD ID", "Agency", "UZA Name", "Mode", "year", "month"]
    ).agg(pl.col("utp_count").sum())

    df_year = (
        df_month_sum.group_by(["NTD ID", "Agency", "UZA Name", "Mode", "year"])
        .agg(pl.col("utp_count").sum())
        .sort(["year", "utp_count"], descending=True)
    )

    df_urban_rail = (
        df_year.filter(
            pl.col("Mode").is_in(
                ["Heavy Rail", "Light Rail", "Streetcar Rail", "Cable Car"]
            )
        )
        .group_by(["NTD ID", "Agency", "year"])
        .agg(pl.col("utp_count").sum())
        .sort(["year", "utp_count"], descending=True)
        .filter(pl.col("year") == "2025")
    ).top_k(11, by="utp_count")

    with pl.Config(tbl_rows=-1):
        print(df_urban_rail)


if __name__ == "__main__":
    main()
