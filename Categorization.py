from collections import defaultdict
import pandas as pd
director_dct = defaultdict(list)
producer_dct = defaultdict(list)
screenwriter_dct = defaultdict(list)
actor_dct = defaultdict(list)
franchise_dict = defaultdict(list)
production_com_dict = defaultdict(list)
distribution_com_dict = defaultdict(list)
MPAA_rating_dct = {'Not Rated': '0', 'G': '1', 'PG': '2', 'PG-13': '3', 'R': '4', 'NC-17': '5'}


def categorization(input, output, used_profit):
    movie_data = pd.read_csv(input)
    #Add a column called 'Profit' for Net Profit after total box office substract budget
    movie_data['Profit'] = 0

    for i in range(0, len(movie_data)):
        movie_name = movie_data['Movie Name'][i]

        #total box office
        the_budget = float(movie_data['Budget with inflation'][i])
        domestic_bo = movie_data['Domestic Box Office with inflation'][i]
        international_bo = movie_data['International Box Office with inflation'][i]
        if str(international_bo) == 'nan':
            international_bo = 0
        total_bo = float(domestic_bo) + float(international_bo)

        net_profit = total_bo - the_budget
        #add profit information to the 'Profit' column
        movie_data.loc[i, 'Profit'] = net_profit

        #add box office to list grouped by target's name for analysis
        #franchise
        franchise = movie_data['Franchise'][i]
        add_to_dict(franchise_dict, franchise, net_profit, 'No')

        #Production company
        production_com = movie_data['Production Company'][i]
        add_to_dict(production_com_dict, production_com, net_profit, 'nan')

        #Distribution company
        distribution_com = movie_data['Distribution Company'][i]
        add_to_dict(distribution_com_dict, distribution_com, net_profit, 'nan')

        #director
        director = movie_data['Director'][i]
        add_to_dict(director_dct, director, net_profit, 'nan')

        #producer1-4
        producer1 = movie_data['Producer1'][i]
        producer2 = movie_data['Producer2'][i]
        producer3 = movie_data['Producer3'][i]
        producer4 = movie_data['Producer4'][i]
        producer5 = movie_data['Producer5'][i]
        add_to_dict(producer_dct, producer1, net_profit, 'nan')
        add_to_dict(producer_dct, producer2, net_profit, 'nan')
        add_to_dict(producer_dct, producer3, net_profit, 'nan')
        add_to_dict(producer_dct, producer4, net_profit, 'nan')
        add_to_dict(producer_dct, producer5, net_profit, 'nan')

        #screenwriter
        screenwriter1 = movie_data['ScreenWriter1'][i]
        screenwriter2 = movie_data['ScreenWriter2'][i]
        screenwriter3 = movie_data['ScreenWriter3'][i]
        add_to_dict(screenwriter_dct, screenwriter1, net_profit, 'nan')
        add_to_dict(screenwriter_dct, screenwriter2, net_profit, 'nan')
        add_to_dict(screenwriter_dct, screenwriter3, net_profit, 'nan')

        #actor
        actor1 = movie_data['Actor1'][i]
        actor2 = movie_data['Actor2'][i]
        actor3 = movie_data['Actor3'][i]
        actor4 = movie_data['Actor4'][i]
        actor5 = movie_data['Actor5'][i]
        actor6 = movie_data['Actor6'][i]
        add_to_dict(actor_dct, actor1, net_profit, 'nan')
        add_to_dict(actor_dct, actor2, net_profit, 'nan')
        add_to_dict(actor_dct, actor3, net_profit, 'nan')
        add_to_dict(actor_dct, actor4, net_profit, 'nan')
        add_to_dict(actor_dct, actor5, net_profit, 'nan')
        add_to_dict(actor_dct, actor6, net_profit, 'nan')

        #G:1 PG:2 PG-13:3 G:4 NC-17:5
        mpaa = movie_data['MPAA Rating'][i]
        if str(mpaa) != 'nan':
            movie_data.loc[i, 'MPAA Rating'] = MPAA_rating_dct[str(mpaa)]

        # During summer
        # No: 0, Yes: 1
        during_summer = movie_data['During Summer'][i]
        if str(during_summer) == 'Yes':
            movie_data.loc[i, 'During Summer'] = 1
        elif str(during_summer) == 'No':
            movie_data.loc[i, 'During Summer'] = 0

        # In holiday
        # No: 0, in holiday: 1
        in_holiday = movie_data['In Holiday'][i]
        if str(in_holiday) == 'No':
            movie_data.loc[i, 'In Holiday'] = 0
        else:
            movie_data.loc[i, 'In Holiday'] = 1

        # Source
        # Original Screenplay to 0, to 1 for other
        film_source = movie_data['Source'][i]
        if str(film_source) == 'Original Screenplay':
            movie_data.loc[i, 'Source'] = 0
        else:
            movie_data.loc[i, 'Source'] = 1

        ##
        ##
        #categorize the director, producer, screenwriter, actor:
        #1. when they perform more than 4 movies whose net profit
        #   is larger than 50000000
        #2. when they perform 1 to 4 movies whose total box
        #   office is top 20%
        #3. when they perform 0 movies whose total box office is top 20%
        #   but at least 1 movie whose total box office is top 50%
        #4. when they perform 0 movies whose total box office is top 20%
        #   and 0 movies whose total box office is top 50%

        #production company
        categorize_based_on_profit(used_profit, production_com_dict, production_com, 'nan',
                                   'Production Company', i, movie_data)

        #distribution company
        categorize_based_on_profit(used_profit, distribution_com_dict, distribution_com, 'nan',
                                   'Distribution Company', i, movie_data)

        # franchise
        categorize_based_on_profit(used_profit, franchise_dict, franchise, 'No', 'Franchise', i, movie_data)

        # director
        categorize_based_on_profit(used_profit, director_dct, director, 'nan', 'Director', i, movie_data)

        # producer1-4
        categorize_based_on_profit(used_profit, producer_dct, producer1, 'nan', 'Producer1', i, movie_data)
        categorize_based_on_profit(used_profit, producer_dct, producer2, 'nan', 'Producer2', i, movie_data)
        categorize_based_on_profit(used_profit, producer_dct, producer3, 'nan', 'Producer3', i, movie_data)
        categorize_based_on_profit(used_profit, producer_dct, producer4, 'nan', 'Producer4', i, movie_data)
        categorize_based_on_profit(used_profit, producer_dct, producer5, 'nan', 'Producer5', i, movie_data)


        # screenwriter1-3
        categorize_based_on_profit(used_profit, screenwriter_dct,
                                       screenwriter1, 'nan', 'ScreenWriter1', i, movie_data)
        categorize_based_on_profit(used_profit, screenwriter_dct,
                                       screenwriter2, 'nan', 'ScreenWriter2', i, movie_data)
        categorize_based_on_profit(used_profit, screenwriter_dct,
                                       screenwriter3, 'nan', 'ScreenWriter3', i, movie_data)

        # actor1-6
        categorize_based_on_profit(used_profit, actor_dct, actor1, 'nan', 'Actor1', i, movie_data)
        categorize_based_on_profit(used_profit, actor_dct, actor2, 'nan', 'Actor2', i, movie_data)
        categorize_based_on_profit(used_profit, actor_dct, actor3, 'nan', 'Actor3', i, movie_data)
        categorize_based_on_profit(used_profit, actor_dct, actor4, 'nan', 'Actor4', i, movie_data)
        categorize_based_on_profit(used_profit, actor_dct, actor5, 'nan', 'Actor5', i, movie_data)
        categorize_based_on_profit(used_profit, actor_dct, actor6, 'nan', 'Actor6', i, movie_data)

    movie_data = movie_data.sort_values('Release Date').set_index('Release Date')
    movie_data.to_csv(output)


