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
