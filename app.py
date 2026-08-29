import os
import re
from pathlib import Path
from collections import defaultdict
import pandas as pd
from bs4 import BeautifulSoup
import streamlit as st

# --- STREAMLIT CONFIGURATION ---
st.set_page_config(page_title="Hansard Master Search", layout="wide")
st.title(" Singapore Hansard Files Keyword Search")

# --- INITIALIZE NLP ---
@st.cache_resource
def load_nlp():
    return None

nlp = load_nlp()

# --- MP METADATA FROM YOUR SCRIPT ---
mp_metadata = {
    "Mr Lim Biow Chuan": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Joan Pereira": {"gender": "Female", "ethnicity": "Other", "mp_type": "MP"},
    "Dr Amy Khor Lean Suan": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Nadia Ahmad Samdin": {"gender": "Female", "ethnicity": "Malay", "mp_type": "MP"},
    "Mr Desmond Tan": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Murali Pillai": {"gender": "Male", "ethnicity": "Indian", "mp_type": "MP"},
    "Mr Gan Thiam Poh": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Seah Kian Peng": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Zaqy Mohamad": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
    "Mr Dennis Tan Lip Fong": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Indranee Rajah": {"gender": "Female", "ethnicity": "Indian", "mp_type": "MP"},
    "Mr Alex Yam": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Dr Wan Rizal": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
    "Ms Sylvia Lim": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Abdul Samad": {"gender": "Male", "ethnicity": "Malay", "mp_type": "NMP"},
    "Mr Desmond Choo": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Shawn Huang Wei Zhong": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Mohd Fahmi Bin Aliman": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
    "Mr Kwek Hian Chuan Henry": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Chong Kee Hiong": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Don Wee": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Hazel Poa": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "NCMP"},
    "Mr Gerald Giam Yean Song": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Patrick Tay Teck Guan": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Yeo Wan Ling": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Zhulkarnain Abdul Rahim": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
    "Dr Ng Eng Hen": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Heng Chee How": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Poh Li San": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Edward Chia Bing Hui": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Tin Pei Ling": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Derrick Goh": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Saktiandi Supaat": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
    "Mr Baey Yam Keng": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Liang Eng Hwa": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Raj Joshua Thomas": {"gender": "Male", "ethnicity": "Indian", "mp_type": "NMP"},
    "Dr Vivian Balakrishnan": {"gender": "Male", "ethnicity": "Indian", "mp_type": "MP"},
    "Dr Tan Wu Meng": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Leong Mun Wai": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "NCMP"},
    "Mr Pritam Singh": {"gender": "Male", "ethnicity": "Indian", "mp_type": "MP"},
    "Mr Sitoh Yih Pin": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Hany Soh": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Rahayu Mahzam": {"gender": "Female", "ethnicity": "Malay", "mp_type": "MP"},
    "Mr Heng Swee Keat": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Leon Perera": {"gender": "Male", "ethnicity": "Indian", "mp_type": "MP"},
    "Mr Louis Ng Kok Kwang": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Grace Fu Hai Yien": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Edwin Tong Chun Fai": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Gan Kim Yong": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Ong Ye Kung": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Desmond Lee": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Chua Kheng Wee Louis": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms He Ting Ru": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Assoc Prof Razwana Begum Abdul Rahim": {"gender": "Female", "ethnicity": "Malay", "mp_type": "NMP"},
    "Mr Ong Hua Han": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "NMP"},
    "Ms Usha Chandradas": {"gender": "Female", "ethnicity": "Indian", "mp_type": "NMP"},
    "Mr Keith Chua": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "NMP"},
    "Mr Mark Lee": {"gender": "Male", "ethnicity": "Indian", "mp_type": "NMP"},
    "Mr Neil Parkeh Nimil Rajnikant": {"gender": "Male", "ethnicity": "Malay", "mp_type": "NMP"},
    "Ms See Jinli Jean": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "NMP"},
    "Mr Yip Hon Weng": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Xie Yao Quan": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Miss Rachel Ong": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Shareal Taha": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
    "Ms Carrie Tan": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Assoc Prof Jamus Jerome Lim": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Darryl David": {"gender": "Male", "ethnicity": "Indian", "mp_type": "MP"},
    "Mr Melvin Yong Yik Chye": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Mariam Jaafar": {"gender": "Female", "ethnicity": "Malay", "mp_type": "MP"},
    "Miss Cheryl Chan Wei Ling": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Ang Wei Neng": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Dr Lim Wee Kiak": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Eric Chua": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Denise Phua Lay Peng": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Foo Mee Har": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Muhamad Faisal Abdul Manap": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
    "Mr Muhamad Faisal Bin Abdul Manap": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
    "Mr Vikram Nair": {"gender": "Male", "ethnicity": "Indian", "mp_type": "MP"},
    "Mr Alvin Tan": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Sun Xueling": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Tan Kiat How": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Dr Koh Poh Koon": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Sim Ann": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Christopher De Souza": {"gender": "Male", "ethnicity": "Other", "mp_type": "MP"},
    "Ms Jessica Tan Soon Neo": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Dr Janil Puthucheary": {"gender": "Male", "ethnicity": "Indian", "mp_type": "MP"},
    "Ms Low Yen Ling": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Assoc Prof Dr Muhammad Faishal Ibrahim": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
    "Ms Gan Siow Huang": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Dr Tan See Leng": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Dr Mohamad Maliki Osman": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
    "Mr Chan Chun Sing": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr K Shanmugam": {"gender": "Male", "ethnicity": "Indian", "mp_type": "MP"},
    "Mr Lee Hsien Loong": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Lawrence Wong": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Teo Chee Hean": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Masagos Zulkifli B M M": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
        "Miss Cheng Li Hui": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Mohd Fahmi Aliman": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
    "Ms Raeesah Khan": {"gender": "Female", "ethnicity": "Malay", "mp_type": "MP"},
    "Mr Sharael Taha": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
    "Mdm Deputy Speaker": {"gender": "Female", "ethnicity": "Unknown (speaker)", "mp_type": "MP"},
    "Dr Shahira Abdullah": {"gender": "Female", "ethnicity": "Malay", "mp_type": "NMP"},
    "Ms Ng Ling Ling": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Janet Ang": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "NMP"},
    "Mr Neil Parekh Nimil Rajnikant": {"gender": "Male", "ethnicity": "Indian", "mp_type": "NMP"},
    "Ms Anthea Ong": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "NMP"},
    "Mr Mark Chay": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "NMP"},
    "Assoc Prof Daniel Goh Pei Siong": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "NCMP"},
    "Mr Png Eng Huat": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Irene Quay Siew Ching": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "NMP"},
    "Prof Lim Sun Sun": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "NMP"},
    "Ms Yip Pin Xiu": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "NMP"},
    "Mr Chen Show Mao": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mrs Josephine Teo": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Chee Hong Tat": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
        "Mr S Iswaran": {"gender": "Male", "ethnicity": "Indian", "mp_type": "MP"},
    "Dr Syed Harun Alhabsyi": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
    "Dr Intan Azura Mokhtar": {"gender": "Female", "ethnicity": "Malay", "mp_type": "MP"},
    "Prof Fatimah Lateef": {"gender": "Female", "ethnicity": "Malay", "mp_type": "MP"},
    "Mr Zainal Sapari": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
        "Mr Alex Yam Ziming": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Assoc Prof Walter Theseira": {"gender": "Male", "ethnicity": "Other", "mp_type": "NMP"},
        "Assoc Prof Daniel Goh Pei Siong": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "NCMP"},
    "Assoc Prof Dr Muhammad Faishal Ibrahim": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
    "Assoc Prof Jamus Jerome Lim": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Assoc Prof Razwana Begum Abdul Rahim": {"gender": "Female", "ethnicity": "Malay", "mp_type": "NMP"},
    "Assoc Prof Walter Theseira": {"gender": "Male", "ethnicity": "Other", "mp_type": "NMP"},
    "Dr Amy Khor Lean Suan": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Dr Chia Shi-Lu": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Dr Intan Azura Mokhtar": {"gender": "Female", "ethnicity": "Malay", "mp_type": "MP"},
    "Dr Janil Puthucheary": {"gender": "Male", "ethnicity": "Indian", "mp_type": "MP"},
    "Dr Koh Poh Koon": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Dr Lam Pin Min": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Dr Lily Neo": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Dr Lim Wee Kiak": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Dr Mohamad Maliki Bin Osman": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
    "Dr Ng Eng Hen": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Dr Shahira Abdullah": {"gender": "Female", "ethnicity": "Malay", "mp_type": "NMP"},
    "Dr Syed Harun Alhabsyi": {"gender": "Male", "ethnicity": "Malay", "mp_type": "NMP"},
    "Dr Tan See Leng": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Dr Tan Wu Meng": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Dr Tan Yia Swam": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "NMP"},
    "Dr Teo Ho Pin": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Dr Vivian Balakrishnan": {"gender": "Male", "ethnicity": "Indian", "mp_type": "MP"},
    "Dr Wan Rizal": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
    "Miss Cheng Li Hui": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Miss Cheryl Chan Wei Ling": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Miss Rachel Ong": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Abdul Samad": {"gender": "Male", "ethnicity": "Malay", "mp_type": "NMP"},
    "Mr Alex Yam": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Alex Yam Ziming": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Alvin Tan": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Amrin Amin": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
    "Mr Ang Hin Kee": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Ang Wei Neng": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Arasu Duraisamy": {"gender": "Male", "ethnicity": "Indian", "mp_type": "NMP"},
    "Mr Baey Yam Keng": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Cedric Foo Chee Keng": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Chan Chun Sing": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Charles Chong": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Chee Hong Tat": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Chen Show Mao": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Cheng Hsing Yao": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "NMP"},
    "Mr Chong Kee Hiong": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Chua Kheng Wee Louis": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Darryl David": {"gender": "Male", "ethnicity": "Indian", "mp_type": "MP"},
    "Mr Dennis Tan Lip Fong": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Derrick Goh": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Desmond Choo": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Desmond Lee": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Desmond Tan": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Don Wee": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Douglas Foo": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "NMP"},
    "Mr Edward Chia Bing Hui": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Edwin Tong": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Edwin Tong Chun Fai": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Eric Chua": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Gan Kim Yong": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Gan Thiam Poh": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Gerald Giam Yean Song": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Heng Chee How": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Heng Swee Keat": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr K Shanmugam": {"gender": "Male", "ethnicity": "Indian", "mp_type": "MP"},
    "Mr Keith Chua": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "NMP"},
    "Mr Khaw Boon Wan": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Kwek Hian Chuan Henry": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Lawrence Wong": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Lee Hsien Loong": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Lee Yi Shyan": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Leon Perera": {"gender": "Male", "ethnicity": "Indian", "mp_type": "MP"},
    "Mr Leong Mun Wai": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "NCMP"},
    "Mr Leong Wai Mun": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "NCMP"},
    "Mr Liang Eng Hwa": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Lim Swee Say": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Louis Ng Kok Kwang": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Low Thia Khiang": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Mark Chay": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "NMP"},
    "Mr Mark Lee": {"gender": "Male", "ethnicity": "Indian", "mp_type": "NMP"},
    "Mr Masagos Zulkifli B M M": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
    "Mr Melvin Yong Yik Chye": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Mohamed Irshad": {"gender": "Male", "ethnicity": "Indian", "mp_type": "NMP"},
    "Mr Mohd Fahmi Aliman": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
    "Mr Speaker": {"gender": "Male", "ethnicity": "Unknown (speaker)", "mp_type": "MP"},
        "Mr Mohd Fahmi Aliman": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
    "Mr Mohd Fahmi Bin Aliman": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
    "Mr Muhamad Faisal Bin Abdul Manap": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
    "Mr Murali Pillai": {"gender": "Male", "ethnicity": "Indian", "mp_type": "MP"},
    "Mr Neil Parekh Nimil Rajnikant": {"gender": "Male", "ethnicity": "Indian", "mp_type": "NMP"},
    "Mr Ng Chee Meng": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Ong Hua Han": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "NMP"},
    "Mr Ong Teng Koon": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Ong Ye Kung": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Patrick Tay Teck Guan": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Png Eng Huat": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Pritam": {"gender": "Male", "ethnicity": "Indian", "mp_type": "MP"},
    "Mr Pritam Singh": {"gender": "Male", "ethnicity": "Indian", "mp_type": "MP"},
    "Mr Raj Joshua Thomas": {"gender": "Male", "ethnicity": "Indian", "mp_type": "NMP"},
    "Mr S Iswaran": {"gender": "Male", "ethnicity": "Indian", "mp_type": "MP"},
    "Mr Saktiandi Supaat": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
    "Mr Sam Tan Chin Siong": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Seah Kian Peng": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Sharael Taha": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
    "Mr Shawn Huang Wei Zhong": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Sitoh Yih Pin": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Tan Chuan-Jin": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Tan Kiat How": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Teo Chee Hean": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Teo Ser Luck": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Terence Ho Wee San": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "NMP"},
    "Mr Tharman Shanmugaratnam": {"gender": "Male", "ethnicity": "Indian", "mp_type": "MP"},
    "Mr Vikram Nair": {"gender": "Male", "ethnicity": "Indian", "mp_type": "MP"},
    "Mr Xie Yao Quan": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Yee Chia Hsing": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Yip Hon Weng": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "MP"},
    "Mr Zainal Sapari": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
    "Mr Zaqy Mohamad": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
    "Mr Zhulkarnain Abdul Rahim": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},
    "Mrs Josephine Teo": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Anthea Ong": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "NMP"},
    "Ms Carrie Tan": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Denise Phua Lay Peng": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Foo Mee Har": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Gan Siow Huang": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Grace Fu Hai Yien": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Hany Soh": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Hazel Poa": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "NCMP"},
    "Ms He Ting Ru": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Indranee Rajah": {"gender": "Female", "ethnicity": "Indian", "mp_type": "MP"},
    "Ms Irene Quay Siew Ching": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "NMP"},
    "Ms Janet Ang": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "NMP"},
    "Ms Jessica Tan Soon Neo": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Joan Pereira": {"gender": "Female", "ethnicity": "Other", "mp_type": "MP"},
    "Ms Low Yen Ling": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Mariam Jaafar": {"gender": "Female", "ethnicity": "Malay", "mp_type": "MP"},
    "Ms Nadia Ahmad Samdin": {"gender": "Female", "ethnicity": "Malay", "mp_type": "MP"},
    "Ms Ng Ling Ling": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Poh Li San": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Raeesah Khan": {"gender": "Female", "ethnicity": "Malay", "mp_type": "MP"},
    "Ms Rahayu Mahzam": {"gender": "Female", "ethnicity": "Malay", "mp_type": "MP"},
    "Ms See Jinli Jean": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "NMP"},
    "Ms Sim Ann": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Sun Xueling": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Sylvia Lim": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Tin Pei Ling": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Usha Chandradas": {"gender": "Female", "ethnicity": "Indian", "mp_type": "NMP"},
    "Ms Yeo Wan Ling": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "MP"},
    "Ms Yip Pin Xiu": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "NMP"},
    "Prof Fatimah Lateef": {"gender": "Female", "ethnicity": "Malay", "mp_type": "MP"},
    "Prof Hoon Hian Teck": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "NMP"},
    "Prof Koh Lian Pin": {"gender": "Male", "ethnicity": "Chinese", "mp_type": "NMP"},
    "Prof Lim Sun Sun": {"gender": "Female", "ethnicity": "Chinese", "mp_type": "NMP"},
    "Prof Yaacob Ibrahim": {"gender": "Male", "ethnicity": "Malay", "mp_type": "MP"},




}

