#!/usr/bin/env python
# -*- coding: utf-8 -*-
#歧視無邊，回頭是岸。鍵起鍵落，情真情幻。

from lxml import html
import requests
import argparse

def retrieve_from_page(accept_lang='en-UK,en;q=0.8'):
    headers_once = {
        'Agent': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36',
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'en-UK,en;q=0.8'
    }
    headers_once['Accept-Language']=  accept_lang

    page = requests.get('http://www.google.com/advanced_search', headers=headers_once)
    tree = html.fromstring(page.text)

    #This will create a list of countries supported/listed in the menu with id "cr_menu":
    #CODE //ul[@id="cr_menu"]//li[@class="goog-menuitem" and contains(@value,"country")]/@value
    #NAME //ul[@id="cr_menu"]//li[@class="goog-menuitem" and contains(@value,"country")]/div/text()
    country_list = tree.xpath('''//ul[@id="cr_menu"]//li[@class="goog-menuitem" and contains(@value,"country")]/@value''')
    country_code = [x.replace('country','') for x in country_list]
    country_name = tree.xpath('''//ul[@id="cr_menu"]//li[@class="goog-menuitem" and contains(@value,"country")]//text()''')

    #This will create a list of languages supported/listed in the menu with id "lr_menu":
    #CODE //ul[@id="lr_menu"]//li[@class="goog-menuitem" and contains(@value,"lang")]/@value
    #NAME //ul[@id="lr_menu"]//li[@class="goog-menuitem" and contains(@value,"lang")]/div/text()
    lang_list = tree.xpath('''//ul[@id="lr_menu"]//li[@class="goog-menuitem" and contains(@value,"lang")]/@value''')
    lang_code = [x.replace('lang_','') for x in lang_list]
    lang_name = tree.xpath('''//ul[@id="lr_menu"]//li[@class="goog-menuitem" and contains(@value,"lang")]//text()''')

    return country_code, country_name, lang_code, lang_name

def export_to_xlsx_csv_tab(ex_dataframe, ex_filename):
    import csv
    ex_dataframe.to_excel(ex_filename+'.xlsx', sheet_name='Sheet1')
    ex_dataframe.to_csv(ex_filename+'.csv', sep=',', quoting=csv.QUOTE_ALL, na_rep='{na}',index=False, encoding='utf-8')
    ex_dataframe.to_csv(ex_filename+'.tab', sep='\t', quoting=csv.QUOTE_NONE, na_rep='{na}',index=False, encoding='utf-8')
    ex_dataframe.to_csv(ex_filename+'.tsv', sep='\t', quoting=csv.QUOTE_NONE, na_rep='{na}',index=False, encoding='utf-8')


def fetch_and_write(options):
    # Fetch the current country and language codes (including names in all supported languages) supported by Google's advance search
    import numpy as np
    import pandas as pd

    ccode, cname, lcode, lname=retrieve_from_page()

    df_country_google_integrated   = pd.DataFrame({  'geocode' : pd.Series(ccode),
                                        'geoname' : pd.Series(cname)
                                       })

    df_lang_google_integrated      = pd.DataFrame({  'langcode' : pd.Series(lcode),
                                        'langname' : pd.Series(lname)
                                       })

    lcode.remove('en')
    for l in lcode: # all or some [0:2] 
        ccode, cname, lcode, lname=retrieve_from_page(accept_lang='xx;q=0.8'.replace('xx',l))
        df_country_google_adding  = pd.DataFrame({  'geocode' : pd.Series(ccode),
                                            'geoname_xx'.replace('xx',l).replace('-','_') : pd.Series(cname)
                                           })

        df_lang_google_adding     = pd.DataFrame({  'langcode' : pd.Series(lcode),
                                            'langname_xx'.replace('xx',l).replace('-','_') : pd.Series(lname)
                                           })

        df_country_google_integrated    =pd.merge(df_country_google_integrated, df_country_google_adding,   on='geocode')
        df_lang_google_integrated       =pd.merge(df_lang_google_integrated,    df_lang_google_adding,      on='langcode')

    if options.outputpath:
        output_path = options.outputpath
    else:
        output_path =""

    import os  
    
    export_to_xlsx_csv_tab(df_country_google_integrated, os.path.join(output_path, 'country_google'))
    export_to_xlsx_csv_tab(df_lang_google_integrated, os.path.join(output_path, 'lang_google'))


    
    
    
    
######################       MAIN  ########################
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""Fetch the current country and language codes (including names in all supported languages) supported by Google's advance search""")
    parser.add_argument("-o", "--outputpath", dest="outputpath", default=".",
                        help="write data to OUTPUTPATH", metavar="OUTPUTPATH")

    args = parser.parse_args()
    
    fetch_and_write(args)

