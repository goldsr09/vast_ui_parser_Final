import json
import pandas as pd

# The JSON you provided
data = {
  "columns": [
    "publisher_id",
    "tag_id",
    "tag_name",
    "date_key",
    "total_pod_based_ad_requests",
    "total_pod_unfilled_ad_requests",
    "total_num_unfiltered_ad_requests",
    "total_num_unfiltered_impressions",
    "fill_rate",
    "impression_rate"
  ],
  "data": [
    [
      "100",
      "abc123def456ghi789jk",
      "Example_Inventory Split_VOD",
      "2025-06-30",
      2472041,
      2450103,
      618053,
      76219,
      0.9,
      12.3
    ],
    [
      "100",
      "abc123def456ghi789jk",
      "Example_Inventory Split_VOD",
      "2025-06-29",
      2025580,
      1999808,
      506523,
      93633,
      1.3,
      18.5
    ],
    [
      "100",
      "abc123def456ghi789jk",
      "Example_Inventory Split_VOD",
      "2025-06-28",
      2321762,
      2288663,
      581731,
      124180,
      1.4,
      21.3
    ],
    [
      "100",
      "abc123def456ghi789jk",
      "Example_Inventory Split_VOD",
      "2025-06-27",
      1559480,
      1452779,
      454896,
      114304,
      6.8,
      25.1
    ],
    [
      "100",
      "abc123def456ghi789jk",
      "Example_Inventory Split_VOD",
      "2025-06-26",
      273145,
      0,
      273145,
      85697,
      100,
      31.4
    ],
    [
      "100",
      "abc123def456ghi789jk",
      "Example_Inventory Split_VOD",
      "2025-06-25",
      290583,
      0,
      290583,
      107980,
      100,
      37.2
    ],
    [
      "100",
      "abc123def456ghi789jk",
      "Example_Inventory Split_VOD",
      "2025-06-24",
      321361,
      0,
      321362,
      141834,
      100,
      44.1
    ],
    [
      "100",
      "abc123def456ghi789jk",
      "Example_Inventory Split_VOD",
      "2025-06-23",
      334160,
      0,
      334161,
      41415,
      100,
      12.4
    ],
    [
      "100",
      "abc123def456ghi789jk",
      "Example_Inventory Split_VOD",
      "2025-06-22",
      359221,
      0,
      359227,
      43357,
      100,
      12.1
    ],
    [
      "100",
      "abc123def456ghi789jk",
      "Example_Inventory Split_VOD",
      "2025-06-21",
      379316,
      0,
      379316,
      77720,
      100,
      20.5
    ],
    [
      "100",
      "abc123def456ghi789jk",
      "Example_Inventory Split_VOD",
      "2025-06-20",
      246320,
      0,
      246320,
      76543,
      100,
      31.1
    ],
    [
      "100",
      "abc123def456ghi789jk",
      "Example_Inventory Split_VOD",
      "2025-06-19",
      111040,
      0,
      111042,
      17864,
      100,
      16.1
    ],
    [
      "100",
      "abc123def456ghi789jk",
      "Example_Inventory Split_VOD",
      "2025-06-12",
      705093,
      701336,
      355019,
      12585,
      0.5,
      3.5
    ],
    [
      "100",
      "abc123def456ghi789jk",
      "Example_Inventory Split_VOD",
      "2025-06-11",
      743239,
      723828,
      371646,
      64669,
      2.6,
      17.4
    ],
    [
      "100",
      "abc123def456ghi789jk",
      "Example_Inventory Split_VOD",
      "2025-06-10",
      777820,
      777501,
      388910,
      1014,
      0,
      0.3
    ],
    [
      "100",
      "abc123def456ghi789jk",
      "Example_Inventory Split_VOD",
      "2025-06-09",
      753806,
      753634,
      376903,
      537,
      0,
      0.1
    ],
    [
      "100",
      "abc123def456ghi789jk",
      "Example_Inventory Split_VOD",
      "2025-06-08",
      770558,
      770357,
      385279,
      583,
      0,
      0.2
    ],
    [
      "100",
      "abc123def456ghi789jk",
      "Example_Inventory Split_VOD",
      "2025-06-07",
      828254,
      828061,
      414127,
      560,
      0,
      0.1
    ],
    [
      "100",
      "abc123def456ghi789jk",
      "Example_Inventory Split_VOD",
      "2025-06-06",
      720922,
      720765,
      360461,
      491,
      0,
      0.1
    ],
    [
      "100",
      "abc123def456ghi789jk",
      "Example_Inventory Split_VOD",
      "2025-06-05",
      795314,
      795136,
      397657,
      484,
      0,
      0.1
    ],
    [
      "100",
      "abc123def456ghi789jk",
      "Example_Inventory Split_VOD",
      "2025-06-04",
      774670,
      774522,
      387335,
      434,
      0,
      0.1
    ],
    [
      "100",
      "abc123def456ghi789jk",
      "Example_Inventory Split_VOD",
      "2025-06-03",
      772188,
      771992,
      386094,
      499,
      0,
      0.1
    ],
    [
      "100",
      "abc123def456ghi789jk",
      "Example_Inventory Split_VOD",
      "2025-06-02",
      709170,
      708984,
      354585,
      485,
      0,
      0.1
    ],
    [
      "100",
      "abc123def456ghi789jk",
      "Example_Inventory Split_VOD",
      "2025-06-01",
      702852,
      702653,
      351426,
      566,
      0,
      0.2
    ],
    [
      "100",
      "lmn012opq345rst678uv",
      "Example_Inventory Split_LIVE",
      "2025-06-30",
      1438401,
      1407573,
      443729,
      22786,
      2.1,
      5.1
    ],
    [
      "100",
      "lmn012opq345rst678uv",
      "Example_Inventory Split_LIVE",
      "2025-06-29",
      1222337,
      1194364,
      390748,
      24046,
      2.3,
      6.2
    ],
    [
      "100",
      "lmn012opq345rst678uv",
      "Example_Inventory Split_LIVE",
      "2025-06-28",
      866467,
      842315,
      276490,
      24889,
      2.8,
      9
    ],
    [
      "100",
      "lmn012opq345rst678uv",
      "Example_Inventory Split_LIVE",
      "2025-06-27",
      976713,
      949788,
      287803,
      34969,
      2.8,
      12.2
    ],
    [
      "100",
      "lmn012opq345rst678uv",
      "Example_Inventory Split_LIVE",
      "2025-06-26",
      689830,
      670856,
      211771,
      28004,
      2.8,
      13.2
    ],
    [
      "100",
      "lmn012opq345rst678uv",
      "Example_Inventory Split_LIVE",
      "2025-06-25",
      598237,
      541690,
      189702,
      26446,
      9.5,
      13.9
    ],
    [
      "100",
      "lmn012opq345rst678uv",
      "Example_Inventory Split_LIVE",
      "2025-06-24",
      700639,
      649145,
      211510,
      52467,
      7.3,
      24.8
    ],
    [
      "100",
      "lmn012opq345rst678uv",
      "Example_Inventory Split_LIVE",
      "2025-06-23",
      736840,
      732498,
      219696,
      6664,
      0.6,
      3
    ],
    [
      "100",
      "lmn012opq345rst678uv",
      "Example_Inventory Split_LIVE",
      "2025-06-22",
      1334004,
      2007296,
      207033,
      1772,
      -50.5,
      0.9
    ],
    [
      "100",
      "lmn012opq345rst678uv",
      "Example_Inventory Split_LIVE",
      "2025-06-21",
      477330,
      468898,
      143738,
      5753,
      1.8,
      4
    ],
    [
      "100",
      "lmn012opq345rst678uv",
      "Example_Inventory Split_LIVE",
      "2025-06-20",
      431977,
      421842,
      126375,
      3664,
      2.3,
      2.9
    ],
    [
      "100",
      "lmn012opq345rst678uv",
      "Example_Inventory Split_LIVE",
      "2025-06-19",
      165468,
      163417,
      47868,
      1329,
      1.2,
      2.8
    ],
    [
      "100",
      "lmn012opq345rst678uv",
      "Example_Inventory Split_LIVE",
      "2025-06-11",
      338068,
      337911,
      245091,
      26,
      0,
      0
    ],
    [
      "100",
      "lmn012opq345rst678uv",
      "Example_Inventory Split_LIVE",
      "2025-06-10",
      365914,
      365826,
      182957,
      75,
      0,
      0
    ],
    [
      "100",
      "lmn012opq345rst678uv",
      "Example_Inventory Split_LIVE",
      "2025-06-09",
      399959,
      399834,
      199979,
      105,
      0,
      0.1
    ],
    [
      "100",
      "lmn012opq345rst678uv",
      "Example_Inventory Split_LIVE",
      "2025-06-08",
      414916,
      414806,
      207458,
      101,
      0,
      0
    ],
    [
      "100",
      "lmn012opq345rst678uv",
      "Example_Inventory Split_LIVE",
      "2025-06-07",
      275082,
      274989,
      137541,
      72,
      0,
      0.1
    ],
    [
      "100",
      "lmn012opq345rst678uv",
      "Example_Inventory Split_LIVE",
      "2025-06-06",
      317092,
      317008,
      158546,
      70,
      0,
      0
    ],
    [
      "100",
      "lmn012opq345rst678uv",
      "Example_Inventory Split_LIVE",
      "2025-06-05",
      350646,
      350525,
      175323,
      114,
      0,
      0.1
    ],
    [
      "100",
      "lmn012opq345rst678uv",
      "Example_Inventory Split_LIVE",
      "2025-06-04",
      300668,
      300587,
      150334,
      72,
      0,
      0
    ],
    [
      "100",
      "lmn012opq345rst678uv",
      "Example_Inventory Split_LIVE",
      "2025-06-03",
      383362,
      383255,
      191681,
      99,
      0,
      0.1
    ],
    [
      "100",
      "lmn012opq345rst678uv",
      "Example_Inventory Split_LIVE",
      "2025-06-02",
      332554,
      332472,
      166277,
      73,
      0,
      0
    ],
    [
      "100",
      "lmn012opq345rst678uv",
      "Example_Inventory Split_LIVE",
      "2025-06-01",
      434472,
      434363,
      217236,
      102,
      0,
      0
    ]
  ]
}# paste your JSON here

def flatten_cache_entries(data):
    """
    Flattens the cache entries from the JSON data into a list of dictionaries.
    """
    flat_rows = []
    for entry in data['cache_entries']:
        cache_key = entry['cache_key']
        row_count = entry['row_count']
        query_type = entry['query_type']
        created_at = entry['created_at']
        updated_at = entry['updated_at']
        date_range_min = entry['date_range']['min']
        date_range_max = entry['date_range']['max']
        sample_row = entry['sample_row']

        # Flatten each entry into a dictionary
        flat_rows.append({
            "cache_key": cache_key,
            "row_count": row_count,
            "query_type": query_type,
            "created_at": created_at,
            "updated_at": updated_at,
            "date_range_min": date_range_min,
            "date_range_max": date_range_max,
            "sample_row": sample_row
        })
    return flat_rows

def export_to_csv(flat_rows, filename="flattened_cache_entries.csv"):
    """
    Exports the flattened rows to a CSV file.
    """
    df = pd.DataFrame(flat_rows)
    df.to_csv(filename, index=False)
    prindt(f"Exported {len(df)} rows to {filename}")

# --- Usage ---
flat_rows = flatten_cache_entries(data)
export_to_csv(flat_rows, "flattened_cache_entries.csv")