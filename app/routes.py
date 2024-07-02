from flask import Blueprint, render_template, request, g, current_app, json, make_response, redirect
from datetime import datetime

bp = Blueprint('main', __name__)
active_sessions = {}

@bp.before_request
def before_request():
    # Ensure answers is available in g
    g.answers = current_app.config.get('answers')

@bp.route('/')
def title():
    stats_cookie = request.cookies.get('game_stats')
    today_cookie = request.cookies.get('today')
    playable = False
    date = str(datetime.now().date())

    if stats_cookie:
        game_stats = json.loads(stats_cookie)
        average_time = game_stats['average_time']
    else:
        average_time = "N/A"

    if today_cookie:
        today = json.loads(today_cookie)
        if date != today[1]:
            time_today = "N/A"
            playable = True
        else:
            time_today = today[0]
    else:
        time_today = "N/A"
        playable = True

    return render_template('title.html', average_time=average_time, time_today=time_today, playable=playable)

@bp.route('/rules')
def rules():
    return render_template('rules.html')

@bp.route('/play')
def play():
    clues = g.modelData.get_clues()
    clue1, clue2 = clues[0], clues[1]
    g.modelData.startTimer()
    return render_template('play.html', clue1=clue1, clue2=clue2, newclue=True, correct=False)

@bp.route('/pause')
def pause():
    g.modelData.pauseTimer()
    return redirect('/')

@bp.route('/resume')
def resume():
    g.modelData.resumeTimer()
    return redirect('/play')

@bp.route('/congrats')
def congrats():
    return render_template('congrats.html', time="10.47")

@bp.route('/submit', methods=['GET','POST'])
def submit():
    if request.method == 'POST':
        newclue = False
        correct = False
        answer1 = request.form['answer1']
        in_between = request.form['in_between']
        answer2 = request.form['answer2']
        response = g.modelData.check_answer(answer1, in_between, answer2)
        clue1, clue2 = g.modelData.get_clues()

        if response == [True, True, True]:
            response = [False, False, False]
            answer1, answer2, in_between = '', '', ''
            newclue = True 
            correct = True
        
        if g.modelData.done:
            time = g.modelData.stopTimer()
            g.modelData.reset()
            
            # Get the existing stats from cookies
            stats_cookie = request.cookies.get('game_stats')
            today_cookie = request.cookies.get('today')

            if stats_cookie:
                game_stats = json.loads(stats_cookie)
            else:
                game_stats = {'times': [], 'average_time': 0}

            if today_cookie:
                today = json.loads(today_cookie)
            else:
                today = ["N/A", str(datetime.now().date())]

            # Update the stats
            if str(datetime.now().date()) != today[1] or game_stats['times'] == []:
                game_stats['times'].append(time)
                today = [time, str(datetime.now().date())]

            game_stats['average_time'] = round(sum(game_stats['times']) / len(game_stats['times']), 2)

            # Set the updated stats in cookies
            response = make_response(render_template('congrats.html', time=time))
            response.set_cookie('game_stats', json.dumps(game_stats))
            response.set_cookie('today', json.dumps(today))
            return response
            
        return render_template('play.html', clue1=clue1, clue2=clue2, answer1=answer1, 
                               in_between=in_between, answer2=answer2, response=response, 
                               newclue=newclue, correct=correct)
    