import geopandas as gdf
import pandas as pd
from sqlalchemy import create_engine

DB_URL = "postgresql://david@localhost:5432/geo"


def get_census_tracts():
    engine = create_engine(DB_URL)
    with engine.connect() as con:
        tracts = gdf.GeoDataFrame.from_postgis("SELECT * FROM tl_2020.tract", con)

    # filter out OCONUS
    # conus_tracts = tracts[
    #    ~tracts["statefp"].isin(("02", "15", "60", "66", "69", "72", "78"))
    # ]
    return tracts


def main():
    print("Hello from language-maps!")

    data = pd.read_csv("data/ACSDT5Y2024.B16002-Data.csv", skiprows=[0])

    columns = {
        "Geography": "Geography",
        "Geographic Area Name": "Geographic Area Name",
        "Estimate!!Total:": "total",
        "Estimate!!Total:!!English only": "english",
        "Estimate!!Total:!!Spanish:": "spanish",
        "Estimate!!Total:!!French, Haitian, or Cajun:": "french",
        "Estimate!!Total:!!German or other West Germanic languages:": "german",
        "Estimate!!Total:!!Russian, Polish, or other Slavic languages:": "slavic",
        "Estimate!!Total:!!Other Indo-European languages:": "other_indoeuropean",
        "Estimate!!Total:!!Korean:": "korean",
        "Estimate!!Total:!!Chinese (incl. Mandarin, Cantonese):": "chinese",
        "Estimate!!Total:!!Vietnamese:": "vietnamese",
        "Estimate!!Total:!!Tagalog (incl. Filipino):": "tagalog",
        "Estimate!!Total:!!Other Asian and Pacific Island languages:": "other_asian_pi",
        "Estimate!!Total:!!Arabic:": "arabic",
        "Estimate!!Total:!!Other and unspecified languages:": "other",
    }
    data = data[columns.keys()].rename(columns=columns)

    data["english_pct"] = (data["english"] / data["total"]).fillna(0)
    data["spanish_pct"] = (data["spanish"] / data["total"]).fillna(0)
    data["french_pct"] = (data["french"] / data["total"]).fillna(0)
    data["german_pct"] = (data["german"] / data["total"]).fillna(0)
    data["slavic_pct"] = (data["slavic"] / data["total"]).fillna(0)
    data["other_indoeuropean_pct"] = (
        data["other_indoeuropean"] / data["total"]
    ).fillna(0)
    data["korean_pct"] = (data["korean"] / data["total"]).fillna(0)
    data["chinese_pct"] = (data["chinese"] / data["total"]).fillna(0)
    data["vietnamese_pct"] = (data["vietnamese"] / data["total"]).fillna(0)
    data["tagalog_pct"] = (data["tagalog"] / data["total"]).fillna(0)
    data["other_asian_pi_pct"] = (data["other_asian_pi"] / data["total"]).fillna(0)
    data["arabic_pct"] = (data["arabic"] / data["total"]).fillna(0)
    data["other_pct"] = (data["other"] / data["total"]).fillna(0)

    data["tractce"] = data["Geography"].str[9:]

    data = data.sort_values("Geography")
    print(data[data["total"] == 0])
    data.to_csv("data/language_data.csv")


if __name__ == "__main__":
    main()
