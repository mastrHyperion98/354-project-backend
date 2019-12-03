
class ProductRecord(object):

    def __init__(self, product, number_of_sales):
        self.sales = number_of_sales
        self.product = product

    def __gt__(self, other):
        return self.sales > other.sales

    def to_json(self):
        """Returns the instance of product as a JSON

          Returns:
              dict -- JSON representation of the product
          """
        return {
            'product': self.product,
            'sales': self.sales
        }