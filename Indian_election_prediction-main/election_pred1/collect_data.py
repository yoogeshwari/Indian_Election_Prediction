# data_collection.py
import re
import requests
import pandas as pd
import time
from datetime import datetime

API_KEYS = ["ff06c2f473e589541f271a684eb4ec2e", "777c90099eed5ef46262df507bb0435e", "0f78a4f5c19b6c4d5ae6a9bef55bb297"]

GNEWS_URL = "https://gnews.io/api/v4/search"

all_parties = {
    "National": {
        "BJP": ["BJP", "Bharatiya Janata Party", "Narendra Modi"],
        "Congress": ["Congress", "INC", "Rahul Gandhi"],
        "AAP": ["AAP", "Aam Aadmi Party", "Arvind Kejriwal"],
        "TMC": ["TMC", "Trinamool", "Mamata Banerjee"]
    },

    "State": {
        "Andhra Pradesh": {
            "YSRCP": ["YSRCP", "YSR Congress Party", "Jagan Mohan Reddy"],
            "TDP": ["TDP", "Telugu Desam Party", "Chandrababu Naidu"],
            "JSP": ["JSP", "Janasena Party", "Pawan Kalyan"],
            "INC": ["Congress Andhra Pradesh", "APCC", "Y.S.Sharmila"],
            "BJP": ["BJP Andhra Pradesh", "Daggubati Purandeswari"]
        },
        "Arunachal Pradesh": {
            "BJP": ["BJP Arunachal Pradesh", "Modi Arunachal"],
            "INC": ["Congress Arunachal Pradesh", "Arunachal PCC", "Nabam Tuki"],
            "NPP": ["NPP", "National Peoples Party", "Thangwang Wangham"],
            "JD": ["JD", "Janata Dal", "Kipa Kame"]
        },
        "Assam": {
            "BJP": ["BJP Assam", "Modi Assam"],
            "Congress": ["Congress Assam", "INC Assam"],
            "AIUDF": ["AIUDF", "All India United Democratic Front", "Maulana Badruddin Ajmal "]
        },
        "Bihar": {
            "JD(U)": ["JD", "Janata Dal United", "Nitish Kumar"],
            "RJD": ["RJD", "Rashtriya Janata Dal", "Tejashwi Yadav"],
            "BJP": ["BJP Bihar", "Bharatiya Janata Party Bihar", "Dilip Kumar Jaiswal"],
            "INC": ["Congress Bihar", "Shyam Sunder Singh Dheeraj"]
        },
        "Chhattisgarh": {
            "Congress": ["Congress Chhattisgarh", "Bhupesh Baghel"],
            "BJP": ["BJP Chhattisgarh", "Vishnu Deo Sai"]
        },
        "Goa": {
            "BJP": ["BJP Goa", "Sadanand Tanavade"],
            "INC": ["INC Goa", "Congress Goa", "Yuri Alemao"],
            "AAP": ["AAP Goa", "Aam Aadmi Party Goa", "Amit Palekar"]
        },
        "Gujarat": {
            "BJP": ["BJP Gujarat", "Modi Gujarat"],
            "Congress": ["Congress Gujarat", "INC Gujarat"],
            "AAP": ["AAP Gujarat", "Aam Aadmi Party Gujarat"]
        },
        "Haryana": {
            "BJP": ["BJP Haryana"],
            "Congress": ["Congress Haryana"],
            "JJP": ["JJP", "Jannayak Janata Party"]
        },
        "Himachal Pradesh": {
            "Congress": ["Congress Himachal Pradesh"],
            "BJP": ["BJP Himachal Pradesh"]
        },
        "Jharkhand": {
            "JMM": ["JMM", "Jharkhand Mukti Morcha", "Hemant Soren"],
            "BJP": ["BJP Jharkhand"],
            "INC": ["Congress Jharkhand"]
        },
        "Karnataka": {
            "Congress": ["Congress Karnataka", "Siddaramaiah"],
            "BJP": ["BJP Karnataka"],
            "JD(S)": ["JD", "Janata Dal"]
        },
        "Kerala": {
            "CPI(M)": ["CPI Kerala", "Pinarayi Vijayan"],
            "INC": ["Congress Kerala"],
            "BJP": ["BJP Kerala"],
            "IUML": ["IUML", "Indian Union Muslim League"]
        },
        "Madhya Pradesh": {
            "Congress": ["Congress Madhya Pradesh"],
            "BJP": ["BJP Madhya Pradesh"]
        },
        "Maharashtra": {
            "Shiv Sena (UBT)": ["Shiv Sena", "Uddhav Thackeray"],
            "Shiv Sena (Eknath)": ["Shiv Sena", "Eknath Shinde"],
            "BJP": ["BJP Maharashtra"],
            "NCP": ["NCP", "Nationalist Congress Party"],
            "INC": ["Congress Maharashtra"],
            "MNS": ["MNS", "Maharashtra Navnirman Sena"]
        },
        "Manipur": {
            "BJP": ["BJP Manipur"],
            "INC": ["Congress Manipur"],
            "NPP": ["NPP Manipur"]
        },
        "Meghalaya": {
            "NPP": ["NPP", "National Peoples Party"],
            "INC": ["Congress Meghalaya"],
            "BJP": ["BJP Meghalaya"],
            "UDP": ["UDP", "United Democratic Party"]
        },
        "Mizoram": {
            "MNF": ["MNF", "Mizo National Front"],
            "ZPM": ["ZPM", "Zoram Peoples Movement"],
            "INC": ["Congress Mizoram"]
        },
        "Nagaland": {
            "NDPP": ["NDPP", "Nationalist Democratic Progressive Party"],
            "BJP": ["BJP Nagaland"],
            "NCP": ["NCP Nagaland"]
        },
        "Odisha": {
            "BJD": ["BJD", "Biju Janata Dal", "Naveen Patnaik"],
            "BJP": ["BJP Odisha"],
            "INC": ["Congress Odisha"]
        },
        "Punjab": {
            "AAP": ["AAP Punjab", "Aam Aadmi Party Punjab"],
            "INC": ["Congress Punjab"],
            "SAD": ["SAD", "Shiromani Akali Dal"],
            "BJP": ["BJP Punjab"]
        },
        "Rajasthan": {
            "BJP": ["BJP Rajasthan"],
            "INC": ["Congress Rajasthan"]
        },
        "Sikkim": {
            "SKM": ["SKM", "Sikkim Krantikari Morcha"],
            "SDF": ["SDF", "Sikkim Democratic Front"],
            "BJP": ["BJP Sikkim"]
        },
        "Tamil Nadu": {
            "DMK": ["DMK", "Dravida Munnetra Kazhagam", "MK Stalin"],
            "AIADMK": ["AIADMK", "All India Anna Dravida Munnetra Kazhagam", "EPS"],
            "BJP": ["BJP Tamil Nadu", "Modi Tamil Nadu"],
            "INC": ["Congress Tamil Nadu"],
            "TVK": ["TVK", "Tamizhaga Vetri Kazhagam", "Vijay"],
            "PMK": ["PMK", "Pattali Makkal Katchi"]
        },
        "Telangana": {
            "BRS": ["BRS", "Bharat Rashtra Samithi", "KCR"],
            "INC": ["Congress Telangana"],
            "BJP": ["BJP Telangana"],
            "AIMIM": ["AIMIM", "All India Majlis-e-Ittehad-ul-Muslimeen"]
        },
        "Tripura": {
            "BJP": ["BJP Tripura"],
            "CPI(M)": ["CPI Tripura"],
            "INC": ["Congress Tripura"],
            "TIPRA Motha": ["TIPRA Motha", "Tipraha Indigenous Progressive Regional Alliance"]
        },
        "Uttar Pradesh": {
            "BJP": ["BJP Uttar Pradesh"],
            "SP": ["SP", "Samajwadi Party", "Akhilesh Yadav"],
            "BSP": ["BSP", "Bahujan Samaj Party", "Mayawati"],
            "INC": ["Congress Uttar Pradesh"],
            "RLD": ["RLD", "Rashtriya Lok Dal"]
        },
        "Uttarakhand": {
            "BJP": ["BJP Uttarakhand"],
            "INC": ["Congress Uttarakhand"]
        },
        "West Bengal": {
            "TMC": ["TMC", "Trinamool Congress", "Mamata Banerjee"],
            "BJP": ["BJP West Bengal"],
            "INC": ["Congress West Bengal"],
            "CPI(M)": ["CPI West Bengal"]
        }
   }
}

