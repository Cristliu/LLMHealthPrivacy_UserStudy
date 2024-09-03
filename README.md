# Prevalence Overshadows Concerns? Understanding Chinese Users’ Privacy Awareness and Expectations Towards LLM-based Healthcare Consultation

This repository contains the code and redacted datasets for our IEEE S&P 2025 paper: *"Prevalence Overshadows Concerns? Understanding Chinese Users’ Privacy Awareness and Expectations Towards LLM-based Healthcare Consultation"*


---

## REDACTED Datasets

This repository provides datasets where sensitive information has been removed to address ethical concerns. Specifically:
- **Demographics & Background** sections have been removed.
- Responses containing free-text answers have been marked as **REDACTED**.

All text or statistical features that could directly or indirectly identify participants have been deleted.

## Data Analysis

To explore the data analysis details, please refer to the following Jupyter Notebooks:

- DATA_Analysis_Part I - Awareness During Consultation (RQ1).ipynb
- DATA_Analysis_Part II - Privacy Expectations (RQ2).ipynb
- DATA_Analysis_Part III - Attitudes and Previous Experiences (RQ3).ipynb

The scripts provided in these notebooks have been processed to handle any sensitive information. Note that some datasets (e.g., `DataforCI_ShortColumnName.xlsx` and `00Codebook`) have been hidden from the release to maintain privacy.

## LLM-based Healthcare Chatbot

The deployed system can be accessed at:
- [Chinese version](http://healthllm.top/LLMHPri/encindexzh/)
- [English version](http://healthllm.top/LLMHPri/encindexen/)

The `HealthcareChatbot` directory contains the local version of the Healthcare Chatbot developed using the Django framework. This chatbot provides a responsive user interface and a survey questionnaire interface across multiple platforms. 
The system includes the informed consent form, the healthcare chatbot interface, and the embedded questionnaire.
*Note:* Some Quality Control methods, such as restricting repeated participation in the survey, have been removed from this release.

### Running the Project Locally

If you have experience with running Django projects, follow these steps to run the Healthcare Chatbot locally:

1. **Review `settings.py` and `views.py`:** Update or replace necessary fields, particularly the `DATABASES` and `openai` configuration.

2. **Install dependencies:**
    `pip install -r requirements.txt` or `pip install -r simple-requirements.txt`
    
   If any packages fail to install, please manually install them.

3. **Perform database migrations:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

4. **Run the development server:**
    ```bash
    python manage.py runserver
    ```

5. **Access the system:** Open a web browser and go to:
   - [http://127.0.0.1:8000/LLMHPri/encindexzh/](http://127.0.0.1:8000/LLMHPri/encindexzh/) for the Chinese version.
   - [http://127.0.0.1:8000/LLMHPri/encindexen/](http://127.0.0.1:8000/LLMHPri/encindexen/) for the English version.


---

## Citation
Please consider citing the following paper if you found our work useful.

> Prevalence Overshadows Concerns? Understanding Chinese Users’ Privacy Awareness and Expectations Towards LLM-based Healthcare Consultation, *IEEE S&P 2025*.