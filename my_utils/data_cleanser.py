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