# --- TEXT HELPER FUNCTIONS ---
def extract_sitting_date(file_path):
    filename = Path(file_path).name
    match = re.search(r"sittingdate=(\d{2})-(\d{2})-(\d{4})", filename, flags=re.IGNORECASE)
    if match:
        day, month, year = match.groups()
        return f"{year}-{month}-{day}"
    return "Unknown"

valid_name_pattern = re.compile(
    r"^(?:Mr|Ms|Miss|Mrs|Dr|Mdm|Minister|Assoc\s+Prof|Assoc\s+Prof\s+Dr|Professor|Prof)\s+"
    r"[A-Z][a-zA-Z.\-']*(?:\s+[A-Z][a-zA-Z.\-']*){0,7}$"
)

def clean_speaker_name(raw_name):
    name = str(raw_name).split(":")[0]
    name = re.sub(r"\s*\(.*?\)", "", name)
    return re.sub(r"\s+", " ", name).strip()

def split_into_sentences(text):
    text = re.sub(r"\s+", " ", str(text).strip())
    if not text:
        return []

    abbreviations = {
        "Mr.": "Mr<PERIOD>",
        "Ms.": "Ms<PERIOD>",
        "Mrs.": "Mrs<PERIOD>",
        "Dr.": "Dr<PERIOD>",
        "Prof.": "Prof<PERIOD>",
        "Mdm.": "Mdm<PERIOD>",
        "Assoc Prof.": "Assoc Prof<PERIOD>",
    }

    for old, placeholder in abbreviations.items():
        text = text.replace(old, placeholder)

    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"“‘])', text)
    restored = []

    for sentence in sentences:
        cleaned = sentence.strip()
        if not cleaned:
            continue
        for placeholder, original in {v: k for k, v in abbreviations.items()}.items():
            cleaned = cleaned.replace(placeholder, original)
        restored.append(cleaned)
    return restored

