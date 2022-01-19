import pandas as pd
from datetime import datetime, timedelta


class CleaningUtility:
    def __init__(self):
        pass

    def clean_twitter_follows(
            self,
            dataframe: pd.DataFrame) -> pd.DataFrame:
        # Prevent tokenization errors when formatted into csv format
        for column in dataframe.columns[dataframe.dtypes == object]:
            dataframe[column] = dataframe[column].apply(lambda x: str(
                x).replace('\n', ' // ').replace('\t', '').replace('\r', ''))
        return dataframe

    def textualtime_to_timestring(x):
        ''' Cleaning function that replaces textual time prompts e.g. 4 hours ago, 2 days ago, into actual time estiamte
        i.e. Current Time - Elapsed Time (cleaned textual time prompt)

        Example Usage
        =============
        >>> preprocessTime('4 hours ago')
        2021-12-24 07:53:48
        '''

        timenow = datetime.now()

        if "hour" in x:

            t = x.replace("hours ago", "").replace("hour ago", "").strip(" ")

            t = timenow - timedelta(hours=int(t)) + timedelta(hours=8)

            return datetime.strftime(t, "%Y-%m-%d %H:%M:%S")

        elif "minute" in x:

            t = x.replace("minute ago", "").replace(
                "minutes ago", "").strip(" ")

            t = timenow - timedelta(minutes=int(t)) + timedelta(hours=8)

            return datetime.strftime(t, "%Y-%m-%d %H:%M:%S")

        else:

            t = datetime.strptime(x, "%d %b %Y") + timedelta(hours=8)

            return datetime.strftime(t, "%Y-%m-%d %H:%M:%S")
