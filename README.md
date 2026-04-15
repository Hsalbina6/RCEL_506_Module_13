# RCEL_506_Module_13
MVP APP for my final project
# Content for the updated Ecobici README
readme_v2 = """# Ecobici CDMX Analytics App

A Python-powered Streamlit application for analyzing and visualizing the Public Bike Sharing System of Mexico City (Ecobici).

## **Project Overview**
This project provides a user-friendly dashboard to explore Ecobici data, focusing on station availability, geographic distribution, and trip patterns across the city.

## **Tech Stack**
* **Frontend:** Streamlit
* **Data Processing:** Pandas
* **Visualization:** Folium / Plotly / Matplotlib
* **Language:** Python 3.x

## **Features**
* **Live Map:** Real-time visualization of bike and dock availability at each station.
* **Station Statistics:** Detailed breakdown of individual station performance.
* **Heatmaps:** Geographic density analysis of the Ecobici network in CDMX.
* **User Filters:** Capability to filter data by date, time, and specific neighborhoods (Colonias).

## **Installation**

1.  **Clone this repository:**
    ```bash
    git clone [https://github.com/your-username/ecobici-streamlit-app.git](https://github.com/your-username/ecobici-streamlit-app.git)
    cd ecobici-streamlit-app
    ```

2.  **Create a virtual environment (Optional but recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\\Scripts\\activate
    ```

3.  **Install requirements:**
    ```bash
    pip install -r requirements.txt
    ```

## **How to Run**
Execute the following command in your terminal:
```bash
streamlit run app.py
