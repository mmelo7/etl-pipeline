# 🚀 ETL Pipeline with Airflow, MinIO, and PostgreSQL

This project implements an **ETL (Extract, Transform, Load) pipeline** using **Apache Airflow** to orchestrate the data flow, **MinIO** as a data lake, and **PostgreSQL** as a structured data store. The pipeline extracts cryptocurrency price data from the CoinGecko API, stores raw data in MinIO, processes it, and loads the cleaned data into PostgreSQL.

## 📖 Project Overview

- **Extract**: Fetches cryptocurrency price data from the CoinGecko API.
- **Transform**: Cleans and structures the data.
- **Load**: Stores raw data in MinIO (simulating an AWS S3 data lake) and structured data in PostgreSQL.
- **Orchestrate**: Uses Apache Airflow to manage the entire pipeline.

---

## 🛠️ **Tech Stack**
- **Apache Airflow** 🏗️ - Orchestrates the ETL process.
- **MinIO (S3-like Object Storage)** 🗄️ - Stores raw JSON data.
- **PostgreSQL** 🛢️ - Stores structured and transformed data.
- **Python** 🐍 - Handles API requests, data processing, and database interactions.
- **Docker & Docker Compose** 🐳 - Manages service dependencies.

---

## 📂 **Project Structure**
