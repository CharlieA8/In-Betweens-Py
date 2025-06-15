from game.session_management import clear_all_sessions
from game.answer_management import update_answers
from game.archive_management import filter_old_users

if __name__ == "__main__":
    clear_all_sessions()
    update_answers()
    filter_old_users()