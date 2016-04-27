"""
1.	Domestic box office income for American movies
    (data from boxofficemojo.com, www.the-numbers.com, etc)
2.	Name of Director, writer, main actor, main actress
    and production company(data from imdb.com, etc)
3.	Type of movie, sequel or not, budget of production,
    whether shown during a holiday
    (data from boxofficemojo.com, www.the-numbers.com, etc)
4.	(We plan to focus on) movies released during 1990-2015,
    box office >= $10,000,000; and box office > budget,
    (ignore movies that have missing information).
5.	The CPI (Consumer Price Index) will also be considered
    ( money value in 1990 and 2015 are different).
"""
import os
import re
import pandas as pd
import datetime
from datetime import datetime as dt
import urllib2

#inflation of each year compared to 2015
cpi = {'1990': 1.8134, '1991': 1.7402, '1992': 1.6894, '1993': 1.6403, '1994': 1.5993,
       '1995': 1.5552, '1996': 1.5106, '1997': 1.4767, '1998': 1.4541, '1999': 1.4227,
       '2000': 1.3764, '2001': 1.3383, '2002': 1.3175, '2003': 1.2881, '2004': 1.2547,
       '2005': 1.2136, '2006': 1.1757, '2007': 1.1431, '2008': 1.1009, '2009': 1.1048,
       '2010': 1.0870, '2011': 1.0537, '2012': 1.0323, '2013': 1.0174, '2014': 1.0012,
       '2015': 1.0}

#the date of thanks_giving and labor_day in each year from 1990 to 2015
labor_day = {'1990': '03', '1991': '02', '1992': '07', '1993': '06', '1994': '05',
       '1995': '04', '1996': '02', '1997': '01', '1998': '07', '1999': '06',
       '2000': '04', '2001': '03', '2002': '02', '2003': '01', '2004': '06',
       '2005': '05', '2006': '04', '2007': '03', '2008': '01', '2009': '07',
       '2010': '06', '2011': '05', '2012': '03', '2013': '02', '2014': '01',
       '2015': '07'}

thanks_giving = {'1990': '22', '1991': '28', '1992': '26', '1993': '25', '1994': '24',
       '1995': '23', '1996': '28', '1997': '27', '1998': '26', '1999': '25',
       '2000': '23', '2001': '22', '2002': '28', '2003': '27', '2004': '25',
       '2005': '24', '2006': '23', '2007': '22', '2008': '27', '2009': '26',
       '2010': '25', '2011': '24', '2012': '22', '2013': '28', '2014': '27',
       '2015': '26'}


month_table = {'January': '1', 'February': '2', 'March': '3', 'April': '4', 'May': '5', 'June': '6',
               'July': '7', 'August': '8', 'September': '9', 'October': '10', 'November': '11', 'December': '12'}


#weekly box office available date in each 7 days, append them to the list for searching
week_date_list = []
first_day = datetime.datetime.strptime("1990-01-05", '%Y-%m-%d')
last_day = datetime.datetime.strptime("2015-12-30", '%Y-%m-%d')
day = first_day
while day <= last_day:
    week_date_list.append(day)
    day = day + datetime.timedelta(days=7)