def add_to_dict(the_dist, target, net_profit, false_string):
    if str(target) != false_string:
        the_dist[target].append(net_profit)


def categorize_based_on_profit(target_profit, the_dist, target, false_string, column_name, the_index, data_frame):
    count = 0
    count2 = 0
    if false_string == "nan":
        if str(target) != false_string:
            the_dist_profit_list = the_dist.get(target)
            if the_dist_profit_list:
                for profit in the_dist_profit_list:
                    if profit >= target_profit:
                        count += 1
                    elif profit < 0:
                        count2 += 1
                if count > 4:
                    data_frame.loc[the_index, column_name] = 1
                elif 0 < count <= 4:
                    data_frame.loc[the_index, column_name] = 2
                elif count2 == 0:
                    data_frame.loc[the_index, column_name] = 3
                else:
                    data_frame.loc[the_index, column_name] = 4
    else:
        if str(target) != false_string:
            the_dist_profit_list = the_dist.get(target)
            if the_dist_profit_list:
                for profit in the_dist_profit_list:
                    if profit >= target_profit:
                        count += 1
                    elif profit < 0:
                        count2 += 1
                if count > 4:
                    data_frame.loc[the_index, column_name] = 1
                elif 0 < count <= 4:
                    data_frame.loc[the_index, column_name] = 2
                elif count2 == 0:
                    data_frame.loc[the_index, column_name] = 3
                else:
                    data_frame.loc[the_index, column_name] = 4
        else:
            data_frame.loc[the_index, column_name] = 0

categorization('./movies_1990-2015.csv', './movies_1990-2015_categorized.csv', 50000000)
