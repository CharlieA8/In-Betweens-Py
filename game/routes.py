from flask import Blueprint, render_template, request, g, json, make_response, redirect, Response
from datetime import datetime
from game.modeldata import ModelData
import uuid
from game.session_management import save_session, load_session, delete_session, get_all_sessions
from copy import deepcopy

def create_blueprint(answers):
    bp = Blueprint('main', __name__)

    @bp.before_request
    def before_request():
        g.answers = answers

        # Check for session cookie
        session_id = request.cookies.get('session_id')

        if session_id:
            session_data = load_session(session_id)
            if session_data:
                g.modelData = ModelData(deepcopy(g.answers.answers), **session_data)
            else:
                g.modelData = None
        else:
            g.modelData = None

    @bp.route('/active_sessions')
    def debug_active_sessions():
        sessions_info = get_all_sessions()
        return Response(sessions_info, mimetype='text/plain')
    
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
        if not g.modelData:
            return redirect('/')

        g.modelData.get_clues()
        g.modelData.startTimer()
        save_session(request.cookies.get('session_id'), g.modelData)
        return render_template('play.html', clue1=g.modelData.clue1, clue2=g.modelData.clue2, newclue=True, correct=False)

    @bp.route('/pause')
    def pause():
        if not g.modelData:
            return redirect('/')
        
        g.modelData.pauseTimer()
        save_session(request.cookies.get('session_id'), g.modelData)
        return redirect('/')

    @bp.route('/resume')
    def resume():
        if not g.answers:
            return redirect('/')
        if not g.modelData:
            # New ModelData if no active session
            session_id = str(uuid.uuid4())
            g.modelData = ModelData(deepcopy(g.answers.answers))
            save_session(session_id, g.modelData)

            # set session_id cookie
            response = make_response(redirect('/play'))
            response.set_cookie('session_id', session_id)
            return response
        
        g.modelData.resumeTimer()
        save_session(request.cookies.get('session_id'), g.modelData)
        return redirect('/play')

    @bp.route('/submit', methods=['GET','POST'])
    def submit():
        if request.method == 'POST':
            if not g.modelData:
                return redirect('/')
        
            g.modelData.newClue = False
            g.modelData.correct = False
            g.modelData.answer1 = request.form['answer1']
            g.modelData.inbetween = request.form['in_between']
            g.modelData.answer2 = request.form['answer2']
            g.modelData.check_answer(g.modelData.answer1, g.modelData.inbetween, g.modelData.answer2)
            g.modelData.get_clues()

            if g.modelData.response == [True, True, True]:
                g.modelData.correct_reset()
            
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

                # Clear session data
                session_id = request.cookies.get('session_id')
                delete_session(session_id)

                response.delete_cookie('session_id')
                return response
            
            save_session(request.cookies.get('session_id'), g.modelData)
            return render_template('play.html', clue1=g.modelData.clue1, clue2=g.modelData.clue2, answer1=g.modelData.answer1, 
                                in_between=g.modelData.inbetween, answer2=g.modelData.answer2, response=g.modelData.response, 
                                newclue=g.modelData.newClue, correct=g.modelData.correct)
    return bp
