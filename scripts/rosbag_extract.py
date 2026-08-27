#!/usr/bin/env python3
"""Export AgriLiRa4D ROS 1 bags to human-readable ASCII PCD and CSV files."""

import argparse
import csv
import json
import shutil
import sys
from collections import Counter
from pathlib import Path


TOPICS = {
    "/rslidar_points": "lidar",
    "/radar_points": "radar",
    "/rslidar_imu_data": "imu",
    "/aircraft_pose_enu": "pose_enu",
    "/aircraft_pose_flu": "pose_flu",
    "/aircraft_position_llh": "gnss",
}

POINT_FIELDS = {
    "lidar": ("x", "y", "z", "intensity", "ring", "timestamp"),
    "radar": ("x", "y", "z", "v_doppler_mps", "snr_db", "rcs"),
}

PCD_SCHEMA = {
    "lidar": {
        "fields": "x y z intensity ring timestamp",
        "size": "4 4 4 4 2 8",
        "type": "F F F F U F",
        "count": "1 1 1 1 1 1",
    },
    "radar": {
        "fields": "x y z v_doppler_mps snr_db rcs",
        "size": "4 4 4 4 4 4",
        "type": "F F F F F F",
        "count": "1 1 1 1 1 1",
    },
}

IMU_HEADER = (
    "timestamp", "bag_timestamp", "frame_id",
    "orientation_x", "orientation_y", "orientation_z", "orientation_w",
    "orientation_covariance_00", "orientation_covariance_01", "orientation_covariance_02",
    "orientation_covariance_10", "orientation_covariance_11", "orientation_covariance_12",
    "orientation_covariance_20", "orientation_covariance_21", "orientation_covariance_22",
    "angular_velocity_x", "angular_velocity_y", "angular_velocity_z",
    "angular_velocity_covariance_00", "angular_velocity_covariance_01", "angular_velocity_covariance_02",
    "angular_velocity_covariance_10", "angular_velocity_covariance_11", "angular_velocity_covariance_12",
    "angular_velocity_covariance_20", "angular_velocity_covariance_21", "angular_velocity_covariance_22",
    "linear_acceleration_x", "linear_acceleration_y", "linear_acceleration_z",
    "linear_acceleration_covariance_00", "linear_acceleration_covariance_01", "linear_acceleration_covariance_02",
    "linear_acceleration_covariance_10", "linear_acceleration_covariance_11", "linear_acceleration_covariance_12",
    "linear_acceleration_covariance_20", "linear_acceleration_covariance_21", "linear_acceleration_covariance_22",
)

POSE_HEADER = (
    "timestamp", "bag_timestamp", "frame_id",
    "position_x", "position_y", "position_z",
    "orientation_x", "orientation_y", "orientation_z", "orientation_w",
)

GNSS_HEADER = (
    "timestamp", "bag_timestamp", "frame_id",
    "latitude", "longitude", "altitude",
)

FRAME_HEADER = (
    "frame_index", "timestamp", "bag_timestamp", "frame_id", "point_count", "file",
)


def timestamp_text(stamp):
    """Return an exact ROS timestamp without converting through a float."""
    secs = getattr(stamp, "secs", getattr(stamp, "sec", None))
    nsecs = getattr(stamp, "nsecs", getattr(stamp, "nanosec", None))
    if secs is None or nsecs is None:
        return "{:.9f}".format(stamp.to_sec())
    return "{}.{:09d}".format(secs, nsecs)


def vector3(value):
    return (value.x, value.y, value.z)


def quaternion(value):
    return (value.x, value.y, value.z, value.w)


class Table:
    def __init__(self, path, header):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = path.open("w", newline="", encoding="utf-8")
        self.writer = csv.writer(self.handle, lineterminator="\n")
        self.writer.writerow(header)

    def row(self, values):
        self.writer.writerow(values)

    def close(self):
        self.handle.close()


