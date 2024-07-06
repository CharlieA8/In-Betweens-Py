from datetime import datetime
class ModelData:
    def __init__(self, num_correct, done, start_time, time, pauses, clue1, clue2, answer1, inbetween, answer2, correct, newClue, answers):
        self.answers = answers
        self.num_correct = num_correct
        self.done = done
        self.start_time = start_time
        self.end_time = None
        self.time = time
        self.pauses = pauses
        self.pause_start = None
        self.newClue = newClue
        self.correct = correct
        self.response = [False, False, False]
        self.answer1 = answer1
        self.inbetween = inbetween
        self.answer2 = answer2
        self.clue1 = clue1
        self.clue2 = clue2


    def reset(self):
        self.start_time = None
        self.end_time = None
        self.pause_start = None
        self.time = 0
        self.pauses.clear()
        self.done = False
    
    def correct_reset(self):
        self.newClue = True
        self.correct = True
        self.response = [False, False, False]
        self.answer1 = ''
        self.inbetween = ''
        self.answer2 = ''
    
    def get_clues(self):
        answer = self.answers[self.num_correct]
        self.clue1 = answer.clue1
        self.clue2 = answer.clue2
    
    def check_answer(self, answer1, in_between, answer2):
        response = [False, False, False]
        answer = self.answers[self.num_correct]
        response = answer.checkAnswer(answer1, in_between, answer2)
        if all(response):
            self.num_correct += 1
            if self.num_correct > 2:
                self.num_correct = 0
                self.done = True
                for answer in self.answers:
                    answer.response = [False, False, False]
        self.response = response
    
    def startTimer(self):
        if self.start_time == None:
            self.start_time = datetime.now()
    
    def pauseTimer(self):
        if self.pause_start == None:
            self.pause_start = datetime.now()

    def resumeTimer(self):
        if self.pause_start != None:
            pause_end = datetime.now()
            self.pauses.append([self.pause_start, pause_end])
            self.pause_start = None
    
    def stopTimer(self):
        self.end_time = datetime.now()
        paused_time = 0

        if len(self.pauses) != 0:
            for pause in self.pauses:
                paused_time += (pause[1] - pause[0]).total_seconds()
            
        total_time = (self.end_time - self.start_time).total_seconds() - paused_time
        self.time = round(total_time, 2)
        return self.time