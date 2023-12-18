# Real-Time Anomaly Detection and Prediction in Weather
UChicago Applied Data Science Autumn 2023 Hackathon 3rd Place Winner

- Established a **real-time** anomaly detection model using the Pyensign **cloud platform** and River Python package, and implemented a **Pub-Sub** pattern to detect weather data abnormalities
- Applied a Half-Space Trees algorithm for **anomaly detection**, enhancing model accuracy with an Exponential Decay Weighting method to autocorrect the model
- Created a dynamic front-end dashboard using Plotly for real-time **visualization** of the output

## Dashboard Showcase
Weather Details & Anomaly Score of Hawaii:
![image](https://github.com/dengjy1219/Real-Time-Analytics/assets/104877920/a69aff26-9ed8-48e1-af77-36459dc2a506)


Granular Data:

![image](https://github.com/dengjy1219/Real-Time-Analytics/assets/104877920/1c5ccd5f-dedb-4504-a631-87cf67135ea8)

![image](https://github.com/dengjy1219/Real-Time-Analytics/assets/104877920/a38af507-9b45-49b1-9c13-343df62f54dc)

Several weather details change at 23:00 and the weighted score is around 0.97.
