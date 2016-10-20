import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd


FILENAME = 'analyses.csv'
DATE_FMT = '%d/%m/%Y'


def loadCSV():
    # Read CSV into a pandas dataframe
    df = pd.read_csv(FILENAME)
    # Convert from string to date
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
    # Set date as index
    df = df.set_index('date')
    return df


def plotAnalysesByMonth(df, name, title):
    ticklabels = [item.strftime('%b %Y') for item in df.index]
    ax = df.plot(kind='bar', stacked=True, figsize=(20, 10), alpha=0.6)
    ax.xaxis.set_major_formatter(mticker.FixedFormatter(ticklabels))
    plt.title(title)
    plt.ylabel('Percent (%)')
    plt.savefig('{0}.png'.format(name), bbox_inches='tight')
    plt.show()



if __name__ == '__main__':
    df = loadCSV()

    # Criterions
    crit_malware = df.antivirus.map(lambda x: x != 'n/a' and not x.startswith('0/'))
    crit_na = df.antivirus.map(lambda x: x == 'n/a')
    crit_notmalware = df.antivirus.map(lambda x: x.startswith('0/'))
    crit_duplicated = df.md5.duplicated()

    # Split analyses by malware, no scan at time or not malware
    anal_malware = df.md5[crit_malware].resample('M').count()
    anal_malware = anal_malware.rename('Malware (1+ detections)')
    anal_na = df.md5[crit_na].resample('M').count()
    anal_na = anal_na.rename('Not scanned')
    anal_notmalware = df.md5[crit_notmalware].resample('M').count()
    anal_notmalware = anal_notmalware.rename('Not malware/Unknown at time')

    # Split analyses by md5 duplicates
    anal_unique = df.drop_duplicates(subset='md5').md5.resample('M').count()
    anal_unique = anal_unique.rename('Unique MD5')
    anal_dups = df.md5[crit_duplicated].resample('M').count()
    anal_dups = anal_dups.rename('Not unique MD5')


    # Group results
    anal_classification = pd.concat([anal_malware, anal_notmalware, anal_na], axis=1)
    anal_classification = anal_classification.divide(anal_classification.sum(axis=1), axis=0)
    anal_unique_duplicates = pd.concat([anal_unique, anal_dups], axis=1)
    anal_unique_duplicates = anal_unique_duplicates.divide(anal_unique_duplicates.sum(axis=1), axis=0)

    # Plot
    plotAnalysesByMonth(anal_classification, 'classifcation', 'Analyses classification')
    plotAnalysesByMonth(anal_unique_duplicates, 'unique_dups', 'Duplicate samples')



