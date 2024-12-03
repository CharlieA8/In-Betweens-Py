from flask import Blueprint, render_template, request, g, json, make_response, redirect, send_file, session, url_for
from datetime import datetime
from game.modeldata import ModelData
import uuid
from game.session_management import save_session, load_session, delete_session
from game.answer_management import get_answers, upload_answers, check_answers, force_update
from game.answer import normalize_apostrophes
from copy import deepcopy
import pytz
import os


bp = Blueprint('main', __name__)

@bp.before_request
def before_request():
    g.answers = get_answers()

    # Check for session cookie
    session_id = request.cookies.get('session_id')

    if session_id:
        session_data = load_session(session_id)
        if session_data:
            g.modelData = ModelData(deepcopy(g.answers), **session_data)
        else:
            g.modelData = None
    else:
        g.modelData = None

@bp.route('/')
def title():
    stats_cookie = request.cookies.get('game_stats')
    today_cookie = request.cookies.get('today')
    playable = False

    # Get date in EST
    timezone = pytz.timezone('US/Eastern')
    current_time = datetime.now(timezone)
    date = str(current_time.date())

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
    if not g.modelData:
        return redirect('/')

    g.modelData.get_clues()
    g.modelData.startTimer()
    save_session(request.cookies.get('session_id'), g.modelData)
    return render_template('play.html', clue1=g.modelData.clue1, clue2=g.modelData.clue2, correct=False,
                           count1=g.answers.count1, count2=g.answers.count2, newclue=True, response=g.modelData.response, 
                           answer1 = g.modelData.answer1, in_between = g.modelData.inbetween, answer2 = g.modelData.answer2)

@bp.route('/pause')
def pause():
    if not g.modelData:
        return redirect('/')
    
    g.modelData.pauseTimer()
    save_session(request.cookies.get('session_id'), g.modelData)
    return redirect('/')

@bp.route('/resume')
def resume():
    # Check if the user has already played today
    today_cookie = request.cookies.get('today')

    if today_cookie:
        today = json.loads(today_cookie)

        # Get date in EST
        timezone = pytz.timezone('US/Eastern')
        current_time = datetime.now(timezone)
        date = str(current_time.date())

        if date == today[1]:
            return redirect('/')

    if not g.answers:
        return redirect('/')
    if not g.modelData:
        # New ModelData if no active session
        session_id = str(uuid.uuid4())
        g.modelData = ModelData(deepcopy(g.answers))
        save_session(session_id, g.modelData)

        # set session_id cookie
        response = make_response(redirect('/play'))
        response.set_cookie('session_id', session_id)

        # Log usage
        print(f"*Start* New user started with id {session_id}")

        return response
    
    g.modelData.resumeTimer()
    save_session(request.cookies.get('session_id'), g.modelData)
    return redirect('/play')

@bp.route('/submit', methods=['GET','POST'])
def submit():
    if not g.modelData:
            return redirect('/')

    if request.method == 'POST':
        g.modelData.answer1 = request.form['answer1']
        g.modelData.inbetween = request.form['in_between']
        g.modelData.answer2 = request.form['answer2']
        hint = g.modelData.check_answer(g.modelData.answer1, g.modelData.inbetween, g.modelData.answer2)

        if g.modelData.correct:
            time = g.modelData.stopTimer()
            
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
                today = ["N/A", None]

            # Update the stats
            timezone = pytz.timezone('US/Eastern')
            date = str(datetime.now(timezone).date())
            if today[0] == "N/A" or today[1] != date or game_stats['times'] == []:
                game_stats['times'].append(time)
                today = [time, date]

            num_times = len(game_stats['times'])
            game_stats['average_time'] = round(sum(game_stats['times']) / num_times, 2)

            # Set the updated stats in cookies
            max_age = 10 * 365 * 24 * 60 * 60 # 10 years!!
            response = make_response(render_template('congrats.html', time=time))
            response.set_cookie('game_stats', json.dumps(game_stats), max_age=max_age)
            response.set_cookie('today', json.dumps(today), max_age=86400)

            # Clear session data
            session_id = request.cookies.get('session_id')
            delete_session(session_id)
            response.delete_cookie('session_id')

            # Log usage
            print(f"*Completion* New user ({session_id}) submitted in {time}s. Total times: {num_times}")

            return response
        else:
            session_id = request.cookies.get('session_id')
            save_session(session_id, g.modelData)

            # Log progress
            result = g.modelData.getResponse()
            print(f"*Progress* User ({session_id}) submitted an incorrect answer ({result})")

            return render_template('play.html', clue1=g.modelData.clue1, clue2=g.modelData.clue2, answer1=g.modelData.answer1, 
                                in_between=g.modelData.inbetween, answer2=g.modelData.answer2, response=g.modelData.response, 
                                correct=g.modelData.correct, count1=g.answers.count1, count2=g.answers.count2, newclue=False, hint=hint)
    else:
        return redirect('/resume')


@bp.route('/sitemap.xml', methods=['GET'])
def sitemap():
    sitemap_content = render_template('sitemap.xml')
    response = make_response(sitemap_content)
    response.headers['Content-Type'] = 'application/xml'
    return response

@bp.route('/robots.txt', methods=['GET'])
def robots_txt():
    return send_file('robots.txt')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        # code here for logging anna in 
        # and redirecting to update screen
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            return render_template('login.html', message="All fields must be filled!")
        if username == os.getenv('USERNAME') and password == os.getenv('PASSWORD'):
            session['admin'] = True
            return redirect('/update')
        else:
            return render_template('login.html', message="Incorrect username or password")
        
@bp.route('/update', methods=['GET', 'POST'])
def update():
    if not session.get('admin'):
        return redirect('/login')
    
    if request.method == 'GET':
        return render_template('update.html', new_data=check_answers())
    else:
        clue1 = normalize_apostrophes(request.form["clue1"].strip())
        clue2 = normalize_apostrophes(request.form["clue2"].strip())
        in_between = normalize_apostrophes(request.form["in_between"].strip().upper())
        answer1 = normalize_apostrophes(request.form["answer1"].strip().upper())
        answer2 = normalize_apostrophes(request.form["answer2"].strip().upper())

        if not (clue1 and clue2 and in_between and answer1 and answer2):
            message = "All fields must be filled!"
            message_type = "error"
            return render_template('update.html', message=message, message_type=message_type, new_data=check_answers())
        elif '"' in clue1 or '"' in clue2:
            message = "Clues cannot contain double quotes!"
            message_type = "error"
            return render_template('update.html', message=message, message_type=message_type, new_data=check_answers())
        else:
            data = {
                "clue1": clue1,
                "clue2": clue2,
                "in_between": in_between,
                "answer1": answer1,
                "answer2": answer2,
                "count1": len(answer1.split()) + 1,
                "count2": len(answer2.split()) + 1,
            }
            upload_answers(data)
            return redirect('/update')
        
@bp.route('/forceupdate', methods=['GET'])
def force():
    if not session.get('admin'):
        return redirect('/login')
    force_update()
    message = "Update successfully forced."
    message_type = "success"
    return render_template('update.html', message=message, message_type=message_type, new_data=check_answers())