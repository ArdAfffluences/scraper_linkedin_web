# --- scraper_linkedin_web.py ---
# Script combiné : scrape LinkedIn (via Playwright) et sites web publics (via requests + BeautifulSoup)

import time
import csv
import requests
from bs4 import BeautifulSoup
import pandas as pd
from playwright.sync_api import sync_playwright
import streamlit as st

# --- FONCTION 1 : Scraper LinkedIn People Search ---
def scrape_linkedin(url, cookie):
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.add_cookies([{
            "name": "li_at",
            "value": cookie,
            "domain": ".linkedin.com",
            "path": "/"
        }])
        page = context.new_page()
        page.goto(url)
        page.wait_for_timeout(5000)

        profils = page.query_selector_all(".entity-result__title-text")
        for p in profils:
            results.append({"Profil": p.inner_text().strip()})
        browser.close()
    return results

# --- FONCTION 2 : Scraper un site web public ---
def scrape_public_web(url, nom_selector, email_selector):
    res = []
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        noms = soup.select(nom_selector)
        emails = soup.select(email_selector)

        for nom, email in zip(noms, emails):
            res.append({"Nom": nom.get_text(strip=True), "Email": email.get_text(strip=True)})
    except Exception as e:
        res.append({"Erreur": str(e)})
    return res

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="Scraper Leads", layout="centered")
st.title("🕵️ Scraper LinkedIn & Web Public")
st.markdown("Scraper simple pour extraire des leads depuis LinkedIn et n'importe quel site web.")

option = st.radio("Choisissez le type de scraping :", ("LinkedIn", "Web Public"))

if option == "LinkedIn":
    linkedin_url = st.text_input("🔗 URL LinkedIn Search", "https://www.linkedin.com/search/results/people/?keywords=marketing+manager")
    cookie = st.text_input("🔐 Cookie li_at (confidentiel)", type="password")

    if st.button("Lancer le scraping LinkedIn"):
        try:
            data = scrape_linkedin(linkedin_url, cookie)
            df = pd.DataFrame(data)
            st.dataframe(df)
            df.to_csv("linkedin_resultats.csv", index=False)
            st.success("Scraping terminé. Fichier enregistré sous linkedin_resultats.csv")
        except Exception as e:
            st.error(f"Erreur lors du scraping LinkedIn : {str(e)}")

elif option == "Web Public":
    public_url = st.text_input("🔗 URL du site ", "https://exemple.com/annuaire")
    nom_css = st.text_input("🧷 Sélecteur CSS du nom", ".nom")
    email_css = st.text_input("📧 Sélecteur CSS de l'email", ".email")

    if st.button("Lancer le scraping Web"):
        try:
            data = scrape_public_web(public_url, nom_css, email_css)
            df = pd.DataFrame(data)
            st.dataframe(df)
            df.to_csv("web_resultats.csv", index=False)
            st.success("Scraping terminé. Fichier enregistré sous web_resultats.csv")
        except Exception as e:
            st.error(f"Erreur lors du scraping Web : {str(e)}")