# --- DATA LOADING & PROCESSING ENGINE ---

# --- DATA LOADING & PROCESSING ENGINE --- 
@st.cache_data 
def process_all_files(folder_path): 
    folder = Path(folder_path) 
    if not folder.exists(): 
        return {}, 0 
    html_files = list(folder.glob("*.html")) 
    mp_quotes = defaultdict(list) 
    global_speech_id = 0 
    
    for file_path in html_files: 
        sitting_date = extract_sitting_date(file_path) 
        try: 
            with open(file_path, "r", encoding="utf-8", errors="replace") as f: 
                soup = BeautifulSoup(f, "html.parser") 
        except Exception: 
            continue 
            
        speech_number_in_file = 0 
        
        # --- NEW: Track the absolute sentence count from the top of this file ---
        file_sentence_counter = 0 
        
        for tag in soup.find_all("strong"): 
            speaker_name = clean_speaker_name(tag.get_text(" ", strip=True)) 
            if not valid_name_pattern.match(speaker_name): 
                continue 
            speech_parts = [] 
            for sibling in tag.next_siblings: 
                if getattr(sibling, "name", None) == "strong": 
                    break 
                if isinstance(sibling, str): 
                    text = sibling.strip() 
                elif hasattr(sibling, "get_text"): 
                    text = sibling.get_text(" ", strip=True) 
                else: 
                    text = "" 
                if text: 
                    speech_parts.append(text) 
            full_speech = re.sub(r"\s+", " ", " ".join(speech_parts)).strip() 
            if not full_speech: 
                continue 
                
            # Break this speech turn into sentences to see how long it is
            speech_sentences = split_into_sentences(full_speech)
            speech_length = len(speech_sentences)
            
            # The start position is the current file count, the end is after this speech
            start_sentence_in_file = file_sentence_counter + 1
            end_sentence_in_file = file_sentence_counter + speech_length
            
            # Update our master counter for the file before moving to the next speaker
            file_sentence_counter += speech_length
            
            speech_number_in_file += 1 
            global_speech_id += 1 
            
            mp_quotes[speaker_name].append({ 
                "speech_id": global_speech_id, 
                "original_speech": full_speech, 
                "speaker": speaker_name, 
                "file": file_path.name, 
                "date": sitting_date, 
                "speech_number_in_file": speech_number_in_file,
                # --- NEW: Store where this speech sits in the overall file timeline ---
                "start_sentence_global": start_sentence_in_file,
                "end_sentence_global": end_sentence_in_file
            }) 
    return mp_quotes, global_speech_id 

