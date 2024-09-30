# uber-nyc-dashboard

A Streamlit-based interactive dashboard for exploring Uber pickups and drop-offs in New York City, using public datasets. This project utilizes Streamlit's core features to provide an intuitive, real-time visualization of ride patterns across different times and locations in NYC.

[See it here!](https://uber-nyc-dashboard.streamlit.app/)

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Dataset](#dataset)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

The **uber-nyc-dashboard** allows users to explore Uber pickup and drop-off data for New York City. It includes interactive maps, data filters, and graphs for a comprehensive view of Uber's ride distribution over time and geography.

## Features

- Interactive map showing Uber pickups and drop-offs in NYC
- Data filtering by date and time ranges
- Visualization of ride patterns across neighborhoods
- Statistical insights and summary data
- Real-time updates using Streamlit

## Installation

### Steps

1. Clone this repository:

   ```bash
   git clone https://github.com/ravi-rajpurohit-gh/uber-nyc-dashboard.git
   cd uber-nyc-dashboard
   ```

2. Create and activate the Conda environment:

   ```bash
   conda create --name uber_nyc_env python=3.9
   conda activate uber_nyc_env
   ```

3. Install the required dependencies:

   ```bash
   conda install streamlit pandas numpy
   ```

## Usage

1. Run the Streamlit app:

   ```bash
   streamlit run app.py
   ```

2. Open the app in your browser at `http://localhost:8501` to start interacting with the dashboard.

## Dataset

This project uses the [public Uber Dataset](https://s3-us-west-2.amazonaws.com/streamlit-demo-data/uber-raw-data-sep14.csv.gz) dataset, which includes pickup and drop-off times, locations, and more.

## Contributing

Contributions are welcome! If you would like to contribute to this project, please open an issue or create a pull request.

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.

## License

This project is licensed under the Apache License. See the [LICENSE](LICENSE) file for more details.
