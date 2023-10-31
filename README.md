# DAIBETES - A Diabetes Management Aid

DAIBETES is an experimental project aimed at assisting individuals with type 1 diabetes in managing their condition more effectively.

## Features:

- **Food Data Collection**:
  - Leverages OpenFoodFacts and Typesense to gather and locally store food-related data.
  - Typesense ensures reduced direct API queries to OpenFoodFacts by maintaining a local database.

- **Freestyle Data Ingestion**:
  - Users can upload their blood sugar data from the LibreView app as there's no direct access to Freestyle's API for data retrieval.

- **Data Storage**:
  - All collected data is securely stored in dedicated databases for further analysis and model training.

- **Model Training**:
  - The collected data will be used to train a machine learning model aimed at predicting insulin dosage.

## Setup:

1. Clone the repository.
2. Install the required dependencies from `requirements.txt` using pip:
    ```bash
    pip install -r requirements.txt
    ```
3. Setup your database and update the configuration file with your database credentials.
4. Run the application:
    ```bash
    python app.py
    ```

## Usage:

- Navigate to the `Collect Data` section to input food data and upload Freestyle data.
- Browse the `Show Data` section to view all your entries.
- Access the `Model` section for insights and predictions (coming soon).

## Contribution:

Feel free to fork the project and submit PRs for any enhancements, bug fixes or features you may have.

## License:

This project is open source under the MIT license.

## Contact:

For any inquiries or discussions, reach out at `agathezecevic@gmail.com` 