def fetch_movie_by_year(start_year, end_year, file_name, dir_path):
    df = pd.DataFrame(columns=['Release Date',
                               'Movie Name',
                               'MPAA Rating',
                               'Genre',
                               'Budget',
                               'Domestic Box Office',
                               'International Box Office',
                               'Budget with inflation',
                               'Domestic Box Office with inflation',
                               'International Box Office with inflation',
                               'Weekly Box Office1',
                               'Theater number1',
                               'Weekly Box Office per theater1',
                               'Change1',
                               'Weekly Box Office2',
                               'Theater number2',
                               'Weekly Box Office per theater2',
                               'Change2',
                               'Weekly Box Office3',
                               'Theater number3',
                               'Weekly Box Office per theater3',
                               'Change3',
                               'Weekly Box Office4',
                               'Theater number4',
                               'Weekly Box Office per theater4',
                               'Change4',
                               'During Summer',
                               'In Holiday',
                               'Franchise',
                               'Source',
                               'Production Company',
                               'Distribution Company',
                               'Director',
                               'Producer1',
                               'Producer2',
                               'Producer3',
                               'Producer4',
                               'Producer5',
                               'ScreenWriter1',
                               'ScreenWriter2',
                               'ScreenWriter3',
                               'Actor1',
                               'Actor2',
                               'Actor3',
                               'Actor4',
                               'Actor5',
                               'Actor6'])
    for this_year in range(start_year, end_year + 1):
        each_year = str(this_year)
        files = os.listdir(dir_path + each_year)
        for file in files[1:]:
            #initialization of list for each film process
            actors = ['NA', 'NA', 'NA', 'NA', 'NA', 'NA']
            producers = ['NA', 'NA', 'NA', 'NA', 'NA']
            screen_writers = ['NA', 'NA', 'NA']
            weekly_BO = ['NA', 'NA', 'NA', 'NA']
            theater_number =['NA', 'NA', 'NA', 'NA']
            weekly_BO_per_theater = ['NA', 'NA', 'NA', 'NA']
            weekly_BO_change = ['NA', 'NA', 'NA', 'NA']

            source = open(dir_path + each_year + '/' + file).read()

            movie_name = re.search(r'<h1 itemprop="name">(.*) \(.*\)</h1>', source).group(1)

            date = get_release_date(source, each_year, movie_name)
            if date is None:
                continue

            try:
                #change time format
                date = change_format(date)
            except Exception as e:
                #If the date only contain year, then assign the movie date with June 1st
                date = each_year + '-6-1'
            date_stamp = dt.strptime(date, '%Y-%m-%d')

            #check if during summer
            try:
                in_summer =check_if_in_summer(date_stamp)
            except Exception as e:
                in_summer = 'No'

            #check if in holiday
            try:
                in_holiday = check_if_in_holiday(date_stamp)
            except Exception as e:
                in_holiday = 'No'

            try:
                #filter domestic box office with condition < 10 million
                domestic_box_office = source.split('<td><b>Domestic Box Office</b></td>')[1]
                domestic_box_office = float(re.search(r'<td class="data">\$(.*)</td><td>',
                                              domestic_box_office).group(1)\
                                            .replace(',', ''))
                domestic_box_office_with_inflation = domestic_box_office * cpi[each_year]
                if domestic_box_office_with_inflation < 10000000:
                    continue
            except Exception as e:
                domestic_box_office = 'NA'
                domestic_box_office_with_inflation = 'NA'

            try:
                #filter international box office with condition < 10 million
                international_box_office = source.split('<td><b>International Box Office</b></td>')[1]
                international_box_office = float(re.search(r'<td class="data sum">\$(.*)</td><td>',
                                            international_box_office).group(1)\
                                                .replace(',', ''))
                international_box_office_with_inflation = international_box_office * cpi[each_year]
                if international_box_office_with_inflation < 10000000:
                    continue
            except Exception as e:
                international_box_office = 'NA'
                international_box_office_with_inflation ='NA'

            #find budget
            try:
                budget = float(source.split('Production&nbsp;Budget:</b></td><td>$')[1]\
                             .split('</td></tr>')[0]\
                             .replace(',', ''))
                budget_with_inflation = budget * cpi[each_year]
            except Exception as e:
                budget = 'NA'
                continue

            #check its weekend box office
            start_day = find_nearest_day(date_stamp)
            for i in range(4):
                try:
                    day_string = start_day.strftime("%Y/%m/%d")
                    the_number_link = 'http://www.the-numbers.com/box-office-chart/weekly/' + day_string

                    resp = urllib2.urlopen(the_number_link).read()
                    weekly_BO_source = re.search(r'(.*">' + movie_name[0:26] + '.*\n.*\n.*\n.*\n.*\n.*)\n', resp).group(1)
                    weekly_BO_source = weekly_BO_source.split('\n')
                    # Gross: weekly_BO_source[2]; Change: weekly_BO_source[3]
                    # Theater: weekly_BO_source[4]; BO per theater: weekly_BO_source[5]
                    weekly_BO[i] = float(weekly_BO_source[2].split('</td>')[0]
                                         .split('$')[1]
                                         .replace(',', '')) * cpi[each_year]
                    weekly_BO_change[i] = weekly_BO_source[3]\
                                            .split('</td>')[0]\
                                            .split('">')[1]\
                                            .replace('&nbsp;', '0%')
                    theater_number[i] = weekly_BO_source[4].split('</td>')[0]\
                                            .split('">')[1]\
                                            .replace(',', '')
                    weekly_BO_per_theater[i] = float(weekly_BO_source[5].split('</td>')[0]\
                                                .split('">$')[1]\
                                                .replace(',', '')) * cpi[each_year]

                    start_day = start_day + datetime.timedelta(days=7)
                except Exception as e:
                    weekly_BO[i] = 'NA'
                    weekly_BO_change[i] = 'NA'
                    theater_number[i] = 'NA'
                    weekly_BO_per_theater[i] = 'NA'
                    start_day = start_day + datetime.timedelta(days=7)



            #find the MPAA rating
            movie_mpaa = find_mpaa(source)

            #find Genre
            genre = find_genre(source)

            #production company
            production_company_name = find_production_company_name(source, movie_name)

            #distribution company
            distri_company_name = find_distri_company_name(movie_name)

            #find director
            director = find_director(source)

            #Franchise
            franchise = find_franchise(source)

            #film source
            film_source = find_film_source(source)

            #find 5 producers
            try:
                #find 5 producer
                producers_source = source.split('<h1>Production and Technical Credits</h1>')[1]\
                                    .split('</table>')[0]
                producers_source = re.findall(r'<td class="alnleft">.*Producer.*\n.*\n.*/person.*">(.*)</a></b></td>',
                                              producers_source)
                for i in range(len(producers_source)):
                    if i > 4:
                        break
                    producers[i] = producers_source[i].replace('</span>', '')
            except Exception as e:
                producers[0] = 'NA'
                producers[1] = 'NA'
                producers[2] = 'NA'
                producers[3] = 'NA'
                producers[4] = 'NA'

            #find screenwriter
            try:
                screenwriter_source = source.split('<h1>Production and Technical Credits</h1>')[1]\
                                    .split('</table>')[0]
                screenwriter_source = re.findall(r'<td class="alnleft">.*Screenwriter.*\n.*\n.*/person.*">(.*)</a></b></td>',
                                              screenwriter_source)
                for i in range(len(screenwriter_source)):
                    if i > 2:
                        break
                    screen_writers[i] = screenwriter_source[i].replace('</span>', '')
            except Exception as e:
                screen_writers[0] = 'NA'
                screen_writers[1] = 'NA'
                screen_writers[2] = 'NA'

            #find main five actor/actress
            try:
                actors_source = source.split('<h1>Cast</h1>')[1]\
                                .split('<h1>Production and Technical Credits</h1>')[0]
                actors_source = re.findall(r'<a href="/person/.*">(.*)</a></b></td>', actors_source)
                for i in range(len(actors_source)):
                    if i > 5:
                        break
                    actors[i] = actors_source[i].replace('</span>', '').replace(',', '`')

            except Exception as e:
                actors[0] = 'NA'
                actors[1] = 'NA'
                actors[2] = 'NA'
                actors[3] = 'NA'
                actors[4] = 'NA'
                actors[5] = 'NA'

            df = df.append({'Release Date': date_stamp,
                            'Movie Name': movie_name,
                            'MPAA Rating': movie_mpaa,
                            'Genre': genre,
                            'Budget': budget,
                            'Domestic Box Office': domestic_box_office,
                            'International Box Office': international_box_office,
                            'Budget with inflation': budget_with_inflation,
                            'Domestic Box Office with inflation': domestic_box_office_with_inflation,
                            'International Box Office with inflation': international_box_office_with_inflation,
                            'Weekly Box Office1': weekly_BO[0],
                            'Theater number1': theater_number[0],
                            'Weekly Box Office per theater1': weekly_BO_per_theater[0],
                            'Change1': weekly_BO_change[0],
                            'Weekly Box Office2': weekly_BO[1],
                            'Theater number2': theater_number[1],
                            'Weekly Box Office per theater2': weekly_BO_per_theater[1],
                            'Change2': weekly_BO_change[1],
                            'Weekly Box Office3': weekly_BO[2],
                            'Theater number3': theater_number[2],
                            'Weekly Box Office per theater3': weekly_BO_per_theater[2],
                            'Change3': weekly_BO_change[2],
                            'Weekly Box Office4': weekly_BO[3],
                            'Theater number4': theater_number[3],
                            'Weekly Box Office per theater4': weekly_BO_per_theater[3],
                            'Change4': weekly_BO_change[3],
                            'During Summer': in_summer,
                            'In Holiday': in_holiday,
                            'Franchise': franchise,
                            'Source': film_source,
                            'Production Company': production_company_name,
                            'Distribution Company': distri_company_name,
                            'Director': director,
                            'Producer1': producers[0],
                            'Producer2': producers[1],
                            'Producer3': producers[2],
                            'Producer4': producers[3],
                            'Producer5': producers[4],
                            'ScreenWriter1': screen_writers[0],
                            'ScreenWriter2': screen_writers[1],
                            'ScreenWriter3': screen_writers[2],
                            'Actor1': actors[0],
                            'Actor2': actors[1],
                            'Actor3': actors[2],
                            'Actor4': actors[3],
                            'Actor5': actors[4],
                            'Actor6': actors[5]}, ignore_index=True)

    df = df.sort_values('Release Date').set_index('Release Date')
    df.to_csv(file_name)


