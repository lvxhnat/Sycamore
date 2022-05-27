import pandas as pd
from datetime import datetime


def return_progress_condition(df):

    progress = df[df.STAT_DESC == "PROGRESS"]
    condition = df[df.STAT_DESC == "CONDITION"]

    def statdescDF(dataframe, reqp5y: bool = True):
        """ 
        Parameters
        ===================
        dataframe        : Pandas datarfame
        rep5y            : Boolean, whether p5y average is applicable or not 

        Output 
        ===================
        cov_descs        : Coefficient of variance calculated across the states for the particular year
        mean_descs       : Average across states for the particular year 
        sumnorm_descs    : Normalised sum calculation, summed across states for the particular year
        p5yAVG           : Pass 5 year average, with normalised sum calculation across the states for the particular year

        returns cov_descs, mean_descs, sumnorm_descs
        """

        dataframeMean = dataframe.groupby(["STAT_DESC", "YEAR", "WEEK", "UNIT_DESC"]).VALUE.mean(
        ).reset_index().rename(columns={"VALUE": "MEAN"})
        # To calculate CoV
        dataframeStd = dataframe.groupby(["STAT_DESC", "YEAR", "WEEK", "UNIT_DESC"]).VALUE.std(
        ).reset_index().rename(columns={"VALUE": "STDEV"})
        # To calculate normalised sums
        sums = pd.merge(dataframe.groupby(["STAT_DESC", "YEAR", "WEEK", "UNIT_DESC"]).VALUE.sum().reset_index(), dataframe.groupby(
            ["STAT_DESC", "YEAR", "WEEK"]).VALUE.sum().reset_index(), on=["STAT_DESC", "YEAR", "WEEK"], how="left")
        sums['PCT'] = (sums['VALUE_x']/sums['VALUE_y'])*100
        dataframeSums = sums.drop(columns=['VALUE_x', 'VALUE_y'])

        DATAFRAME = pd.merge(dataframeMean, dataframeStd, on=[
                             'STAT_DESC', 'YEAR', 'WEEK', 'UNIT_DESC'], how='left')
        DATAFRAME['COV'] = DATAFRAME['MEAN']/DATAFRAME['STDEV']

        # Rename the columns
        DATAFRAME.UNIT_DESC = DATAFRAME.UNIT_DESC.apply(
            lambda x: x.replace(" ", "_"))
        dataframeSums.UNIT_DESC = dataframeSums.UNIT_DESC.apply(
            lambda x: x.replace(" ", "_"))

        # Calculate mean, coefficient of variance and normalised sum across states
        mean_descs = pd.pivot_table(DATAFRAME[['STAT_DESC', 'YEAR', 'WEEK', 'UNIT_DESC', 'MEAN']], index=[
                                    "STAT_DESC", 'YEAR', 'WEEK'], columns=["UNIT_DESC"], values='MEAN').reset_index()
        cov_descs = pd.pivot_table(DATAFRAME.drop(columns=['MEAN', 'STDEV']), index=[
                                   "STAT_DESC", 'YEAR', 'WEEK'], columns=["UNIT_DESC"], values='COV').reset_index()
        sumnorm_descs = pd.pivot_table(dataframeSums, index=[
                                       "STAT_DESC", 'YEAR', 'WEEK'], columns=["UNIT_DESC"], values='PCT').reset_index()
        # Calculate P5Y Average based on normalised sum across states
        mean_descs['CALCULATION_TYPE'] = "mean"
        cov_descs['CALCULATION_TYPE'] = "cov"
        sumnorm_descs['CALCULATION_TYPE'] = "sums"

        if reqp5y:

            p5yAVG = sumnorm_descs[sumnorm_descs.YEAR.astype(int) >= int(datetime.now(
            ).year) - 5].drop(columns=['YEAR']).groupby(['STAT_DESC', 'WEEK']).mean().reset_index()
            p5yAVG['YEAR'] = 5
            # Label
            p5yAVG['CALCULATION_TYPE'] = "p5y_avg"
            return cov_descs, mean_descs, sumnorm_descs, p5yAVG

        else:
            return cov_descs, mean_descs, sumnorm_descs

    condition_cov_descs, condition_mean_descs, condition_sumnorm_descs, condition_p5yAVG = statdescDF(
        condition)

    condition_descs = pd.concat(
        [condition_cov_descs, condition_mean_descs, condition_sumnorm_descs, condition_p5yAVG])

    progress_cov_descs, progress_mean_descs, progress_sumnorm_descs = statdescDF(
        progress, False)

    progress_descs = pd.concat(
        [progress_cov_descs, progress_mean_descs, progress_sumnorm_descs])

    return condition_descs, progress_descs
