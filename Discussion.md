
### 🔹 Discussion: Our Approach to the Challenges

Navigating the WRO Future Engineers challenges requires a smart strategy. Here’s a breakdown of our solution ideas for each part of the competition, comparing how we did it with our available components versus how it could be done ideally.

#### 1. Open Challenge: Lap Racing on a Variable-Width Track

*   **The Idea:** The main goal is to complete three laps as quickly as possible without hitting the walls, even as the track width changes.
*   **Our Solution with Available Parts:** We use a two-sensor strategy. The **Raspberry Pi Camera** looks ahead to see the entire lane and prepare for wide corners. The **TCS3200 Color Sensor** points down at the track right in front of the vehicle to precisely follow the line. The car's brain (the Raspberry Pi) constantly blends this "far sight" and "near sight" to decide how to steer. For the narrow 600mm track sections, we simply tell the car to drive slower and make smaller steering adjustments to avoid hitting the walls.
*   **How It Could Be Better:** In an ideal world, we would add a **Rotary Encoder** on the wheel. This would act like an odometer, telling the car exactly how far it has traveled. This would allow it to know its position on the track and anticipate corners instead of just reacting to what it sees. An **IMU** would also help keep the car perfectly straight and stable.

#### 2. Obstacle Challenge: Traffic Signs

*   **The Idea:** The robot must recognize red and green pillars and pass them on the correct side (red on right, green on left) without touching them.
*   **Our Solution with Available Parts:** Our **Pi Camera** is our "eye" for this task. We programmed it to constantly scan for large blocks of red or green color. When it sees one, it identifies the color and estimates its position. The logic is simple: if it's a **green** pillar, the car shifts slightly to the **left** of the lane to pass it. If it's a **red** pillar, it shifts to the **right**. After passing, it centers itself again using the line.
*   **How It Could Be Better:** A more advanced solution would use **Machine Learning** to train a model to recognize the pillars. This would be much more reliable than just looking for colors, as it wouldn't be fooled by shadows or similar-colored objects in the background. Using two cameras for depth perception could also help the car judge the distance to the pillar more accurately.

#### 3. Obstacle Challenge: Parallel Parking

*   **The Idea:** After three laps, the robot must find a parking spot and park inside it parallel to the wall.
*   **Our Solution with Available Parts:** This is the toughest part. We use the camera to find the **magenta-colored** parking blocks. Once found, we use a pre-programmed "dance" of movements. The car stops, moves backward while turning the wheels, then straightens out. We use the **Ultrasonic Sensor** to know when to stop before hitting the block. It's a fixed sequence that we tuned through lots of practice.
*   **How It Could Be Better:** With a **Rotary Encoder**, the car could measure the exact distance it moves, making the parking maneuver smooth and precise every time. Advanced teams could use complex math (like path-planning algorithms) to calculate the perfect steering angles and distances dynamically, instead of relying on a pre-set sequence.

### 🔹 A Note on Our Journey

We are proud of what we have built with the resources we have. The truth is, creating the "perfect" robot was not possible for us. As students in Palestine, our time is limited by university workload, and high-quality components like precision IMUs and encoders are very difficult to find and too expensive for our budget.

Our robot may not be perfect, and its performance might not be flawless. **But that doesn't mean we will stop.** For us, this isn't just about winning. It's about the **passion** for building something from scratch. It's about **teamwork**, **learning**, and **having fun** together. We believe that the true spirit of engineering is to persevere and innovate, no matter the obstacles. We will continue to learn, improve, and compete with pride, because for Team BZU, the journey itself is the greatest achievement.
