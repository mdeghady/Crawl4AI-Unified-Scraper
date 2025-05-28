import re


class DataCleasnerUtils:
    def _convert_currency_symbos_to_code(self, price_string):
        """Convert currency symbol to code
        :arg
            price_string: string e.g. '€75.5', '60$', '3£'
        :return
            string: string e.g. 'EUR', 'USD', 'GBP'
        """
        currency_symbol = self._extract_currency_symbols(price_string)
        if currency_symbol == '€':
            return 'EUR'
        elif currency_symbol == '$':
            return 'USD'
        elif currency_symbol == '£':
            return 'GBP'
        else:
            return price_string

    def _extract_currency_symbols(self,text):
        # Matches common currency symbols (including crypto and rare ones)
        pattern = r'[€$£¥₹₽₩₪₺₴₸₿฿₫៛₡₱₲₵₶₾₼₠₣₤₥₦₧₨₩₪₫₭₮₯₰₳₷₺₻₼₽₾₿]'
        return re.findall(pattern, text)[0]

    def convert_price_to_float(self , price_string,delimiter):
        """Convert price string to float
        :arg
            price_string: string e.g. '€75.5', '60$', '3£'
            delimiter: string e.g. '.', ','
        :return
            float: e.g. 75.5, 60.0, 3.0
        """
        if not price_string:
            return 0.0
        price_string = re.sub(r'[^\d{}]'.format(delimiter), '', price_string)
        return float(price_string.replace(delimiter, '.')) if price_string else 0.0

    def flatten_list_of_dicts(self, list_of_dicts , dicts_key):
        """Flatten a list of dictionaries into a single list of values
        :arg
            list_of_dicts: list of dictionaries e.g. [{'Size': 'S'}, {'Size': 'M'}, {'Size': 'L'}]
            dicts_key: key to extract from each dictionary e.g. 'Size'
        :return
            flattened_dict: list of values e.g. ['S', 'M', 'L']
        """
        flat_list = [d[dicts_key] for d in list_of_dicts if dicts_key in d]

        return flat_list
