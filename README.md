# AgriLiRa4D
**AgriLiRa4D** is a novel multi-modal dataset specifically developed for agricultural UAV SLAM research, incorporating LiDAR, 4D Radar, and IMU measurements collected using an agricultural UAV platform. Our dataset features high-precision ground truth trajectories obtained from a Fiber Optic Inertial Navigation System (FINS) module with a built-in Real-Time Kinematic (RTK) receiver (FINS\_RTK), ensuring centimeter-level position accuracy and high-fidelity orientation references. This work aims to advance the development of robust SLAM systems tailored for agricultural autonomous operations.

***Note: The dataset is currently being uploaded and will be available for download shortly!!!***

### [[Project Page](https://zhan994.github.io/AgriLiRa4D/)]  [[arXiv](https://arxiv.org/abs/2512.01753)] 


**Flat Farmland**

![](imgs/Flat_LiDAR.gif) ![](imgs/Flat_Radar.gif) 


**Hilly Farmland**

![](imgs/Hilly_LiDAR.gif) ![](imgs/Hilly_Radar.gif) 


**Terraced Farmland**

![](imgs/Terr_LiDAR.gif) ![](imgs/Terr_Radar.gif) 


## Mapping Results

| Scene                 | LiDAR                    | 4D Radar                 |
| --------------------- | ------------------------ | ------------------------ |
| **Flat Farmland**     | ![](imgs/Flat_LiDAR.png) | ![](imgs/Flat_Radar.png) |
| **Hilly Farmland**    | ![](imgs/Hilly_LiDAR.png) | ![](imgs/Hilly_Radar.png) |
| **Terraced Farmland** | ![](imgs/Terr_LiDAR.png) | <img src="imgs/Terr_Radar.png"  /> |


## Quick Start

The 33 sequences of our dataset were collected across three representative farmland terrains—flat plains, hilly regions, and mountainous terraces—located in Nanjing, China. The dataset is organized into six sequence groups based on terrain type and scanning mode (*boundary* or *coverage*), namely *NJFlatB*, *NJFlatC*, *NJHillB*, *NJHillC*, *NJTerrB*, and *NJTerrC*.

For all sequences except *NJTerrB* and *NJTerrC*, the UAV flew at a constant altitude with respect to the take-off point. In contrast, for the mountainous-terrain sequences *NJTerrB* and *NJTerrC*, the UAV maintained a fixed height Above Ground Level (AGL) to ensure flight safety and stable sensor coverage over rapidly varying elevation. Multiple combinations of flight altitudes and speeds were employed to introduce different levels of SLAM difficulty. Each sequence additionally begins with a short stationary or hovering segment to facilitate IMU initialization.


| Scene                 | Sequence  | Scanning Mode | Altitude (m) | Speed (m/s) | Path Length (m) |
| :---------------------: | :---------: | :-------------: | :------------: | :-----------: | :---------------: |
| **Flat Farmland**     | NJFlatB01 | boundary      | 5            | 3           | 434.77          |
|                       | NJFlatB02 | boundary      | 5            | 8           | 464.21          |
|                       | NJFlatB03 | boundary      | 10           | 3           | 456.32          |
|                       | NJFlatB04 | boundary      | 10           | 8           | 462.18          |
|                       | NJFlatB05 | boundary      | 15           | 3           | 465.89          |
|                       | NJFlatB06 | boundary      | 15           | 8           | 454.21          |
|                       | NJFlatC01 | coverage      | 5            | 8           | 805.65          |
|                       | NJFlatC02 | coverage      | 10           | 3           | 801.17          |
|                       | NJFlatC03 | coverage      | 10           | 8           | 798.96          |
|                       | NJFlatC04 | coverage      | 15           | 3           | 822.23          |
| **Hilly Farmland**    | NJHillB01 | boundary      | 8            | 3           | 490.61          |
|                       | NJHillB02 | boundary      | 8            | 8           | 493.07          |
|                       | NJHillB03 | boundary      | 13           | 3           | 480.98          |
|                       | NJHillB04 | boundary      | 13           | 8           | 484.60          |
|                       | NJHillB05 | boundary      | 18           | 3           | 483.84          |
|                       | NJHillB06 | boundary      | 18           | 8           | 488.41          |
|                       | NJHillC01 | coverage      | 8            | 3           | 776.47          |
|                       | NJHillC02 | coverage      | 8            | 8           | 783.31          |
|                       | NJHillC03 | coverage      | 13           | 3           | 761.55          |
|                       | NJHillC04 | coverage      | 13           | 8           | 768.14          |
|                       | NJHillC05 | coverage      | 18           | 3           | 756.07          |
|                       | NJHillC06 | coverage      | 18           | 8           | 769.94          |
| **Terraced Farmland** | NJTerrB01 | boundary      | 3            | 3           | 204.91          |
|                       | NJTerrB02 | boundary      | 6            | 3           | 207.21          |
|                       | NJTerrB03 | boundary      | 6            | 6           | 209.71          |
|                       | NJTerrB04 | boundary      | 9            | 3           | 211.95          |
|                       | NJTerrB05 | boundary      | 9            | 6           | 215.72          |
|                       | NJTerrC01 | coverage      | 3            | 3           | 311.23          |
|                       | NJTerrC02 | coverage      | 3            | 6           | 307.53          |
|                       | NJTerrC03 | coverage      | 6            | 3           | 311.24          |
|                       | NJTerrC04 | coverage      | 6            | 6           | 300.84          |
|                       | NJTerrC05 | coverage      | 9            | 3           | 313.64          |
|                       | NJTerrC06 | coverage      | 9            | 6           | 317.48          |


## Related Work

1. [FAST-LIO2](https://github.com/zhan994/FAST_LIO): Fast Direct LiDAR-inertial Odometry
2. [Faster-LIO](https://github.com/zhan994/faster-lio): Lightweight Tightly Coupled Lidar-inertial Odometry using Parallel Sparse Incremental Voxels
3. [EKF-RIO](https://github.com/zhan994/rio): Radar Inertial Odometry With Online Calibration
4. [GaRLIO](https://github.com/zhan994/GaRLIO): Gravity enhanced Radar-LiDAR-Inertial Odometry


## Citation

```
@misc{zhan2025agrilira4dmultisensoruavdataset,
      title={AgriLiRa4D: A Multi-Sensor UAV Dataset for Robust SLAM in Challenging Agricultural Fields}, 
      author={Zhihao Zhan and Yuhang Ming and Shaobin Li and Jie Yuan},
      year={2025},
      eprint={2512.01753},
      archivePrefix={arXiv},
      primaryClass={cs.RO},
      url={https://arxiv.org/abs/2512.01753}, 
}
```
