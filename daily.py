from game.db_setup import setup_db_pool, connection_pool
from game.session_management import clear_all_sessions
from game.answer_management import update_answers
from game.archive_management import filter_old_users

if __name__ == "__main__":
    setup_db_pool()
    clear_all_sessions()
    update_answers()
    filter_old_users()
    connection_pool.closeall()