def fetch_articles(query, max_articles=10):
    for idx in range(len(API_KEYS)):
        params = {
            'q': query,
            'lang': 'en',
            'country': 'in',
            'max': max_articles,
            'token': API_KEYS[idx]
        }
        response = requests.get(GNEWS_URL, params=params)
        if response.status_code == 200:
            return response.json().get('articles', [])
    print(f"All API keys failed for query: {query}")
    return []

def collect_data():
    national_df = pd.DataFrame(columns=["text", "party", "scope"])
    state_df = pd.DataFrame(columns=["text", "party", "state", "scope"])

    for party, query_list in all_parties["National"].items():
        for query in query_list:
            articles = fetch_articles(query)
            for article in articles:
                title = article.get('title', '')
                if title:
                    national_df = pd.concat([national_df, pd.DataFrame([{
                        "text": title,
                        "party": party,
                        "scope": "National",
                    }])], ignore_index=True)
            print(f"Collected articles for {party} nationally using query '{query}'")
            time.sleep(2)

    for state, parties in all_parties["State"].items():
        for party, query_list in parties.items():
            for query in query_list:
                articles = fetch_articles(query)
                for article in articles:
                    title = article.get('title', '')
                    if title:
                        state_df = pd.concat([state_df, pd.DataFrame([{
                            "text": title,
                            "party": party,
                            "state": state,
                            "scope": "State",
                        }])], ignore_index=True)
                print(f"Collected articles for {party} in {state} using query '{query}'")
                time.sleep(2)

    combined_df = pd.concat([national_df, state_df], ignore_index=True)

    output_excel = "collected_data.xlsx"
    combined_df.to_excel(output_excel, index=False)

    print(f"Data successfully saved to {output_excel}")

if __name__ == "__main__":
    collect_data()
