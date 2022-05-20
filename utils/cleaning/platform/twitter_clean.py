import pandas as pd


def clean_twitter_follows(dataframe: pd.DataFrame) -> pd.DataFrame:
    # Prevent tokenization errors when formatted into csv format
    for column in dataframe.columns[dataframe.dtypes == object]:
        dataframe[column] = dataframe[column].apply(lambda x: str(
            x).replace('\n', ' // ').replace('\t', '').replace('\r', ''))
    return dataframe
