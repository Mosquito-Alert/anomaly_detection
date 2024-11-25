# Anomaly Detection Project

This repository contains tools and scripts for performing anomaly detection using geospatial data. Follow the instructions below to set up and use the project.

---

## Prerequisites

1. Ensure you have Python installed (preferably Python 3.8 or higher).
2. Install [pip](https://pip.pypa.io/en/stable/) for package management.
3. Optionally, install [Jupyter Notebook](https://jupyter.org/) for running interactive sessions.

---

## Setup Instructions

### 1. Download Geospatial Data
Download the file **Límites municipales, provinciales y autonómicos** from the official website:  
[https://centrodedescargas.cnig.es/CentroDescargas/catalogo.do?Serie=CAANE](https://centrodedescargas.cnig.es/CentroDescargas/catalogo.do?Serie=CAANE).

### 2. Unzip Data
Extract the downloaded file into a folder named `lineas_limite` in the project root.

### 3. Install Requirements
Run the following command to install all the required Python packages:

```bash
pip install -r requirements.txt
```
### 4. Optional: Start Jupyter
To start a Jupyter Notebook session, use the following command:

```bash
make start
```

### 5. Optional: Stop Jupyter
When you're done with Jupyter, stop the session with:

```bash
make stop
```