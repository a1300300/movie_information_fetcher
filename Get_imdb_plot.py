import os
import re


def get_imdb_plot(input_path, output_path):
    files = os.listdir(input_path)
    for file in files[1:]:
        output_file = file.replace('.html', '.txt')
        source = open(input_path + file).read()
        #start try to get plot summary
        try:
            find_plot_summarys = source.split('<ul class="zebraList">')[1].split('</ul>')[0]
            plot_summarys = re.findall(r'<p class="plotSummary">\n(.*)</p>', find_plot_summarys)
            with open(output_path + output_file, 'w') as f:
                for summary in plot_summarys:
                    summary = summary.replace('        ', '').replace('\n', '').replace(',', '').replace('.', '')\
                                .replace('!', '').replace('?', '').replace('(', '').replace(')', '')
                    f.write(summary + '\n')
        except Exception as e:
            with open(output_path + output_file, 'w') as f:
                f.write('')


get_imdb_plot('./IMDB_pages/', './IMDB_plot/')