import streamlit as st
import requests
import urllib
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from time import sleep
import plotly.express as px
from function import get_paperinfo, get_tags, get_papertitle, get_citecount, get_link, get_author_year_publi_info, cite_number

# title
st.markdown("""
# Scholar Scrap
Scraping relevant information of research papers from Google Scholar.
""")

# scraping function
# creating final repository
paper_repos_dict = {
                    'Paper Title' : [],
                    'Year' : [],
                    'Author' : [],
                    'Citation' : [],
                    'Publication' : [],
                    'Url of paper' : [] }

# adding information in repository
def add_in_paper_repo(papername,year,author,cite,publi,link):
  paper_repos_dict['Paper Title'].extend(papername)
  paper_repos_dict['Year'].extend(year)
  paper_repos_dict['Author'].extend(author)
  paper_repos_dict['Citation'].extend(cite)
  paper_repos_dict['Publication'].extend(publi)
  paper_repos_dict['Url of paper'].extend(link)
  for i in paper_repos_dict.keys():
    print(i,": ", len(paper_repos_dict[i]))
    print(paper_repos_dict[i])
  df = pd.DataFrame(paper_repos_dict)
  
  return df

# headers
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
url_begin = 'https://scholar.google.com/scholar?start={}&q='
url_end = '&hl=en&as_sdt=0,5='
# input
text_input = st.text_input("Search in Google Scholar", placeholder="What are you looking for?")
total_to_scrap = st.slider("How many pages to scrap?", min_value=1, max_value=5, step=1, value=2)
# create scholar url
if text_input:
    text_formated = "+".join(text_input.split())
    input_url = url_begin+text_formated+url_end
    if input_url:
        response=requests.get(input_url,headers=headers)
        # st.info(input_url)
        total_papers = 10 * total_to_scrap
        for i in range (0,total_papers,10):
            # get url for the each page
            url = input_url.format(i)
            # function for the get content of each page
            doc = get_paperinfo(url, headers)

            # function for the collecting tags
            paper_tag,cite_tag,link_tag,author_tag = get_tags(doc)

            # paper title from each page
            papername = get_papertitle(paper_tag)

            # year , author , publication of the paper
            year , publication , author = get_author_year_publi_info(author_tag)

            # cite count of the paper 
            cite = get_citecount(cite_tag)

            # url of the paper
            link = get_link(link_tag)

            # add in paper repo dict
            final = add_in_paper_repo(papername,year,author,cite,publication,link)

            # use sleep to avoid status code 429
            # sleep(10)
        final['Year'] = final['Year'].astype('int')
        final['Citation'] = final['Citation'].apply(cite_number).astype('int')
        with st.expander("Extracted papers"):
          st.dataframe(final)

        fig = px.scatter(
              final, 
              x="Year", 
              y="Citation", 
              color="Publication",
              size="Citation", 
              log_x=True, 
              size_max=60
              )

        with st.expander("Distribution of papers by year and citation", expanded=True):
          st.plotly_chart(fig, theme="streamlit", use_container_width=True)
        