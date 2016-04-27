import urllib2
import re
import json
import mechanize
import pandas as pd
import os

br = mechanize.Browser()
br.set_handle_robots(False)
br.addheaders = [('User-agent', 'chrome')]

imdb_search_link = 'http://www.imdb.com/find?ref_=nv_sr_fn&s=tt&q='
google_serach_link = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q='


# input_file : input csv file
# output_path : the path to save tokens for each movie
def get_imdb_page(input_file, output_path):
    movie_data = pd.read_csv(input_file)
    index = 0
    for i in range(0, len(movie_data)):
        #make query for search: movie name + movie year + imdb
        movie_year = movie_data['Release Date'][i].split('-')[0]
        movie_name = movie_data['Movie Name'][i]
        movie_date = movie_data['Release Date'][i]

        output_filename = output_path + str(index) + '.html'
        if os.path.exists(output_filename):
            print output_filename, ' already exists!'
            index += 1
            continue

        imdb_query_string = movie_name
        encoded_imdb_query_string = urllib2.quote(imdb_query_string)
        google_query_string = movie_name + ' ' + movie_year + ' imdb'
        encoded_google_query_string = urllib2.quote(google_query_string)

        #try search on imdb first
        try:
            resp = str(br.open(imdb_search_link + encoded_imdb_query_string).read())
            movie_link = resp.split('<table class="findList">')[1].split('</table')[0]
            movie_link = re.search(r'(/title/tt\d{6,10}/\?ref_=fn_tt_tt_1)"', movie_link).group(1)
            imdb_link = 'http://www.imdb.com/' + movie_link
        #try google if failed
        except Exception as e:
            try:
                rawData = urllib2.urlopen(google_serach_link + encoded_google_query_string).read()
                jsonData = json.loads(rawData)
                searchResults = jsonData['responseData']['results']
                #Only get the first result's url link we need
                imdb_link = searchResults[0]['url']
            except Exception as e2:
                continue

        imdb_id = re.search(r'.*(tt\d{6,10}).*', imdb_link).group(1)
        imdb_plot_summary_link = 'http://www.imdb.com/title/' + imdb_id +'/plotsummary?ref_=tt_stry_pl'
        #try save page into html file in given folder
        try:
            htmltext = br.open(imdb_plot_summary_link).read()
            # resp2 = urllib2.urlopen(imdb_plot_summary_link).read()
            store = open(output_filename, 'w')
            store.write(str(htmltext))
            store.close()
            print ' Produce ' + output_filename + ' Success!'
        except Exception as e:
            print str(e)
        index += 1

get_imdb_page('./movies_1990-2015.csv', './IMDB_pages/')