import zipfile
import time
import urllib.request

@st.cache_resource
def download_and_unzip_archive():
    zip_path = Path("hansard_files.zip")
    extract_folder = Path("./hansard_files")
    
    # If the folder doesn't exist yet, fetch it from your secure Catbox upload link
    if not extract_folder.exists():
        url = "https://files.catbox.moe/ab4mla.zip"
        
        try:
            # Add a browser mask (User-Agent) so Catbox doesn't block the connection!
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            request_object = urllib.request.Request(url, headers=headers)
            
            # Open the URL to check the file size
            with urllib.request.urlopen(request_object) as response:
                # Get the total file size from the cloud server headers
                total_size = int(response.headers.get('content-length', 0))
                
                # Create clean placeholders in Streamlit for our text and progress bar
                status_text = st.empty()
                progress_bar = st.progress(0)
                
                start_time = time.time()
                bytes_downloaded = 0
                chunk_size = 1024 * 64  # Download 64 KB chunks at a time
                
                # Fetch and save the raw archive bytes smoothly with a timer
                with open(zip_path, 'wb') as out_file:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        out_file.write(chunk)
                        bytes_downloaded += len(chunk)
                        
                        # Calculate elapsed time and download progress percentages
                        elapsed_time = time.time() - start_time
                        
                        if total_size > 0:
                            percent = bytes_downloaded / total_size
                            progress_bar.progress(percent)
                            
                            # Estimate the total time remaining (ETA)
                            speed = bytes_downloaded / elapsed_time if elapsed_time > 0 else 1
                            remaining_bytes = total_size - bytes_downloaded
                            eta = remaining_bytes / speed
                            
                            # Show a beautiful, clean message that updates live
                            status_text.text(
                                f"📥 Downloading 173 Hansard documents... "
                                f"{int(percent * 100)}% complete | "
                                f"Elapsed: {int(elapsed_time)}s | "
                                f"Estimated remaining: {int(eta)}s"
                            )
                        else:
                            # Fallback text if the server doesn't provide a file size
                            status_text.text(f"📥 Downloading... Saved {bytes_downloaded // 1024} KB (Elapsed: {int(elapsed_time)}s)")

                # Clean up the status messages once download finishes successfully
                status_text.text("📦 Unpacking zip files into memory...")
                progress_bar.empty()
                    
                # Safely extract your 174 documents into web memory
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(".")
                if zip_path.exists():
                    os.remove(zip_path)
                    
                status_text.success(" 173 Hansard files successfully downloaded.")
                
        except Exception as e:
            st.error(f"⚠️ Cloud file extraction sync failed. System error details: {e}")
            st.stop()

