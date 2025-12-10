from flask import Blueprint, render_template, request, g, json, make_response, redirect, send_file, session, url_for
from datetime import datetime, timedelta
import bcrypt
from cryptography.fernet import Fernet 
import base64 
from game.modeldata import ModelData
import uuid
from game.session_management import save_session, load_session, delete_session
from game.answer_management import get_answers, upload_answers, get_update, force_update, get_answers_dict
from game.answer import normalize_apostrophes, Answer
from game.archive_management import get_archive, save_level_completion, get_levels_array, upload_archive, visualize_archive, get_user_progress, delete_level
from game.update_queue import visualize_queue, queue_push, delete_from_queue
from copy import deepcopy
import pytz
import os

bp = Blueprint('main', __name__)

# Utility functions for cookie encryption/decryption
def encrypt_cookie_data(data, secret_key):
    """Encrypt cookie data"""
    json_data = json.dumps(data)
    key = base64.urlsafe_b64encode(secret_key.ljust(32)[:32].encode())
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(json_data.encode())
    return base64.urlsafe_b64encode(encrypted_data).decode()

def decrypt_cookie_data(encrypted_data, secret_key):
    """Decrypt cookie data"""
    try:
        key = base64.urlsafe_b64encode(secret_key.ljust(32)[:32].encode())
        cipher = Fernet(key)
        decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = cipher.decrypt(decoded_data).decode()
        return json.loads(decrypted_data)
    except Exception:
        return None

@bp.before_request
def before_request():
    g.answers = get_answers()
    secret_key = request.environ.get('FLASK_SECRET_KEY', 'dev')

    # Check for session cookies
    session_id = request.cookies.get('session_id')
    archive_cookie = request.cookies.get('archive_id')
    
    if archive_cookie:
        try:
            # Decrypt the archive cookie
            archive_data = decrypt_cookie_data(archive_cookie, secret_key)
            archive_id, n = archive_data
            session_data = load_session(archive_id)
            if session_data:
                g.archive_session = ModelData(get_archive(n), **session_data)
            else:
                g.archive_session = None
        except:
            g.archive_session = None
    else:
        g.archive_session = None

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
    secret_key = request.environ.get('FLASK_SECRET_KEY', 'dev')
    stats_cookie = request.cookies.get('game_stats')
    today_cookie = request.cookies.get('today')
    playable = False

    # Get date in EST
    timezone = pytz.timezone('US/Eastern')
    current_time = datetime.now(timezone)
    date = str(current_time.date())

    if stats_cookie:
        try:
            game_stats = decrypt_cookie_data(stats_cookie, secret_key)
            average_time = str(game_stats['average_time']) + "s"
        except:
            average_time = "N/A"
    else:
        average_time = "N/A"

    if today_cookie:
        try:
            today = decrypt_cookie_data(today_cookie, secret_key)
            if date >= today[1]:
                time_today = "N/A"
                playable = True
            else:
                time_today = str(today[0]) + "s"
        except:
            time_today = "N/A"
            playable = True
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
    secret_key = request.environ.get('FLASK_SECRET_KEY', 'dev')

    if today_cookie:
        try:
            today = decrypt_cookie_data(today_cookie, secret_key)
        except:
            today = ["N/A", None]
    else: 
        today = ["N/A", None]

    # Get date in EST
    timezone = pytz.timezone('US/Eastern')
    current_time = datetime.now(timezone)
    date = str(current_time.date())

    if today is not None and today[1] is not None and date < today[1]:
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
        response.set_cookie('session_id', session_id,  httponly=True)

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
            secret_key = request.environ.get('FLASK_SECRET_KEY', 'dev')

            if stats_cookie:
                try:
                    game_stats = decrypt_cookie_data(stats_cookie, secret_key)
                except:
                    game_stats = {'times': [], 'average_time': 0}
            else:
                game_stats = {'times': [], 'average_time': 0}

            if today_cookie:
                try:
                    today = decrypt_cookie_data(today_cookie, secret_key)
                except:
                    today = ["N/A", None]
            else:
                today = ["N/A", None]

            if today is None:
                today = ["N/A", None]

            if game_stats is None:
                game_stats = {'times': [], 'average_time': 0}

            # Update the stats
            timezone = pytz.timezone('US/Eastern')
            current_time = datetime.now(timezone)
            days_ahead = (6 - current_time.weekday()) if current_time.weekday() != 6 else 7
            next_sunday_date = str((current_time + timedelta(days=days_ahead)).date())

            if today[0] == "N/A" or today[1] != next_sunday_date or game_stats['times'] == []:
                game_stats['times'].append(time)
                today = [time, next_sunday_date]

            num_times = len(game_stats['times'])
            game_stats['average_time'] = round(sum(game_stats['times']) / num_times, 2)

            # Set the updated stats in cookies
            max_age = 10 * 365 * 24 * 60 * 60 # 10 years!!

            # Encrypt cookie data
            encrypted_stats = encrypt_cookie_data(game_stats, secret_key)
            encrypted_today = encrypt_cookie_data(today, secret_key)

            response = make_response(render_template('congrats.html', time=time))
            response.set_cookie('game_stats', encrypted_stats, max_age=max_age,  httponly=True)
            response.set_cookie('today', encrypted_today, max_age=max_age,  httponly=True)

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
        
        hash_pw = os.getenv('PW_HASH')

        if username == os.getenv('USERNAME') and bcrypt.checkpw(password.encode('utf-8'), hash_pw.encode('utf-8')):
            session['admin'] = True
            return redirect('/admin/dashboard')
        else:
            return render_template('login.html', message="Invalid credentials")
        
