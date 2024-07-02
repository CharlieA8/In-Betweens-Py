import json

class Answer:
    def __init__(self, id, answer1, in_between, answer2, clue1, clue2):
        self.id = id
        self.answer1 = answer1
        self.in_between = in_between
        self.answer2 = answer2
        self.clue1 = clue1
        self.clue2 = clue2
        self.response = [False, False, False]

    def __str__(self):
        return f"{self.clue1} + {self.clue2}\n{self.answer1} + {self.in_between} + {self.answer2}"
    
    def checkAnswer(self, answer1, in_between, answer2):
        ans1 = answer1.strip()
        inbtw = in_between.strip()
        ans2 = answer2.strip()

        if ans1.upper() == self.answer1:
            self.response[0] = True
        if inbtw.upper() == self.in_between:
            self.response[1] = True
        if ans2.upper() == self.answer2:
            self.response[2] = True

        return self.response
    
class Answers:
    def __init__(self, file_path):
        self.answers = []
        self.load_answers_from_json(file_path)

    def load_answers_from_json(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
            for item in data:
                answer = Answer(item['id'], item['answer1'], item['in_between'], item['answer2'], item['clue1'], item['clue2'])
                self.answers.append(answer)

