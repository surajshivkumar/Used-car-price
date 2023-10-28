import pandas as pd

from utils import get_confg, get_sql_conn

class Search:
    '''Search Queries'''

    def __init__(self, config) -> None:
        '''
        Constructor for the Search class.

        Parameters:
        config (dict): Configuration settings.
        '''
        self.config = config

    def processSearch(self, searchResult: pd.DataFrame, searchTerm: str):
        '''
        Process the search results.

        Parameters:
        searchResult (pd.DataFrame): DataFrame containing search results.
        searchTerm (str): The search term used.

        Returns:
        list: Processed search results as a list of dictionaries.
        '''
        # Remove duplicate entries based on 'make', 'year', and 'model'.
        searchResult = searchResult.drop_duplicates(['make', 'year', 'model'])
        searchResult['search'] = searchTerm
        searchResult['path'] = searchResult.path
        searchResult = searchResult.sort_values(['mileage'], ascending=True)
        searchResult['path'] = searchResult.path.apply(lambda car: car.split('.')[0] + '.webp')
        searchResult = [term for term in searchResult.T.to_dict().values()]

        for car in searchResult:
            path_parts = car['path'].split('.')
            new_path = path_parts[0] + '.webp'
            car['path'] = new_path
        return searchResult

    def processResultsView(self, car: pd.DataFrame):
        '''
        Process car details for results view.

        Parameters:
        car (pd.DataFrame): DataFrame containing car details.

        Returns:
        dict: Processed car details as a dictionary.
        '''
        car.columns = [col.replace('cd_', '') for col in car.columns]
        car = car[['id','mileage_miles', 'car_price', 'year', 'make', 'model',
                   'body_style', 'doors', 'mpg', 'engine', 'transmission', 'drive_type',
                   'fuel', 'tank_size', 'bed_style', 'cab_style', 'path_']]
        car = car.rename(columns={'mileage_miles': 'mileage',
                                 'car_price': 'price',
                                 'path_': 'path'
                                 })
        car['path'] = car['path'].map(lambda x: x.split('.')[0] + '.webp')
        car = car.T.to_dict()[0]
        return car

    def getSearchResult(self, searchTerm: str, searchType: str) -> list:
        '''
        Get search results.

        Parameters:
        searchTerm (str): The search term used.
        searchType (str): Type of search ('search' or 'other').

        Returns:
        list: List of search results as dictionaries.
        '''
        res = []
        conn = get_sql_conn(self.config['sql-prod'],
                            self.config.get('sql-prod', 'bi_db'))
        if searchType == 'search':
            res = pd.read_sql(f'''select cd_id as product_id,
                                        cd_mileage_miles as mileage,
                                        cd_year as Year,
                                        cd_make as Make,
                                        cd_car_price as Price,
                                        cd_path_ as path,
                                        cd_model as Model
                                from car_details cd 
                                where upper(cd_make) = '{searchTerm.split(' ')[0].upper()}' and
                                upper(cd_model) = '{' '.join(searchTerm.split(' ')[1:]).upper()}' ''', conn)
        else:
            res = pd.read_sql(f'''select cd_id as product_id,
                                        cd_mileage_miles as mileage,
                                        cd_year as Year,
                                        cd_make as Make,
                                        cd_car_price as Price,
                                        cd_path_ as path,
                                        cd_model as Model
                                from car_details cd 
                                where cd_body_style = '{searchTerm}' ''', conn)
        conn.close()
        return res

    def getAllCars(self) -> list:
        '''
        Get a list of all available cars.

        Returns:
        list: List of car names.
        '''
        conn = get_sql_conn(self.config['sql-prod'],
                            self.config.get('sql-prod', 'bi_db'))
        cars = pd.read_sql("select distinct concat(cd_make, ' ', cd_model) as cars from car_details", conn)
        conn.close()
        cars['cars'] = cars.apply(lambda x: x.str.title())
        return cars.values.ravel().tolist()

    def getProduct(self, product_id):
        '''
        Get product details based on product ID.

        Parameters:
        product_id: The ID of the product.

        Returns:
        pd.DataFrame: DataFrame containing product details.
        '''
        conn = get_sql_conn(self.config['sql-prod'],
                            self.config.get('sql-prod', 'bi_db'))
        car = pd.read_sql(f'''select * from car_details where cd_id = {product_id}''', conn)
        return car
