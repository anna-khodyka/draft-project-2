urls_dict = \
        {  'covid' :     {
                'url': 'https://moz.gov.ua/article/news/operativna-'+
                       'informacija-pro-poshirennja-koronavirusnoi-infekcii-2019-cov19',
                'parser': 'CovidHTMLParser'
                        },
           'currency':  {
               'url': 'https://minfin.com.ua/ua/currency/',
               'parser': 'CurrencyHTMLParser'
                        },
           'inflation': {
               'url':   'https://index.minfin.com.ua/ua/economy/index/inflation/',
               'parser': 'InflationHTMLParser'
                        }
        }