def imu_row(msg, bag_stamp):
    return (
        timestamp_text(msg.header.stamp), timestamp_text(bag_stamp), msg.header.frame_id,
        *quaternion(msg.orientation), *msg.orientation_covariance,
        *vector3(msg.angular_velocity), *msg.angular_velocity_covariance,
        *vector3(msg.linear_acceleration), *msg.linear_acceleration_covariance,
    )


def pose_row(msg, bag_stamp):
    return (
        timestamp_text(msg.header.stamp), timestamp_text(bag_stamp), msg.header.frame_id,
        *vector3(msg.pose.position), *quaternion(msg.pose.orientation),
    )


def gnss_row(msg, bag_stamp):
    return (
        timestamp_text(msg.header.stamp), timestamp_text(bag_stamp), msg.header.frame_id,
        msg.latitude, msg.longitude, msg.altitude,
    )


def pcd_header(sensor, width, height):
    schema = PCD_SCHEMA[sensor]
    point_count = width * height
    return """# .PCD v0.7 - Point Cloud Data file format
VERSION 0.7
FIELDS {fields}
SIZE {size}
TYPE {type}
COUNT {count}
WIDTH {width}
HEIGHT {height}
VIEWPOINT 0 0 0 1 0 0 0
POINTS {point_count}
DATA ascii
""".format(width=width, height=height, point_count=point_count, **schema)


def export_cloud(msg, bag_stamp, sensor, frame_index, root, read_points):
    fields = POINT_FIELDS[sensor]
    stamp = timestamp_text(msg.header.stamp)
    relative = Path(sensor) / ("{}.pcd".format(stamp))
    output = root / relative
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise ValueError(
            "Duplicate {} header timestamp {}; cannot create unique PCD filename".format(
                sensor, stamp
            )
        )
    expected_count = msg.width * msg.height
    count = 0
    with output.open("w", encoding="ascii", newline="\n") as handle:
        handle.write(pcd_header(sensor, msg.width, msg.height))
        for point in read_points(msg, field_names=fields, skip_nans=False):
            handle.write(" ".join(str(value) for value in point))
            handle.write("\n")
            count += 1
    if count != expected_count:
        raise ValueError(
            "Point count mismatch for {} frame {}: expected {}, wrote {}".format(
                sensor, stamp, expected_count, count
            )
        )
    return (
        frame_index, stamp, timestamp_text(bag_stamp), msg.header.frame_id, count,
        relative.as_posix(),
    )


def write_format_readme(root):
    text = """# AgriLiRa4D open-format sequence

This directory is a measurement-level export of one ROS 1 bag. All timestamps
are Unix time in seconds with nine decimal places. Quaternions use `(x,y,z,w)`.

| Path | Contents |
| --- | --- |
| `lidar/` | One scan per timestamp-indexed ASCII PCD; `x,y,z` [m], `intensity`, `ring`, per-point `timestamp` [s] |
| `radar/` | One scan per timestamp-indexed ASCII PCD; `x,y,z` [m], Doppler velocity [m/s], SNR [dB], RCS [m^2] |
| `lidar_frames.csv`, `radar_frames.csv` | Ordered frame index, header/bag timestamps, frame, point count and relative file |
| `imu.csv` | Orientation, angular velocity [rad/s], linear acceleration [m/s^2], and 3x3 covariances |
| `fins_rtk_pose_enu.csv`, `fins_rtk_pose_flu.csv` | FINS-RTK position [m] and orientation quaternion in the named reference frame |
| `fins_rtk_llh.csv` | Recorded WGS84 latitude/longitude [deg] and altitude [m] |
| `metadata.json` | Format version, source name, topic counts and time range |

PCD files follow version 0.7 and use `DATA ascii`. CSV files are UTF-8 with a
header row.
"""
    (root / "README.md").write_text(text, encoding="utf-8")


