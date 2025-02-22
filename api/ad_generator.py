

class AdGenerator:
    def __init__(self, id, keywords):
        self.id = id
        self.keywords = keywords
        self.status = 'New'
        print(self.id + " " + self.keywords)

    def