@bp.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/login')
        
@bp.route('/admin/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect('/login')

    current_answers = get_answers_dict()
    current_update = get_update()
    
    return render_template('dashboard.html', live=current_answers, staged=current_update)
        
@bp.route('/admin/create', methods=['GET', 'POST'])
def create_puzzle():
    if not session.get('admin'):
        return redirect('/login')

    if request.method == 'POST':
        submit_action = request.form.get('submit_action')

        # Extract form values
        clue1 = normalize_apostrophes(request.form["clue1"].strip())
        clue2 = normalize_apostrophes(request.form["clue2"].strip())
        in_between = normalize_apostrophes(request.form["in_between"].strip().upper())
        answer1 = normalize_apostrophes(request.form["answer1"].strip().upper())
        answer2 = normalize_apostrophes(request.form["answer2"].strip().upper())

        if not (clue1 and clue2 and in_between and answer1 and answer2):
            message = "All fields must be filled!"
            message_type = "error"
            return render_template('create.html', message=message, message_type=message_type)
        elif '"' in clue1 or '"' in clue2:
            message = "Clues cannot contain double quotes!"
            message_type = "error"
            return render_template('create.html', message=message, message_type=message_type)

        data = {
            "clue1": clue1,
            "clue2": clue2,
            "in_between": in_between,
            "answer1": answer1,
            "answer2": answer2,
            "count1": len(answer1.split()) + 1,
            "count2": len(answer2.split()) + 1,
        }
        if submit_action == 'update':
            upload_answers(data)
            message = "Update table successfully updated!"
        elif submit_action == 'archive':
            upload_archive(data)
            message = "Archive successfully updated!"
        elif submit_action == 'queue':
            queue_push(data)
            message = "Puzzle successfully added to queue!"
        
        message_type = "success"
        return render_template('create.html', message=message, message_type=message_type)
    else:
        return render_template('create.html')
    
@bp.route('/view-archive', methods=['GET'])
def view_archive():
    if not session.get('admin'):
        return redirect('/login')
    
    levels = visualize_archive()
    return render_template('view_archive.html', levels=levels)

@bp.route('/view-archive/<int:n>', methods=['GET'])
def archive_pop(n):
    if not session.get('admin'):
        return redirect('/login')
    delete_level(n)
    levels = visualize_archive()
    return render_template('view_archive.html', levels=levels)

@bp.route('/view-queue', methods=['GET'])
def view_queue():
    if not session.get('admin'):
        return redirect('/login')
    clues = visualize_queue()
    return render_template('view_queue.html', clues=clues)

@bp.route('/view-queue/delete/<int:id>', methods=['GET'])
def queue_delete(id):
    if not session.get('admin'):
        return redirect('/login')
    delete_from_queue(id)
    clues = visualize_queue()
    return render_template('view_queue.html', clues=clues)
        
@bp.route('/forceupdate', methods=['GET'])
def force():
    if not session.get('admin'):
        return redirect('/login')
    force_update()
    return redirect('/admin/dashboard')

@bp.route('/archive', methods=['GET'])
def archive():
    user_id = request.cookies.get('archive')
    levels = get_levels_array()
    if user_id:
        user_levels = get_user_progress(user_id)
    else:
        user_levels = {}
    return render_template('archive.html', levels=levels, user_levels=user_levels)

@bp.route("/archive/<int:n>", methods=['GET', 'POST'])
def archive_level(n):
    secret_key = request.environ.get('FLASK_SECRET_KEY', 'dev')
    # Check if there's an active session
    if not g.archive_session:
        archive_id = str(uuid.uuid4())
        g.archive_session = ModelData(get_archive(n))
        save_session(archive_id, g.archive_session)

        # set archive_id cookie
        encrypted_archive_data = encrypt_cookie_data([archive_id, n], secret_key)
        response = make_response(redirect('/archive/' + str(n)))
        response.set_cookie('archive_id', encrypted_archive_data,  httponly=True)

        # Log usage
        print(f"*Start (A)* New user started level {n} with id {archive_id}")
        return response
    
    archive_cookie = request.cookies.get('archive_id')
    archive_data = decrypt_cookie_data(archive_cookie, secret_key)
    archive_id = archive_data[0]
    
    if request.method == 'GET':
        g.archive_session.get_clues()
        g.archive_session.startTimer()
        save_session(archive_id, g.archive_session)

        return render_template('archive_level.html', clue1=g.archive_session.clue1, clue2=g.archive_session.clue2, correct=False,
                        count1=g.archive_session.count1, count2=g.archive_session.count2, newclue=True, response=g.archive_session.response, 
                        answer1 = g.archive_session.answer1, in_between = g.archive_session.inbetween, answer2 = g.archive_session.answer2)
    else:
        submit_action = request.form.get('submit_action')

        if submit_action == 'back':
            response = make_response(redirect('/archive'))
            delete_session(archive_id)
            response.delete_cookie('archive_id')

            # Log usage
            print(f"*Progress* User ({archive_id}) went back to archive.")
            return response
        else:
            g.archive_session.answer1 = request.form['answer1']
            g.archive_session.inbetween = request.form['in_between']
            g.archive_session.answer2 = request.form['answer2']
            hint = g.archive_session.check_answer(g.archive_session.answer1, g.archive_session.inbetween, g.archive_session.answer2)

            if g.archive_session.correct:
                time = g.archive_session.stopTimer()
                
                # Get the existing stats from cookies
                user_id = request.cookies.get('archive')

                if user_id == None:
                    user_id = str(uuid.uuid4())

                # Update the stats
                save_level_completion(user_id, n)

                # Update archive cookies
                max_age = 10 * 365 * 24 * 60 * 60 # 10 years!!
                response = make_response(render_template('congrats.html', time=time, level=n))
                
                response.set_cookie('archive', user_id, max_age=max_age,  httponly=True)
                delete_session(archive_id)
                response.delete_cookie('archive_id')

                # Log usage
                print(f"*Completion* User ({user_id}) submitted level {n} in {time}s.")
                return response
            else:
                # Log progress
                result = g.archive_session.getResponse()
                save_session(archive_id, g.archive_session)

                print(f"*Progress* A user submitted an incorrect answer for level {n}: ({result})")

                return render_template('archive_level.html', clue1=g.archive_session.clue1, clue2=g.archive_session.clue2, answer1=g.archive_session.answer1, 
                                    in_between=g.archive_session.inbetween, answer2=g.archive_session.answer2, response=g.archive_session.response, 
                                    correct=g.archive_session.correct, count1=g.archive_session.count1, count2=g.archive_session.count2, newclue=False, hint=hint)


