import streamlit as st
import requests
import urllib
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from time import sleep
import plotly.express as px
from function import get_paperinfo, get_tags, get_papertitle, get_citecount, get_link, get_author_year_publi_info, cite_number, convert_df

st.set_page_config(page_title="Scholar Scrap", layout="wide")
html_temp = """
                    <div style="background-color:{};padding:1px">
                    
                    </div>
                    """

with st.sidebar:
    st.markdown("""
    # About
    A tool to extract relevant information of research papers from Google Scholar based on user input. 
    """)
    
    st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"),unsafe_allow_html=True)
    st.markdown("""
    # How does it work?
    Enter your keywords in the text field and select how many pages to scrap from Google Scholar results.  
    """)

    st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"),unsafe_allow_html=True)
    st.markdown("""
    Made by [@nainia_ayoub](https://twitter.com/nainia_ayoub) 
    """)

hide="""
<style>
footer{
	visibility: hidden;
    	position: relative;
}
.viewerBadge_container__1QSob{
    visibility: hidden;
}

<style>
"""
st.markdown(hide, unsafe_allow_html=True)

# title
st.markdown("""
## Scholar Scrap
Scraping relevant information of research papers from Google Scholar.
""")



# scraping function
# creating final repository
paper_repos_dict = {
                    'Paper Title' : [],
                    'Year' : [],
                    'Author' : [],
                    'Citation' : [],
                    'Publication site' : [],
                    'Url of paper' : [] }

# adding information in repository
def add_in_paper_repo(papername,year,author,cite,publi,link):
  paper_repos_dict['Paper Title'].extend(papername)
  paper_repos_dict['Year'].extend(year)
  paper_repos_dict['Author'].extend(author)
  paper_repos_dict['Citation'].extend(cite)
  paper_repos_dict['Publication site'].extend(publi)
  paper_repos_dict['Url of paper'].extend(link)
#   for i in paper_repos_dict.keys():
#     print(i,": ", len(paper_repos_dict[i]))
#     print(paper_repos_dict[i])
  df = pd.DataFrame(paper_repos_dict)
  
  return df

# headers
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
url_begin = 'https://scholar.google.com/scholar?start={}&q='
url_end = '&hl=en&as_sdt=0,5='
# input
col1, col2 = st.columns([3,1])
with col1:
  text_input = st.text_input("Search in Google Scholar", placeholder="What are you looking for?", disabled=False)
with col2:
  total_to_scrap = st.slider("How many pages to scrap?", min_value=1, max_value=5, step=1, value=2)

st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"),unsafe_allow_html=True)
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
            sleep(20)
		
        final['Year'] = final['Year'].astype('int')
        final['Citation'] = final['Citation'].apply(cite_number).astype('int')

        with st.expander("Extracted papers"):
          st.dataframe(final)
          csv = convert_df(final)
          file_name_value = "_".join(text_input.split())+'.csv'
          st.download_button(
              label="Download data as CSV",
              data=csv,
              file_name=file_name_value,
              mime='text/csv',
          )



        with st.expander("Distribution of papers by year and citation", expanded=True):
          size_button = st.checkbox('Set Citation as bubble size', value=True)
          size_value = None
          if size_button:
            size_value = 'Citation'
          final_sorted = final.sort_values(by='Year', ascending=True)
          fig = px.scatter(
                final_sorted, 
                x="Year", 
                color="Publication site",
                size=size_value, 
                log_x=True, 
                size_max=60
                )
          fig.update_xaxes(type='category')
          st.plotly_chart(fig, theme="streamlit", use_container_width=True)
        
