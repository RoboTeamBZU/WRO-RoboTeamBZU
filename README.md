🔹 Introduction

This repository represents the complete WRO Future Engineers project by Team BZU.
It combines all hardware, software, and 3D-printed components to build a fully autonomous competition robot.

🔹 Team Overview

Team Name: RoboTeam BZU

Institution: Birzeit University

Category: Future Engineers – WRO

Goal: Design a robot capable of completing autonomous navigation, color recognition, and task execution on the competition field.

🔹 Components & Modules

This repository links all submodules and components:

Raspberry Pi 4 – Main controller.

Raspberry Pi Camera – Vision system for object detection.

Ultrasonic Sensor – Distance measurement for obstacle avoidance.

Motor with H-Bridge – Drive system for movement and steering.

TCS3200 Color Sensor – Color recognition for line following and object sorting.

STL Files / 3D Models – Custom mounts and chassis for assembling the robot.

🔹 Usage & Integration

Each module has its own repository with code, wiring, and examples.

The main robot program integrates sensors, motors, and camera for real-time decision-making.

Calibration files, diagrams, and instructions are included in the /docs folder.

🔹 Repository Structure
WRO-RoboTeamBZU/
│── docs/                 # Assembly diagrams, calibration notes, photos
│── raspberry-pi-4/       # Main controller module
│── raspberry-pi-camera/  # Vision module
│── ultrasonic-sensor/    # Obstacle detection module
│── motor-hbridge/        # Drive system module
│── tcs3200-color-sensor/ # Color recognition module
│── STL-Files-3D-models/  # 3D-printed parts
└── README.md             # This file

🔹 Future Improvements

Integrate advanced navigation algorithms.

Add more sensors for redundancy and reliability.

Optimize robot weight and speed using updated 3D parts.

🔹 Acknowledgments

Thanks to WRO organizers for providing the competition framework.

Special thanks to team members for contributions to coding, CAD design, and assembly.
