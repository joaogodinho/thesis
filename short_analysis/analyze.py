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


if __name__ == '__main__':
    df = loadCSV()

    # Criterions
    crit_malware = df.antivirus.map(lambda x: x != 'n/a' and not x.startswith('0/'))
    crit_na = df.antivirus.map(lambda x: x == 'n/a')
    crit_notmalware = df.antivirus.map(lambda x: x.startswith('0/'))

    # Split analyses by malware, no scan at time or not malware
    anal_month_malware = df.md5[crit_malware].resample('M').count()
    anal_month_malware = anal_month_malware.rename('Malware (1+ detections)')
    anal_month_na = df.md5[crit_na].resample('M').count()
    anal_month_na = anal_month_na.rename('Not scanned')
    anal_month_notmalware = df.md5[crit_notmalware].resample('M').count()
    anal_month_notmalware = anal_month_notmalware.rename('Not malware/Unknown at time')
    # Group results
    anal_month = pd.concat([anal_month_malware, anal_month_notmalware, anal_month_na], axis=1)

    ticklabels = [item.strftime('%b %Y') for item in anal_month.index]
    ax = anal_month.plot(kind='bar', figsize=(20, 10))
    ax.xaxis.set_major_formatter(mticker.FixedFormatter(ticklabels))
    plt.ylabel('#Analyses')
    plt.savefig('months.png', bbox_inches='tight')
    plt.show()