# Turn on the cloud file unpacking engine right here
download_and_unzip_archive()
# -------------------------------------------------------------
# Read and parse the downloaded Hansard files.
FOLDER_PATH = "./hansard_files"
with st.spinner("🔄 Reading and parsing your 174 documents automatically... Please wait."):
    quotes_database, total_records = process_all_files(FOLDER_PATH)

if not quotes_database:
    st.error(f"Could not find any HTML files in {FOLDER_PATH}. Please check your folder structure.")
    st.stop()

import time  # Make sure this is imported to handle the 2-second delay

# 1. Create an empty container placeholder
banner_placeholder = st.empty()

# 2. Put your success alert message inside it
banner_placeholder.success(f" Analyzing {total_records} speeches")

# 3. Tell the app to wait for exactly 2 seconds
time.sleep(1)

# 4. Completely wipe the banner from the screen!
banner_placeholder.empty()
# --- UI SIDEBAR FILTER PANEL ---

st.sidebar.header(" Filter Options")
search_keyword = st.sidebar.text_input("Enter search keywords (comma separated):", value="")
filter_mp = st.sidebar.selectbox("Filter by Specific MP Name:", ["All"] + sorted(list(quotes_database.keys())))
filter_gender = st.sidebar.selectbox("Filter by Gender:", ["All", "Male", "Female"])
filter_ethnicity = st.sidebar.selectbox("Filter by Ethnicity:", ["All", "Chinese", "Malay", "Indian", "Other"])
filter_type = st.sidebar.selectbox("Filter by Position (MP Type):", ["All", "MP", "NCMP", "NMP"])
context_before = st.sidebar.slider("Sentences before keyword:", 0, 5, 2)
context_after = st.sidebar.slider("Sentences after keyword:", 0, 5, 2)
show_full = False

