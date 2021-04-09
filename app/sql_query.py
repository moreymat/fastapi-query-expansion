import sqlite3
from datetime import datetime

database = "data/user_feedback.db"

# Parameter: Database pointer, sql command, and the data used for the command
# Function: Run the sql command
def run_sql_command(cursor, sql_command, data):

    try:
        if data is not None:
            cursor.execute(sql_command, data)
        else:
            cursor.execute(sql_command)

        record = cursor.fetchall()

        return record

    except sqlite3.Error as error:
        print(
            "\nError while running this command: \n",
            sql_command,
            "\n",
            error,
            "\n",
            data,
            "\n",
        )
        return None


def check_proposed_keyword_already_exist(cursor, search_id, proposed_keyword):

    sqlite_check_proposed_keyword_exist_query = "SELECT id FROM search_expansion_feedback WHERE search_id = ? and keyword_proposed = ?"

    record = run_sql_command(
        cursor,
        sqlite_check_proposed_keyword_exist_query,
        (search_id, proposed_keyword),
    )

    return record


def update_proposed_keyword_feedback(cursor, feedback_id, feedback):

    sqlite_update_result_query = (
        "UPDATE search_expansion_feedback SET feedback = ? WHERE id = ?"
    )

    run_sql_command(cursor, sqlite_update_result_query, (feedback, feedback_id))


def insert_proposed_keyword_feedback(
    cursor, search_id, original_keyword, proposed_keyword, feedback
):

    sqlite_insert_result_query = "INSERT INTO search_expansion_feedback(search_id, keyword_used, keyword_proposed, feedback) VALUES(?, ?, ?, ?);"

    run_sql_command(
        cursor,
        sqlite_insert_result_query,
        (search_id, original_keyword, proposed_keyword, feedback),
    )


# Function: Add a new search entry in the database
def add_new_search_query(
    conversation_id, user_search, date, flag_activate_sql_query_commit
):

    try:

        sqliteConnection = sqlite3.connect(database)
        cursor = sqliteConnection.cursor()

        sqlite_insert_feedback_query = (
            "INSERT INTO search(conversation_id, user_search, date) VALUES(?, ?, ?);"
        )
        run_sql_command(
            cursor, sqlite_insert_feedback_query, (conversation_id, user_search, date),
        )

        if flag_activate_sql_query_commit:
            sqliteConnection.commit()

        cursor.close()
        sqliteConnection.close()

    except sqlite3.Error as error:
        print("-ADD_NEW_SEARCH_QUERY-\nError while connecting to sqlite", error, "\n")


# Function: Add the keyword proposed in the database
def add_proposed_keyword_feedback(
    conversation_id,
    search,
    original_keyword,
    proposed_keyword,
    feedback,
    flag_activate_sql_query_commit,
):

    try:

        sqliteConnection = sqlite3.connect(database)
        cursor = sqliteConnection.cursor()

        search_id = get_search_id(cursor, conversation_id, search)

        if search_id is not None:

            record = check_proposed_keyword_already_exist(
                cursor, search_id, proposed_keyword
            )

            if len(record) > 0:

                update_proposed_keyword_feedback(cursor, record[0][0], feedback)

            else:

                insert_proposed_keyword_feedback(
                    cursor, search_id, original_keyword, proposed_keyword, feedback
                )

            if flag_activate_sql_query_commit:
                sqliteConnection.commit()

        cursor.close()
        sqliteConnection.close()

    except sqlite3.Error as error:
        print("-ADD_FEEDBACK_EXPANSION-\nError while connecting to sqlite", error, "\n")


# Return the search_id corresponding to these parameters
def get_search_id(cursor, conversation_id, user_search):

    try:

        sqlite_get_search_id_query = "SELECT id FROM search where conversation_id = ? and user_search = ? ORDER BY id DESC;"

        record = run_sql_command(
            cursor, sqlite_get_search_id_query, (conversation_id, user_search)
        )

        if len(record) > 0:
            return record[0][0]
        else:
            return None

    except sqlite3.Error as error:
        print("-GET_SEARCH_ID-\nError while connecting to sqlite", error, "\n")
