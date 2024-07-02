from datetime import datetime
class ModelData:
    def __init__(self, answers):
        self.answers = answers
        self.num_correct = 0
        self.done = False
        self.start_time = None
        self.end_time = None
        self.time = 0
        self.pauses = []
        self.pause_start = None

    def reset(self):
        self.start_time = None
        self.end_time = None
        self.pause_start = None
        self.time = 0
        self.pauses.clear()
        self.done = False
    
    def load_from_dict(self, data):
        self.num_correct = data['num_correct']
        self.done = data['done']
        self.start_time = datetime.fromisoformat(data['start_time']) if data['start_time'] else None
        self.end_time = datetime.fromisoformat(data['end_time']) if data['end_time'] else None
        self.time = data['time']
        self.pauses = [(datetime.fromisoformat(start), datetime.fromisoformat(end)) for start, end in data['pauses']]
        self.pause_start = datetime.fromisoformat(data['pause_start']) if data['pause_start'] else None

    def to_dict(self):
        return {
            'num_correct': self.num_correct,
            'done': self.done,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'time': self.time,
            'pauses': [(start.isoformat(), end.isoformat()) for start, end in self.pauses],
            'pause_start': self.pause_start.isoformat() if self.pause_start else None
        }
    

    def get_clues(self):
        answer = self.answers[self.num_correct]
        clues = [answer.clue1, answer.clue2]
        return clues
    
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
        return response
    
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