def convert_bag(bag_path, output_root):
    try:
        import rosbag
        from sensor_msgs.point_cloud2 import read_points
    except ImportError as exc:
        raise RuntimeError(
            "ROS 1 Python packages are required. Source your ROS environment first "
            "(for example: source /opt/ros/noetic/setup.bash)."
        ) from exc

    sequence = bag_path.name[:-4] if bag_path.name.endswith(".bag") else bag_path.stem
    final_root = output_root / sequence
    work_root = output_root / ("." + sequence + ".incomplete")
    if final_root.exists() or work_root.exists():
        raise FileExistsError(
            "Output already exists for {} (remove or move it explicitly before retrying)".format(sequence)
        )
    output_root.mkdir(parents=True, exist_ok=True)
    work_root.mkdir()

    tables = {
        "imu": Table(work_root / "imu.csv", IMU_HEADER),
        "pose_enu": Table(work_root / "fins_rtk_pose_enu.csv", POSE_HEADER),
        "pose_flu": Table(work_root / "fins_rtk_pose_flu.csv", POSE_HEADER),
        "gnss": Table(work_root / "fins_rtk_llh.csv", GNSS_HEADER),
        "lidar_frames": Table(work_root / "lidar_frames.csv", FRAME_HEADER),
        "radar_frames": Table(work_root / "radar_frames.csv", FRAME_HEADER),
    }
    counts = Counter()
    cloud_indices = Counter()
    first_bag_stamp = None
    last_bag_stamp = None

    try:
        with rosbag.Bag(str(bag_path), "r") as bag:
            for topic, msg, bag_stamp in bag.read_messages(topics=list(TOPICS)):
                name = TOPICS[topic]
                counts[topic] += 1
                first_bag_stamp = first_bag_stamp or timestamp_text(bag_stamp)
                last_bag_stamp = timestamp_text(bag_stamp)
                if name in ("lidar", "radar"):
                    row = export_cloud(
                        msg, bag_stamp, name, cloud_indices[name], work_root,
                        read_points,
                    )
                    tables[name + "_frames"].row(row)
                    cloud_indices[name] += 1
                elif name == "imu":
                    tables[name].row(imu_row(msg, bag_stamp))
                elif name.startswith("pose_"):
                    tables[name].row(pose_row(msg, bag_stamp))
                else:
                    tables[name].row(gnss_row(msg, bag_stamp))

        metadata = {
            "format": "AgriLiRa4D open format",
            "format_version": "1.0",
            "sequence": sequence,
            "source_bag": bag_path.name,
            "point_cloud_format": "PCD 0.7 ASCII",
            "tabular_format": "CSV",
            "bag_time_start": first_bag_stamp,
            "bag_time_end": last_bag_stamp,
            "message_counts": {topic: counts[topic] for topic in TOPICS},
        }
        with (work_root / "metadata.json").open("w", encoding="utf-8") as handle:
            json.dump(metadata, handle, indent=2, sort_keys=True)
            handle.write("\n")
        write_format_readme(work_root)
    except Exception:
        shutil.rmtree(work_root)
        raise
    finally:
        for table in tables.values():
            table.close()

    work_root.rename(final_root)
    return final_root, counts


def discover_bags(inputs):
    bags = []
    for item in inputs:
        path = Path(item).expanduser()
        if path.is_dir():
            bags.extend(sorted(path.rglob("*.bag")))
        elif path.is_file():
            bags.append(path)
        else:
            raise FileNotFoundError("Input does not exist: {}".format(path))
    unique = []
    seen = set()
    for bag in bags:
        resolved = bag.resolve()
        if resolved not in seen:
            unique.append(resolved)
            seen.add(resolved)
    if not unique:
        raise FileNotFoundError("No .bag files were found")
    return unique


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Export AgriLiRa4D bags to ASCII PCD point clouds and CSV tables."
    )
    parser.add_argument(
        "inputs", nargs="+", metavar="BAG_OR_DIR",
        help="one or more ROS bag files, or directories containing .bag files",
    )
    parser.add_argument(
        "-o", "--output", required=True, type=Path,
        help="output directory; one subdirectory is created per bag",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    try:
        bags = discover_bags(args.inputs)
        for bag in bags:
            print("Exporting {} ...".format(bag), flush=True)
            output, counts = convert_bag(bag, args.output.resolve())
            print("Wrote {} ({} messages)".format(output, sum(counts.values())))
    except (OSError, RuntimeError, ValueError) as exc:
        print("error: {}".format(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
