from functools import lru_cache
import pandas as pd
import duckdb as db

class summarize_bea():
    def __init__(self, con):
        self.con = con

    def create_employment_population(self):
        """
        Join population table with employment
        """
        query = f"""
        select
            employment.geoname as state,
            employment.timeperiod as year,
            employment.datavalue as employment,
            population.datavalue as population,
            employment.topic
        from wages_salary employment
        inner join wages_salary population on employment.geoname = population.geoname and employment.timeperiod = population.timeperiod
        where employment.topic = 'Total employment'
            and employment.timeperiod >= 2000
            and population.topic = 'Population'
        order by state,
            year
                """
        return self.con.sql(query).df()

    def create_real_gdp(self):
        """
        Query Real GDP and create Real GDP in millions
        """
        query = """ 
        select 
            geoname as state,
            timeperiod as year,
            datavalue as real_gdp,
            datavalue / 1000000 as real_gdp_million,
            topic as industry
        from real_gdp
                """
        return self.con.sql(query).df()
    
    def real_gdp_pivot(self):
        """
        Pivot Real GDP on Industry for visualization on industry real GDP
        """
        real_gdp_df = self.create_real_gdp()
        return real_gdp_df.pivot_table(index=["industry"], columns=["state", "year"], values=["real_gdp_million"]).T.reset_index().drop("level_0", axis=1)
    
    def income_top_five(self):
        """
        Query top 5 income increases
        """
        query = """ 
        select *
        from income
        where change_rank <= 5
                """
        return self.con.sql(query).df()
    
    def income_type_comparison(self):
        """
        Join peronsal income with disposable income
        """
        query = """
        select 
            personal.state,
            personal.year,
            personal.income as personal_income,
            disposable.income as disposable_income
        from income personal
        inner join income disposable on personal.state = disposable.state and personal.year = disposable.year
        where personal.income_type = 'personal income'
                and disposable.income_type = 'disposable income'
                """
        return self.con.sql(query).df()

    def ce_change_rate(self):
        """
        Calculate mean & standard deviation of spend changes for each consumer expenditure
        """
        query = """ 
        select 
            consumer_expenditure,
            state,
            year,
            spend,
            prev_year_spend,
            spend_change,
            change_rank,
            stddev(spend_change) over (partition by consumer_expenditure, year) as std_dev,
            avg(spend_change) over (partition by consumer_expenditure, year) as mean,
            avg(spend_change) over (partition by consumer_expenditure, year) + stddev(spend_change) 
                over (partition by consumer_expenditure, year) as max,
            avg(spend_change) over (partition by consumer_expenditure, year) - stddev(spend_change) 
                over (partition by consumer_expenditure, year) as min,
            case 
                when spend_change >= avg(spend_change) over (partition by consumer_expenditure, year) + stddev(spend_change) 
                    over (partition by consumer_expenditure, year) then 'high rate'
                when spend_change <= avg(spend_change) over (partition by consumer_expenditure, year) - stddev(spend_change) 
                    over (partition by consumer_expenditure, year) then 'low rate'
                else 'normal rate'
            end as change_rate

        from consumer_expenditures
                """
        return self.con.sql(query)
    
    def summarize_ce_change_rate(self):
        """
        Create change rates based on standard devation of spend changes for consumer expenditures
        """
        ce_change_rate_sql = self.ce_change_rate()
        query = """ 
        select 
            year,
            consumer_expenditure,
            sum(case when change_rate = 'high rate' then 1 else 0 end) as 'High Rate',
            sum(case when change_rate = 'low rate' then 1 else 0 end) as 'Low Rate',
            sum(case when change_rate = 'normal rate' then 1 else 0 end) as 'Normal Rate'
            from ce_change_rate_sql
        where year <> '2000'
        group by 1, 2
        order by year,
                consumer_expenditure
                """
        ce_change_rate_summ = self.con.sql(query).df()
        df_melt = ce_change_rate_summ.melt(id_vars=["consumer_expenditure", "year"], 
                                        value_vars=["High Rate", "Low Rate", "Normal Rate"],
                                        var_name="change_rate", value_name="percent")
        return df_melt
    
    def ce_change_rate_table(self):
        """
        Query change rates created for each consumer expenditure
        """
        ce_change_rate_sql = self.ce_change_rate()
        query = """ 
        select
            year,
            state,
            consumer_expenditure,
            spend,
            prev_year_spend,
            spend_change,
            change_rate
        from ce_change_rate_sql
        order by year,
            state,
            consumer_expenditure
                """
        return self.con.sql(query).df()
    
    @lru_cache(maxsize=128)
    def get_state_abbv(self):
        """
        Get state abbreviations to join onto BEA state data 
        """
        state_url = "https://www.faa.gov/air_traffic/publications/atpubs/cnt_html/appendix_a.html"
        state_url_df = pd.read_html(state_url)[0]
        state_abbv_df = pd.concat([state_url_df.iloc[:, :2].rename({"STATE(TERRITORY)": "state", "STATE(TERRITORY).1": "state_abbv"}, axis=1), 
                        state_url_df.iloc[:, 2:4].rename({"STATE(TERRITORY).2": "state", "STATE(TERRITORY).3": "state_abbv"}, axis=1), 
                        state_url_df.iloc[:, 4:].rename({"STATE(TERRITORY).4": "state", "STATE(TERRITORY).5": "state_abbv"}, axis=1)
                        ]). reset_index(drop=True)
        return state_abbv_df
    
    def summary_for_map(self):
        """ 
        Join income, population, real gdp, total consumer expenditure, and employment tables to use as labels in the US map
        """
        query = """
        select 
                gdp.geoname as state,
                gdp.timeperiod as year,
                gdp.datavalue / 1000 as real_gdp,
                disp.datavalue as disposable_income,
                pers.datavalue as personal_income,
                ce.datavalue as consumer_expenditure,
                emp.datavalue as employment,
                pop.datavalue as population,
        from real_gdp gdp
        left join disposable_income disp on gdp.geoname = disp.geoname and gdp.timeperiod = disp.timeperiod
        left join personal_income pers on gdp.geoname = pers.geoname and gdp.timeperiod = pers.timeperiod
        left join consumption_expenditures ce on gdp.geoname = ce.geoname and gdp.timeperiod = ce.timeperiod
        left join wages_salary emp on gdp.geoname = emp.geoname and gdp.timeperiod = emp.timeperiod
        left join population pop on gdp.geoname = pop.geoname and gdp.timeperiod = pop.timeperiod
        where gdp.topic = 'All industry total'
                and disp.topic = 'Per capita disposable personal income'
                and pers.topic = 'Per capita personal income'
                and ce.topic = 'Per capita personal consumption expenditures (PCE) by state' 
                and emp.topic = 'Total employment'
                and pop.topic = 'Population'
                """
        return self.con.sql(query).df()
    
    def map_summ_state_abv(self):
        map_summ_df = self.summary_for_map()
        state_abbv_df = self.get_state_abbv()
        map_summ_abbv = map_summ_df.merge(state_abbv_df, on="state", how="left")
        return map_summ_abbv


# lru_cache