# TDT Fibre Photometry Analysis
This code is based on Thomas Akam's guide to processing Fibre Photometry Data in python [found here](https://github.com/ThomasAkam/photometry_preprocessing).
It has two seperate python files to run to analyse the data.

## Installation
First you need to download the repository from GitHub.
```
git clone https://github.com/kasparmccoy/FiPho_2C.git
```
Then change the directory to the right directory
```
cd FiPho_2C
```
Then create a conda environment
```
conda env create -n FiPho -f Dependencies.yaml
```
## Usage
First set your current directory to the `Fi_Pho_2C` folder
```
cd FiPho_2C
```
Next create a settings excel file based on the example provided and name it `settings.xlsx`.
Place this file in the output directory of your choosing, copy the path to this directory to the clipboard.

For data extraction from TDT tanks run the following code and paste the output directory path into the terminal:
```
python data_extract.py
```
For data analysis from this output directory run the following code and paste the output directory path into the terminal:
```
python data_analysis.py
```