def get_release_date(source, each_year, movie_name):
    try:
        #find domestic release date
        date = source.split('Domestic Releases:</b></td>\n<td>')[1]
        date = re.search(r'(.{3,12} \d{1,2}\D{1,2}, \d{4})', date).group(0)
        if date.split(' ')[2] != each_year:
            return None
        return date
    except Exception as e:
        try:
            wiki_name = movie_name.replace(' ', '_')
            wiki_link = 'https://en.wikipedia.org/wiki/' + wiki_name
            resp = urllib2.urlopen(wiki_link).read()
            date = re.search(r'li>(.{3,12}&#160;\d{1,2},&#160;\d{4})', resp).group(1)
            date = date.replace('&#160;', ' ')
            return date
        except Exception as ee:
            return None

def change_format(date):
    month = month_table[date.split(' ')[0]]
    day = date.split(' ')[1].replace('th,', '')\
                            .replace('st,', '')\
                            .replace('nd,', '')\
                            .replace('rd,', '')\
                            .replace(',', '')
    year = date.split(' ')[2]
    return year + '-' + month + '-' + day


def check_if_in_summer(date_stamp):
    for i in range(31):
        day = date_stamp + datetime.timedelta(days=i)
        m = day.strftime('%m')
        if m in ['06', '07', '08']:
            return 'Yes'
            break
    return 'No'


