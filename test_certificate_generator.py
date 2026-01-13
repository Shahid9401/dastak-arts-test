import pandas as pd
from certificate_generator import generate_certificates_for_event

def run_test():
    # ✅ Sample test dataset (4 variations)
    test_data = [
        {"Event": "Group Dance", "Status": "final", "Name": "Anandha Krishnan", "Class": "MSc Physics", "Group": "Group 4", "Position": "First"},
        {"Event": "Group Dance", "Status": "final", "Name": "Mohammed Shahid Ibrahim", "Class": "BSc Physics", "Group": "Group 2", "Position": "Second"},
        {"Event": "Group Dance", "Status": "final", "Name": "Ayesha Fathima", "Class": "BA English", "Group": "Group 1", "Position": "Third"},
        {"Event": "Group Dance", "Status": "final", "Name": "Sreehari Narayanan V P", "Class": "BCom Finance", "Group": "Group 3", "Position": "First"},
    ]

    df = pd.DataFrame(test_data)

    # ✅ Call your generator using the dataframe directly
    result = generate_certificates_for_event("Group Dance", source_df=df)
    print(result)

if __name__ == "__main__":
    run_test()