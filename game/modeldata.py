from datetime import datetime
class ModelData:
    def __init__(self, answer, done=False, start_time=None, time=0, pauses=None, 
                 pause_start=None, clue1='', clue2='', answer1='', inbetween='', 
                 answer2='', correct=False, response=[False, False, False]):
        self.answer = answer
        self.done = done
        self.start_time = start_time
        self.end_time = None
        self.time = time
        self.pauses = pauses if pauses is not None else []
        self.pause_start = pause_start
        self.correct = correct
        self.response = response
        self.answer1 = answer1
        self.inbetween = inbetween
        self.answer2 = answer2
        self.clue1 = clue1
        self.clue2 = clue2
        self.count1 = 0
        self.count2 = 0

    def reset(self):
        self.start_time = None
        self.end_time = None
        self.pause_start = None
        self.time = 0
        self.pauses.clear()
        self.done = False
    
    def get_clues(self):
        self.clue1 = self.answer.clue1
        self.clue2 = self.answer.clue2
        self.count1 = self.answer.count1
        self.count2 = self.answer.count2
    
    def check_answer(self, answer1, in_between, answer2):
        response = [False, False, False]
        answer = self.answer
        response = answer.checkAnswer(answer1, in_between, answer2)
        if all(response):
            self.correct = True
        else:
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