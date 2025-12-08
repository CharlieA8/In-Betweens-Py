import game.db_setup as db
from game.session_management import clear_all_sessions
from game.answer_management import update_answers
from game.archive_management import filter_old_users

# daily update script
if __name__ == "__main__":
    db.setup_db_pool()
    clear_all_sessions()
    print(update_answers())
    print(filter_old_users())
    db.connection_pool.closeall()