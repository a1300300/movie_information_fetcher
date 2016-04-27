"""
1.	Fetch movie information form website http://www.the-numbers.com
    in the range of specified years
2.  Movie data will be stored in directories arranged by years with Html format
"""
import urllib2
import re


def get_moive_info(start_year, end_year, dir_path):
    years = []
    for i in range(start_year, end_year + 1):
        years.append(str(i))
    for each_year in years:
        try:
            year_link = "http://www.the-numbers.com/movies/year/" + each_year
            resp = urllib2.urlopen(year_link).read()
            #from each year get links for all movies
            results = re.findall(r'/movie/(.*)#tab=summary', resp)

            for each_movie in results:
                movie_link = "http://www.the-numbers.com/movie/" + each_movie + "#tab=summary"
                #get html source code from the link
                resp = urllib2.urlopen(movie_link).read()
                #path to save file
                save = dir_path + "/" + each_year + "/" + each_movie + ".html"
                store = open(save, 'w')
                store.write(str(resp))
                store.close()
                print 'Produce ' + save + 'Success!'

        except Exception as e:
            print(str(e))

get_moive_info(1990, 2015, './years')
