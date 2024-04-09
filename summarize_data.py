import duckdb as db

class summarize_bea():
    def __init__(self, con):
        self.con = con

    def create_employment_population(self):
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
        real_gdp_df = self.create_real_gdp()
        return real_gdp_df.pivot_table(index=["industry"], columns=["state", "year"], values=["real_gdp_million"]).T.reset_index().drop("level_0", axis=1)
    
    def income_top_five(self):
        query = """ 
        select *
        from income
        where change_rank <= 5
                """
        return self.con.sql(query).df()
    
    def income_type_comparison(self):
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
    
