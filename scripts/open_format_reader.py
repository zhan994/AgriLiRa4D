#!/usr/bin/env python3
"""Minimal ROS-independent reader for the AgriLiRa4D open format."""

import argparse
import csv
import json
import sys
from pathlib import Path


def read_pcd_header(path):
    """Read and validate an ASCII PCD header."""
    header = {}
    with Path(path).open("r", encoding="ascii") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            key, *values = line.split()
            header[key.upper()] = values
            if key.upper() == "DATA":
                break
    if header.get("DATA") != ["ascii"]:
        raise ValueError("Expected an ASCII PCD file: {}".format(path))
    if "FIELDS" not in header or "POINTS" not in header:
        raise ValueError("Incomplete PCD header: {}".format(path))
    return header


def iter_pcd_points(path):
    """Yield each ASCII PCD point as a field-name dictionary of floats/ints."""
    header = read_pcd_header(path)
    fields = header["FIELDS"]
    types = header["TYPE"]
    sizes = header["SIZE"]
    converters = [int if kind in ("I", "U") else float for kind in types]
    expected = int(header["POINTS"][0])
    count = 0
    in_data = False
    with Path(path).open("r", encoding="ascii") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not in_data:
                if line.lower() == "data ascii":
                    in_data = True
                continue
            if not line:
                continue
            values = line.split()
            if len(values) != len(fields):
                raise ValueError("Unexpected field count in {}".format(path))
            point = {}
            for name, value, convert, size in zip(fields, values, converters, sizes):
                point[name] = convert(value)
            count += 1
            yield point
    if count != expected:
        raise ValueError(
            "PCD header declares {} points but {} were read from {}".format(
                expected, count, path
            )
        )


def iter_csv_rows(path):
    """Yield CSV rows as dictionaries while preserving the documented names."""
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        yield from csv.DictReader(handle)


def first_or_none(values):
    return next(iter(values), None)


def inspect_sequence(sequence_dir):
    sequence_dir = Path(sequence_dir)
    with (sequence_dir / "metadata.json").open("r", encoding="utf-8") as handle:
        metadata = json.load(handle)
    print("Sequence:", metadata["sequence"])
    print("Message counts:", json.dumps(metadata["message_counts"], sort_keys=True))

    for sensor in ("lidar", "radar"):
        frame = first_or_none(iter_csv_rows(sequence_dir / (sensor + "_frames.csv")))
        if frame is not None:
            cloud_path = sequence_dir / frame["file"]
            print("First {} frame: {}".format(sensor, cloud_path))
            print("First {} point: {}".format(sensor, first_or_none(iter_pcd_points(cloud_path))))

    imu = first_or_none(iter_csv_rows(sequence_dir / "imu.csv"))
    print("First IMU row:", imu)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Inspect an AgriLiRa4D ASCII PCD/CSV sequence without ROS."
    )
    parser.add_argument("sequence_dir", type=Path)
    args = parser.parse_args(argv)
    try:
        inspect_sequence(args.sequence_dir)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print("error: {}".format(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
