import streamlit as st
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd


# this function for the getting inforamtion of the web page
def get_paperinfo(paper_url, headers):

  #download the page
  response=requests.get(paper_url,headers=headers)

  # check successful response
  if response.status_code != 200:
    print('Status code:', response.status_code)
    raise Exception('Failed to fetch web page ')

  #parse using beautiful soup
  paper_doc = BeautifulSoup(response.text,'html.parser')
  for div in paper_doc.find_all("div", {'class':'gs_ggs gs_fl'}): 
    div.decompose()

  return paper_doc

# this function for the extracting information of the tags
def get_tags(doc):
  paper_tag = doc.select('[data-lid]')
  # cite_tag = doc.select('[title=Cite] + a')
  cite_tag = doc.find_all('div', {"class": "gs_fl"})
  link_tag = doc.find_all('h3',{"class" : "gs_rt"})
  author_tag = doc.find_all("div", {"class": "gs_a"})

  return paper_tag,cite_tag,link_tag,author_tag

# it will return the title of the paper
def get_papertitle(paper_tag):
  
  paper_names = []
  
  for tag in paper_tag:
    paper_names.append(tag.select('h3')[0].get_text())

  return paper_names

# it will return the number of citation of the paper
def get_citecount(cite_tag):
  cite_count = []
  for i in cite_tag:
    cite = i.text
    tmp = re.findall('Cited by[ ]\d+', cite)
    if tmp:
      cite_count.append(tmp[0])
    else:
      cite_count.append(0)

  return cite_count

# function for the getting link information
def get_link(link_tag):

  links = []

  for i in range(len(link_tag)) :
    if link_tag[i].a:  
      links.append(link_tag[i].a['href']) 
    else:
      links.append(None)

  return links 

# function for the getting autho , year and publication information
def get_author_year_publi_info(authors_tag):
  years = []
  publication = []
  authors = []
  for i in range(len(authors_tag)):
      authortag_text = (authors_tag[i].text).split()
      # year = int(re.search(r'\d+', authors_tag[i].text).group())
      # years.append(year)
      
      input_text_year = " ".join(authors_tag[i].text.split()[-3:])
      datesearch = re.findall("(19\d{2}|20\d{2})", input_text_year)
      if len(datesearch) > 0:
        year = int(datesearch[len(datesearch)-1])
        years.append(year)
      else:
        year = 0
        years.append(year)
      publication.append(authortag_text[-1])
      author = authortag_text[0] + ' ' + re.sub(',','', authortag_text[1])
      authors.append(author)
  
  return years , publication, authors

def cite_number(text):
  if text != 0:
    result = text.split()[-1]
  else:
    result = str(text)
  return result

@st.cache_data
def convert_df(df):
  # IMPORTANT: Cache the conversion to prevent computation on every rerun
  return df.to_csv().encode('utf-8')



