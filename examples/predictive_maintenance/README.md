# UCI AI4I 2020 predictive-maintenance scenario

This is the second AlgoWeaver scenario. It uses the **AI4I 2020 Predictive
Maintenance Dataset** from the UCI Machine Learning Repository (dataset DOI
`10.24432/C5HS5C`). UCI describes it as a synthetic multivariate dataset that
reflects industrial predictive-maintenance data and publishes it under the
Creative Commons Attribution 4.0 International license.

Source and attribution:

- https://archive.ics.uci.edu/dataset/601/ai4i%2B2020%2Bpredictive%2Bmaintenance%2Bdataset
- Matzka, S. (2020), *Explainable Artificial Intelligence for Predictive Maintenance Applications*.
- The checked-in `ai4i2020.csv` is the downloaded dataset without content changes.

The demo algorithm is an intentionally transparent rule baseline. It flags a
row as high risk when torque is at least 70 Nm and tool wear is at least 180
minutes. It is useful for demonstrating ingestion, evidence linking, static
validation and metric reporting; it is not presented as a production model.
