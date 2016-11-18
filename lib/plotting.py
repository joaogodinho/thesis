import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


def plotByMonth(df, name, title):
    ticklabels = [item.strftime('%b %Y') for item in df.index]
    ax = df.plot(kind='bar', figsize=(20, 10), alpha=0.6)
    ax.xaxis.set_major_formatter(mticker.FixedFormatter(ticklabels))
    plt.title(title)
    plt.ylabel('#Analyses')
    # plt.savefig('img/{0}.png'.format(name), bbox_inches='tight')
    plt.show()


def plotByMonthPercentage(df, name, title):
    ticklabels = [item.strftime('%b %Y') for item in df.index]
    ax = df.plot(kind='bar', stacked=True, figsize=(20, 10), alpha=0.6)
    ax.xaxis.set_major_formatter(mticker.FixedFormatter(ticklabels))
    ax.set_ylim([0, 1])
    plt.title(title)
    plt.ylabel('Percent (x100)')
    # plt.savefig('img/{0}.png'.format(name), bbox_inches='tight')
    plt.show()