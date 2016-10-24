import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd


FILENAME = 'analyses.csv'
DATE_FMT = '%d/%m/%Y'
DATE_FMT_OUT = '%d-%m-%Y'
OUT_URL = 'urls'


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
    plt.savefig('img/{0}.png'.format(name), bbox_inches='tight')
    plt.show()


def analyze(df):
    # Criterions
    crit_malware = df.antivirus.map(lambda x: x != 'n/a' and (
        x.startswith('1/') or
        x.startswith('2/') or
        x.startswith('3/') or
        x.startswith('4/')
    ))
    crit_malware2 = df.antivirus.map(lambda x: x != 'n/a' and not (
        x.startswith('0/') or
        x.startswith('1/') or
        x.startswith('2/') or
        x.startswith('3/') or
        x.startswith('4/')
    ))
    crit_na = df.antivirus.map(lambda x: x == 'n/a')
    crit_notmalware = df.antivirus.map(lambda x: x.startswith('0/'))
    crit_duplicated = df.md5.duplicated()
    crit_pe32 = df.file_type.map(lambda x: str(x).startswith('PE32'))

    # Split analyses by malware, no scan at time or not malware
    anal_malware = df.md5[crit_malware].resample('M').count()
    anal_malware = anal_malware.rename('Malware (1 to 4 detections, mean={:.0f})'.format(anal_malware.mean()))
    anal_malware2 = df.md5[crit_malware2].resample('M').count()
    anal_malware2 = anal_malware2.rename('Malware (5+ detections, mean={:.0f})'.format(anal_malware2.mean()))
    anal_na = df.md5[crit_na].resample('M').count()
    anal_na = anal_na.rename('Not scanned (mean={:.0f})'.format(anal_na.mean()))
    anal_notmalware = df.md5[crit_notmalware].resample('M').count()
    anal_notmalware = anal_notmalware.rename('Not malware/Unknown at time (mean={:.0f})'.format(anal_notmalware.mean()))

    # Split analyses by md5 duplicates
    anal_unique = df.drop_duplicates(subset='md5').md5.resample('M').count()
    anal_unique = anal_unique.rename('Unique MD5 (mean={:.0f})'.format(anal_unique.mean()))
    anal_dups = df.md5[crit_duplicated].resample('M').count()
    anal_dups = anal_dups.rename('Not unique MD5 (mean={:.0f})'.format(anal_dups.mean()))


    # Group results
    anal_classification = pd.concat([anal_malware, anal_malware2, anal_notmalware, anal_na], axis=1)
    anal_classification = anal_classification.divide(anal_classification.sum(axis=1), axis=0)
    anal_unique_duplicates = pd.concat([anal_unique, anal_dups], axis=1)
    anal_unique_duplicates = anal_unique_duplicates.divide(anal_unique_duplicates.sum(axis=1), axis=0)

    # Plot
    plotAnalysesByMonth(anal_classification, 'classification_pe32', 'Analyses classification')
    plotAnalysesByMonth(anal_unique_duplicates, 'unique_dups_pe32', 'Duplicate samples')


def generate_urls(df):
    df = df.link
    for index in df.index.unique():
        df[df.index == index].to_csv(OUT_URL + '/' + index.strftime(DATE_FMT_OUT), index=False)


if __name__ == '__main__':
    df = loadCSV()

    generate_urls(df)


