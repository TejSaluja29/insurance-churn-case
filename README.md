Ontario Life Insurance Churn Prediction

Project overview

This repository turns the Ontario Life insurance churn case into a polished, business-facing analytics project. The goal is not only to predict churn, but to translate churn risk into a ranked outreach list, a tiered retention program, and a pilot measurement plan.

The project is structured as a consulting-style report. The main deliverable is a clean Jupyter notebook that connects data, modeling, and business action in one narrative.

Business question

Ontario Life wants to reduce churn across its life insurance portfolio by answering four questions:
1. Which customers are most at risk of churn?
2. What patterns in the data explain churn?
3. Which operational levers should the company pull first?
4. How should success be measured after rollout?

Main deliverable

notebooks/01_ontario_life_churn_report.ipynb

This notebook is the final analysis. It uses a balanced logistic regression model as the primary production-facing model because it matches the final slide narrative, keeps the modeling transparent, and supports threshold-based triage.

Key results

Model performance
- Holdout AUC-ROC: 0.6329
- Accuracy at threshold 0.58: 78.8%
- Average precision: 0.0980
- Precision at threshold 0.58: 8.8%
- Recall at threshold 0.58: 28.2%

What the data says
- Overall churn rate is 5.9%
- Churned customers have lower median satisfaction: 64.0 vs 68.8 for retained customers
- Churned customers carry much higher median premiums: $434.70 vs $176.40
- Churned customers are longer-tenured: median 9 years vs 7 years
- Churn rises sharply by tenure band, from 2.42% in years 0 to 2 to 8.40% after year 10
- Among customers who churned, the top stated reasons were Better Offer Elsewhere (33.6%), Premiums Unaffordable (29.0%), No Longer Needed (21.3%), and Poor Customer Service (16.2%)

Threshold strategy
- Risk >= 0.75 flags 52 customers in the holdout set
- Risk >= 0.70 flags 100 customers
- Risk >= 0.58 flags 373 customers

Ranking value
- Top 10% of customers by risk contain 17.9% of churners
- Top 20% contain 29.9%
- Top 30% contain 45.3%

Business impact

This project intentionally frames the model as a triage tool, not a magic classifier.

The model is useful because it helps Ontario Life spend retention effort where risk is most concentrated:
- If the team can only contact 100 customers, the 0.70 threshold produces a manageable list and surfaces 15 actual churners in the holdout sample. Random outreach to 100 customers would surface about 6 churners at the base rate.
- If the team wants broader coverage, the 0.58 threshold captures more churners and supports low-cost digital outreach at scale.
- The deck's rollout targets such as save rate, cost per save, and ROI should be treated as pilot KPIs, not as outputs directly calculated from this dataset.

Methodology

1. Clean and profile the 10,000-customer dataset.
2. Use churn_reason only for descriptive analysis, never as a predictive feature.
3. Engineer an annual premium and CLV proxy.
4. One-hot encode channel, health status, and policy term.
5. Train a balanced logistic regression model on a stratified train/test split.
6. Evaluate ranking quality, threshold trade-offs, and gains.
7. Convert model scores into a tiered retention strategy.

Repository structure

.
├── README.md
├── requirements.txt
├── data/
│   └── Insurance Churn Dataset.xlsx
├── notebooks/
│   └── ontario_life_churn_report.ipynb
├── src/
│   └── churn_utils.py
├── reports/
│   └── figures/
│       ├── churn_reasons.png
│       ├── gains_chart.png
│       ├── logistic_drivers.png
│       ├── satisfaction_gap.png
│       ├── tenure_band_churn.png
│       └── threshold_tradeoff.png
├── references/
│   ├── Insurance Churn Case.pdf
│   └── Reducing_Churn_at_Ontario_Life_Early_Warning_Retention_System.pptx
└── notes/
    └── refactor_notes.md

How to run

1. Create a virtual environment.
2. Install dependencies with:
   pip install -r requirements.txt
3. Launch Jupyter:
   jupyter notebook
4. Open notebooks/01_ontario_life_churn_report.ipynb
5. Run all cells from top to bottom.

Recommended charts for the README

Use these exported figures in the public GitHub landing page:
- reports/figures/satisfaction_gap.png
- reports/figures/tenure_band_churn.png
- reports/figures/gains_chart.png
- reports/figures/logistic_drivers.png

Notes and limitations

- This repository keeps the model intentionally simple and interpretable.
- The dataset supports churn prediction and prioritization, but not full causal ROI measurement.
- Cost per save, retained premium, and incremental ROI require intervention data that is not in the raw case dataset.
- The feature set preserves the final deck logic. Because CLV proxy overlaps with tenure and premium, coefficient magnitudes should be interpreted directionally, not as causal effect sizes.

What makes this strong for recruiters

- The notebook reads like a client-facing report, not a class submission.
- The model is tied to concrete operating decisions.
- The write-up clearly separates what is measured from what is proposed.
- The project shows judgment around leakage, thresholding, and business trade-offs.

Suggested next upgrades

1. Add probability calibration and a calibration curve.
2. Add a small cost-simulation model for retention economics.
3. Add a lightweight Streamlit app that scores uploaded policyholder files.
4. Add unit tests for feature engineering and threshold logic.
5. Add a one-page executive memo PDF as a portfolio asset.
