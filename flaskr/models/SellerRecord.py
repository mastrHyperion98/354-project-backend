
class SellerRecord(object):

    def __init__(self, username, number_of_sales):
        self.sales = number_of_sales
        self.username = username

    def __gt__(self, other):
        return self.sales > other.sales

    def to_json(self):
        """Returns the instance of product as a JSON

          Returns:
              dict -- JSON representation of the product
          """
        return {
            'username': self.username,
            'sales': self.sales
        }