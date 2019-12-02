
class SellerRecord(object):

    def __init__(self, product_permalink, number_of_sales):
        self.sales = number_of_sales
        self.product_permalink = product_permalink

    def __gt__(self, other):
        return self.sales > other.sales

    def to_json(self):
        """Returns the instance of product as a JSON

          Returns:
              dict -- JSON representation of the product
          """
        return {
            'product_permalink': self.product_permalink,
            'sales': self.sales
        }