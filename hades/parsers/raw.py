import pandas as pd
from pathlib import Path


def parse_raw(results: Path) -> pd.DataFrame:
    data = dict()
    with open(results, "r") as f:
        for line in f.readlines():
            match line.split():
                case "Index", *k:
                    if "headers" not in locals():
                        headers = line.split()
                case [ind, *k] if "headers" in locals() and len(k) == len(headers) - 1:
                    for head, val in zip(headers, k):
                        if head not in data.keys():
                            data[head] = [
                                float(val),
                            ]
                        else:
                            data[head].append(float(val))
    df = pd.DataFrame(data=data, dtype=float)
    return df
