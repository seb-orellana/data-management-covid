# data-management-covid
Extraction of anonymous COVID-19 data in Bogota, Colombia, allows for filtering, and creation of statistics locally. 

It includes two distinct versions of the code to showcase progression in programming and data processing skills—from an early university version to an improved version using more advanced techniques. Versions: "v1-original" (2020 version), and "v2-upgrade" (2025 version).

Python 3.11.9 64-bit was used. Previous versions might work.
---

## 🔹 Project Description

The goal of this project is to read, analyze, and extract statistics from a local `.csv` database of COVID-19 data in Bogotá. The project allows:

- Reading the CSV file and displaying general statistics
- Filtering data by location or case label
- Extracting infected cases between two specific dates
- Exporting filtered statistics to a new CSV file

---

## 🔸 Versions

### `v1-original/`
Developed during my first year of university. It uses basic file I/O and manual data parsing techniques.

### `v2-upgrade/`
A slighly better version of the original code.
The code now uses libraries to enhance use, allowing for the creation of a GUI and a better management of the data.
Furthermmore, the code has been separated in multiple .py to avoid the clutter of lines in a single file.

There are more possible upgrades, however, there are no plans to applying them soon.

---

## 📝 Requirements

Python 3.11.9 is required. Previous versions might work for the "v1-original/" version.
libraries: tkinter, pathlib, pandas, and tkcalendar.