# --- FILTER LOGIC ---

def passes_filters(name):
    meta = mp_metadata.get(name, {})
    if filter_gender != "All" and meta.get("gender") != filter_gender:
        return False
    if filter_ethnicity != "All" and meta.get("ethnicity") != filter_ethnicity:
        return False
    if filter_type != "All" and meta.get("mp_type") != filter_type:
        return False
    if filter_mp != "All" and name != filter_mp:
        return False
    return True

# --- SEARCH ENGINE EXECUTION ---

grand_total_hits = 0
all_export_rows = []

# Clean dictionary to bundle separate speeches together by (Speaker + Date)
grouped_results = {}

if search_keyword:
    keywords = [kw.strip() for kw in search_keyword.split(",") if kw.strip()]
    sorted_keywords = sorted(keywords, key=len, reverse=True)
    if keywords:
        kw_pattern = re.compile(r"(?i)\b(" + "|".join(re.escape(k) for k in sorted_keywords) + r")\b")
        for mp, speeches in quotes_database.items():
            if not passes_filters(mp):
                continue
            for record in speeches:
                text = record["original_speech"]
                fresh_hits = len(kw_pattern.findall(text))  
                if fresh_hits == 0:
                    continue
                grand_total_hits += fresh_hits
                sentences = split_into_sentences(text)
                
                # --- Snippet window creator --- 
                display_segments = []  
                context_snippet = ""
                
                if show_full: 
                    display_segments.append(text)
                    context_snippet = text
                else: 
                    match_indices = [idx for idx, s in enumerate(sentences) if kw_pattern.search(s)] 
                    ranges = [] 
                    for idx in match_indices:
                        ranges.append([max(0, idx - context_before), min(len(sentences), idx + context_after + 1)]) 
                    
                    merged = [] 
                    for start, end in ranges: 
                        # Crucial [1] fix ensures numbering intervals are mathematically valid!
                        if not merged or start > merged[-1][1]: 
                            merged.append([start, end]) 
                        else: 
                            merged[-1][1] = max(merged[-1][1], end) 
                    
                    base_offset = record.get("start_sentence_global", 1) - 1
                    
                    snippet_parts = []
                    for start, end in merged:
                        #  THE FIX: We use 'segment_text' here so it never overwrites the tracker!
                        segment_text = " ".join(sentences[start:end]).strip()
                        segment_text = segment_text.lstrip(":")
                        
                        true_start = base_offset + start + 1
                        true_end = base_offset + end
                        
                        # Only display if we successfully extracted text characters
                        if segment_text:
                            display_segments.append(f"<i><b>[Document Sentences {true_start}–{true_end}]:</b></i> " + segment_text)
                            snippet_parts.append(segment_text)
                        
                    context_snippet = " | ".join(snippet_parts)

                # --- GROUPING MECHANISM BY SPEAKER AND DATE ---
                group_key = (mp, str(record["date"]))
                
                if group_key not in grouped_results:
                    grouped_results[group_key] = {
                        "mp": mp,
                        "date": str(record["date"]),
                        "file": record["file"],
                        "hits": fresh_hits,
                        "segments": display_segments,
                        "full_speech": text,
                        "snippets_for_excel": [context_snippet]
                    }
                else:
                    grouped_results[group_key]["hits"] += fresh_hits
                    grouped_results[group_key]["segments"].extend(display_segments)
                    grouped_results[group_key]["snippets_for_excel"].append(context_snippet)

        # --- FINAL PROCESSING STEP: Package the grouped data back into your app loops ---
        results_container = []
        for key, data in grouped_results.items():
            mp, speech_date = key
            meta = mp_metadata.get(mp, {})
            
            combined_excel_snippet = " || ".join(data["snippets_for_excel"])
            
            all_export_rows.append({
                "Speaker": mp,
                "Gender": meta.get("gender", "Unknown"),
                "Ethnicity": meta.get("ethnicity", "Unknown"),
                "MP Type": meta.get("mp_type", "Unknown"),
                "Date": speech_date,
                "File Source": data["file"],
                "Extracted Context Window": combined_excel_snippet
            })
            
            results_container.append(data)
            results_container.sort(key=lambda x: (x['hits'], x['date']), reverse=True)
            