def check_if_in_holiday(date_stamp):
    #check Christmas and NewYear
    for i in range(31):
        day = date_stamp + datetime.timedelta(days=i)
        if day.strftime('%m-%d') in ['12-24', '12-25']:
            return 'Christmas'
        elif day.strftime('%m-%d') in ['12-31', '1-1']:
            return 'New Year'

        #check Thanksgiving
        date_string = day.strftime('%Y-%m-%d')
        year = date_string.split('-')[0]
        day = thanks_giving[year]
        if year + '-11-' + day == date_string:
            return 'Thanks Giving'

        #check labor day
        day = labor_day[year]
        if year + '-09-' + day == date_string:
            return 'Labor Day'

    return 'No'


def find_nearest_day(date_stame):
    min_day = 100
    start_day = last_day
    for i in week_date_list:
        if abs(int((date_stame - i).days)) < min_day:
            min_day = abs(int((date_stame - i).days))
            start_day = i
    return start_day


def find_mpaa(source):
    try:
        movie_mpaa = source.split('<tr><td><b>MPAA&nbsp;Rating:</b></td>')[1]
        movie_mpaa = re.search(r'<td>.*">(.*)</a>', movie_mpaa).group(1)
    except Exception as e:
        movie_mpaa = 'NA'
    return movie_mpaa


def find_genre(source):
    try:
        genre = source.split('Genre:</b></td><td>')[1]
        genre = re.search(r'<.*>(.*)</a></td></tr>', genre).group(1)

    except Exception as e:
        genre = 'NA'
    return genre


def find_production_company_name(source, movie_name):
    try:
        production_company_name = source.split('<tr><td><b>Production Companies:</b></td>')[1]
        production_company_name = re.search(r'<a href=.*>(.*)</a>', production_company_name).group(1)
    except Exception as e:
        try:
            wiki_name = movie_name.replace(' ', '_')
            wiki_link = 'https://en.wikipedia.org/wiki/' + wiki_name
            resp = urllib2.urlopen(wiki_link).read()
            production_company_name = str(resp).split('Production<br />\ncompany</div>')[1]
            production_company_name = re.search(r'<a href.*>(.*)</a>', production_company_name).group(1)
        except Exception as e:
            production_company_name = 'NA'
    return production_company_name


def find_distri_company_name(movie_name):
    try:
        wiki_name = movie_name.replace(' ', '_')
        wiki_link = 'https://en.wikipedia.org/wiki/' + wiki_name
        resp = urllib2.urlopen(wiki_link).read()
        distri_company_name = str(resp).split('>Distributed by</th>')[1]
        distri_company_name = re.search(r'<td style=".*">(.*)</a></td>', distri_company_name).group(1)
        if len(distri_company_name) > 40:
            distri_company_name = 'NA'
    except Exception as e:
        distri_company_name = 'NA'
    return distri_company_name


def find_director(source):
    try:
        #find director
        director = source.split('itemprop="director"')[1]\
                        .split('<span itemprop="name">')[1]\
                        .split('</span></a></b></td>')[0]
    except Exception as e:
        director = 'NA'
    return director


def find_franchise(source):
    try:
        franchise = re.search(r'<a href="/movies/franchise/.*">(.*)</a>', source).group(1)
    except Exception as e:
        franchise = 'No'
    return franchise


def find_film_source(source):
    try:
        film_source = re.search(r'<td><b>Source:</b></td>.*">(.*)</a>', source).group(1)
    except Exception as e:
        film_source = 'Original Screenplay'
    return film_source

fetch_movie_by_year(1990, 2016, './movies_1990-2015.csv', './years/')
