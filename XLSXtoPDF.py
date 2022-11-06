import pandas
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def xlsx_to_pdf(df: pandas.DataFrame, path:str):
    fig, ax =plt.subplots(figsize=(4,1))

    ax.axis('tight')
    ax.axis('off')

    ax.table(cellText=df.values, colLabels=df.columns, loc='center')
    pp = PdfPages(path)
    pp.savefig(fig, bbox_inches='tight')
    pp.close()