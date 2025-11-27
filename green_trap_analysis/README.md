# Green Trap Analysis

A starter template for fetching World Development Indicators (WDI) data, engineering features, and exploring clustering analyses for green-transition research.

## Project Structure
```
green_trap_analysis/
├── data/
│   ├── raw/                          # Original WDI data
│   └── processed/                    # Engineered features
├── src/
│   ├── config.py                     # Configuration & variables
│   ├── data_loader.py                # WDI API ingestion
│   └── preprocessor.py               # Feature engineering
├── notebooks/
│   └── analysis.ipynb                # Clustering & ML analysis
├── outputs/
│   ├── figures/                      # Visualizations
│   └── models/                       # Trained models (optional)
├── requirements.txt
└── README.md
```

## Installation & Setup
1. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Update `src/config.py` with the economies and indicator codes you want to analyze.
2. Fetch WDI data and write it to `data/raw/wdi_data.csv`:
   ```bash
   python -m src.data_loader
   ```
3. Generate processed features and write them to `data/processed/features.csv`:
   ```bash
   python -m src.preprocessor
   ```
4. Open `notebooks/analysis.ipynb` for exploration and modeling.

## Notes
- The repository uses placeholders (e.g., `.gitkeep`) so empty folders are tracked in version control.
- Add real data to the `data/raw` folder and version it cautiously (consider `.gitignore` for large files).