# --- MAIN DISPLAY METRIC ---

st.metric(label="Total Keyword Matches Found", value=grand_total_hits)

# --- STEP 5: TABS GENERATION (Search vs Data Analytics) ---
tab_search, tab_analytics = st.tabs([" Search Results", " Analytical Dashboard"])

with tab_search:
    if 'results_container' not in locals():
        results_container = []
    if 'all_export_rows' not in locals():
        all_export_rows = []
    if results_container:
        st.subheader(f"Found {grand_total_hits} mentions across {len(results_container)} matching speeches")
        st.write("---")
        
        # 1. (Keep your speech expander displaying loop here...)
    
            # [... your existing expander display loop ...]
                    # Make sure your display loop looks like this and doesn't just say 'pass':
        for item in results_container:
            meta_info = mp_metadata.get(item['mp'], {})
            with st.expander(f" {item['mp']} ({meta_info.get('mp_type', 'Unknown')}) — {item['date']} ({item['hits']} hits)"):
                st.caption(f" Source File: {item['file']}")
                if show_full:
                    highlighted_full = kw_pattern.sub(r'<span style="color: #000000; font-weight: bold;">\1</span>', item["full_speech"])
                    st.markdown(highlighted_full, unsafe_allow_html=True)
                else:
                    for seg in item["segments"]:
                        highlighted_text = kw_pattern.sub(r'<span style="color: #000000; font-weight: bold;">\1</span>', seg)
                        st.markdown(highlighted_text, unsafe_allow_html=True)

            
        st.write("---")
        
        # 2. CONVERT TO DATAFRAME
        df_export = pd.DataFrame(all_export_rows)
        
        # 3. USE AN IN-MEMORY BYTES STREAM TO GENERATE A REAL EXCEL FILE (.xlsx)
        import io
        buffer = io.BytesIO()
        
        # Create an Excel writer with the xlsxwriter design engine
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_export.to_excel(writer, sheet_name='Search Results', index=False)
            
            # Access the underlying workbook sheet rules
            worksheet = writer.sheets['Search Results']
            
            # loop through each column, measure the longest text, and auto-adjust the width!
            for idx, col in enumerate(df_export.columns):
                # Find length of longest string item in the column or the header name itself
                max_len = max(df_export[col].astype(str).map(len).max(), len(col))
                # Set column width with a little bit of breathing room padding (+3)
                worksheet.set_column(idx, idx, max_len + 3)
                
        # 4. DOWNLOAD THE FULLY STYLED REAL EXCEL FILE
                # 1. Inject custom styles to override the red theme color entirely
        st.markdown("""
            <style>
            div[data-testid="stDownloadButton"] button {
                background-color: #84C76F !important; /* Official Excel Green */
                color: black !important;              /* Clean white text */
                font-weight: bold !important;         /* Bold typography */
                border: none !important;              /* Remove default borders */
                padding: 10px 24px !important;        /* Give it some nice padding */
                border-radius: 6px !important;        /* Smooth, modern rounded corners */
                box-shadow: 0px 2px 5px rgba(0,0,0,0.15) !important; /* Soft depth shadow */
            }
            div[data-testid="stDownloadButton"] button:hover {
                background-color: #659654 !important; /* Darker green on mouse hover */
                color: white !important;
                cursor: pointer;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # 2. Your download button code (make sure type="primary" is removed!)
        st.download_button(
            label="Download Search Results as Excel Spreadsheet (.xlsx)",
            data=buffer.getvalue(),
            file_name=f"hansard_search_{search_keyword.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="hansard_tab_download_btn"
        )



    else:
        st.warning("⚠️ No matches found matching your keyword and filter criteria.")

with tab_analytics:
    st.subheader(" Keyword Demographics & Volume Trends")
    if all_export_rows:
        df_analytics = pd.DataFrame(all_export_rows)
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Top Speakers Talking About This Topic")
            speaker_counts = df_analytics["Speaker"].value_counts()
            st.bar_chart(speaker_counts)
            
            st.write("### Breakdown by Position Type")
            type_counts = df_analytics["MP Type"].value_counts()
            st.bar_chart(type_counts)
            
        with col2:
            st.write("### Ethnic Breakdown")
            eth_counts = df_analytics["Ethnicity"].value_counts()
            st.bar_chart(eth_counts)
            
            st.write("### Gender Distribution")
            gender_counts = df_analytics["Gender"].value_counts()
            st.bar_chart(gender_counts)
            

    else:
        st.info("Analytics charts will automatically draw themselves here as soon as you get matching keyword results!")
