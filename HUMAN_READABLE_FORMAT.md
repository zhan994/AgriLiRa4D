# Human-readable release format

AgriLiRa4D is distributed in two equivalent representations:

1. ROS 1 bag files preserve the original messages for direct playback.
2. The open-format release provides point clouds as ASCII PCD and time-series
   measurements as UTF-8 CSV, without requiring ROS or proprietary software.

The two representations contain the same measurements. Calibration YAML files
and TUM-format ground-truth trajectories are already plain text and are shared by
both representations.

## Directory layout

Each sequence has the following layout after conversion:

```text
NJFlatB01/
├── README.md
├── metadata.json
├── lidar_frames.csv
├── radar_frames.csv
├── imu.csv
├── fins_rtk_pose_enu.csv
├── fins_rtk_pose_flu.csv
├── fins_rtk_llh.csv
├── lidar/
│   ├── <timestamp>.pcd
│   └── ...
└── radar/
    ├── <timestamp>.pcd
    └── ...
```

LiDAR and radar filenames use the original ROS header timestamp. Their ordered
frame tables provide explicit indices and retain both header and bag timestamps.

| ROS topic | Open-format output |
| --- | --- |
| `/rslidar_points` | `lidar/<timestamp>.pcd` and `lidar_frames.csv` |
| `/radar_points` | `radar/<timestamp>.pcd` and `radar_frames.csv` |
| `/rslidar_imu_data` | `imu.csv` |
| `/aircraft_pose_enu` | `fins_rtk_pose_enu.csv` |
| `/aircraft_pose_flu` | `fins_rtk_pose_flu.csv` |
| `/aircraft_position_llh` | `fins_rtk_llh.csv` |

## Conversion

The converter requires ROS 1 and uses only the standard `rosbag` and
`sensor_msgs` Python packages:

```bash
source /opt/ros/noetic/setup.bash
python3 scripts/rosbag_extract.py /path/to/NJFlatB01.bag \
  --output /path/to/open_format
```

An entire download directory can be converted in one invocation:

```bash
python3 scripts/rosbag_extract.py /path/to/all_bags \
  --output /path/to/open_format
```

The exporter never overwrites an existing sequence directory. It writes to a
temporary `.incomplete` directory and publishes the sequence only after all
messages have been converted successfully.

The open-format reader has no ROS or third-party dependency. The following
command validates the PCD headers and point counts and prints representative
LiDAR, radar, and IMU records:

```bash
python3 scripts/open_format_reader.py /path/to/open_format/NJFlatB01
```

## Conventions

- Point clouds follow PCD version 0.7 with `DATA ascii`; one file represents one
  LiDAR or radar frame.
- All tabular files are RFC 4180-style UTF-8 CSV with one header row.
- All timestamps are Unix time in seconds with nanosecond precision.
- Point-cloud coordinates and poses use metres.
- Angular velocity uses radians per second and acceleration uses metres per
  second squared.
- Orientations are Hamilton quaternions in `(x, y, z, w)` order.
- Covariances are flattened in row-major order and retain the ROS message values.
- `timestamp` is the ROS message header time; `bag_timestamp` is the bag record
  time. LiDAR's per-point `timestamp` field is retained unchanged in seconds.
- GNSS latitude and longitude use WGS84 degrees; altitude uses metres.
- The acquisition retained only FINS-RTK latitude, longitude, and altitude; no
  GNSS status, service, or covariance measurements are included.
- Frame identifiers and all measurement values are copied without coordinate
  conversion or interpolation.

Each point-cloud frame index records both timestamps, frame ID, point count, and
relative PCD filename. `metadata.json` records the format version and message
counts, making completeness checks possible without ROS.
