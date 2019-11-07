# This semaphore is for the checkout. We do not want to lock all the threads if the product that is being handled is
# different. As such we will be using a set (non-duplicate and non-ordered) list of ids. If an id is in the set than
# if another wait call is made for the same id will have to wait. Otherwise they can resume without any issues.
# Note: Deadlock can occur if notify is not called.
import time

class Checkout_Semaphore:
    # A set of all locked ids
    product_ids = set()

    def wait(self, id):
        subset = {id}
        while self.product_ids.issuperset(subset):
            # this should in theory prevent two threads from resuming at the same time and maintain mutual exclusivity.
            time.sleep(0.5)
        self.product_ids.add(id)

    def notify(self, id):
        self.product_ids.discard(id)