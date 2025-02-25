class Answer:
    def __init__(self, data=None):
        if data is not None:
            self.load_answer_from_json(data)
        else:
            self.id = -1
            self.answer1 = "Ans1"
            self.in_between = "Inbtw"
            self.answer2 = "Ans2"
            self.clue1 = "Clue1"
            self.clue2 = "Clue2"
            self.count1 = "count1"
            self.count2 = "count2"
            self.response = [False, False, False]

    def __str__(self):
        return f"{self.clue1} + {self.clue2}\n{self.answer1} + {self.in_between} + {self.answer2}"
    
    def normalize_apostrophes(self, input_string):
        # Replace smart apostrophes with standard apostrophes
        if input_string is None:
            return
        else:
            new_string = input_string.replace("’", "'").replace("‘", "'")
            return new_string

    def checkAnswer(self, answer1, in_between, answer2):
        ans1 = answer1.strip().upper()
        inbtw = in_between.strip().upper()
        ans2 = answer2.strip().upper()

        ans1 = self.normalize_apostrophes(ans1)
        inbtw = self.normalize_apostrophes(inbtw)
        ans2 = self.normalize_apostrophes(ans2)

        hint = False

        if ans1 == self.answer1:
            self.response[0] = True
        else:
            if self.in_between in ans1:
                hint = True
        
        if inbtw == self.in_between:
            self.response[1] = True
        
        if ans2 == self.answer2:
            self.response[2] = True
        else:
            if self.in_between in ans2:
                hint = True

        return [self.response, hint]
    
    def load_answer_from_json(self, data):
        self.id = data['id']
        self.answer1 = data['answer1']
        self.in_between = data['in_between']
        self.answer2 = data['answer2']
        self.clue1 = data['clue1']
        self.clue2 = data['clue2']
        self.count1 = data['count1']
        self.count2 = data['count2']
        self.response = [False, False, False]

def normalize_apostrophes(input_string):
        # Replace smart apostrophes with standard apostrophes
        if input_string is None:
            return
        else:
            new_string = input_string.replace("’", "'").replace("‘", "'")
            return new_string