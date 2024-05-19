from app import TransactionLog, app, User, WithdrawalRequest
from datetime import timedelta
import os


def calculate_transaction_volume_for_date(date_start, date_end, compare_date_delta):
    with app.app_context():
        transactions = TransactionLog.query.filter(
            TransactionLog.transaction_date >= date_start,
            TransactionLog.transaction_date <= date_end,
            TransactionLog.transaction_status == "completed",
            TransactionLog.transaction_type == "yatirim"
        ).all()

        previous_start = date_start - timedelta(days=compare_date_delta)
        previous_end = date_end - timedelta(days=compare_date_delta)
        transactions_compare = TransactionLog.query.filter(
            TransactionLog.transaction_date <= previous_end,
            TransactionLog.transaction_date >= previous_start,
            TransactionLog.transaction_status == "completed",
            TransactionLog.transaction_type == "yatirim"
        ).all()

        transaction_value = sum([t.transaction_amount for t in transactions])

        transaction_value_for_previous_period = sum([t.transaction_amount for t in transactions_compare])

        if transaction_value_for_previous_period > 0:
            percentage_change = transaction_value / transaction_value_for_previous_period * 100
        else:
            percentage_change = 100

        return transaction_value, percentage_change - 100


def calculate_total_balance():
    with app.app_context():
        total = 0
        for i in User.query.all():
            total += i.balance
        return total


def logged_in_users(date_start, date_end, compare_date_delta):
    with app.app_context():

        users_logged_in_within_period = User.query.filter(
            User.last_login <= date_end,
            User.last_login >= date_start
        ).all()

        previous_start = date_start - timedelta(days=compare_date_delta)
        previous_end = date_end - timedelta(days=compare_date_delta)

        users_logged_in_within_previous_period = User.query.filter(
            User.last_login <= previous_end,
            User.last_login >= previous_start
        ).all()

        if len(users_logged_in_within_previous_period) > 0:
            percentage_change = len(users_logged_in_within_period) / users_logged_in_within_previous_period * 100
        else:
            percentage_change = 100

        return len(users_logged_in_within_period), percentage_change - 100


def total_users(date_start, date_end):
    with app.app_context():
        users_logged_in_within_period = User.query.filter(
            User.registration_date <= date_end,
            User.registration_date >= date_start
        ).all()

        users_logged_in_within_previous_period = User.query.all()

        if len(users_logged_in_within_previous_period) > 0:
            percentage_change = len(users_logged_in_within_period) / len(users_logged_in_within_previous_period) * 100
        else:
            percentage_change = int(0)

        return len(users_logged_in_within_period), percentage_change


def total_withdrawals(date_start, date_end, compare_date_delta):
    with app.app_context():
        withdrawal_requests = sum([i.withdrawal_amount for i in WithdrawalRequest.query.filter(
            WithdrawalRequest.request_date <= date_end,
            WithdrawalRequest.request_date >= date_start,
            WithdrawalRequest.request_date == "Tamamlandı"
        ).all()])

        previous_start = date_start - timedelta(days=compare_date_delta)
        previous_end = date_end - timedelta(days=compare_date_delta)
        withdrawal_requests_for_previous_period = sum([i.withdrawal_amount for i in WithdrawalRequest.query.filter(
            WithdrawalRequest.request_date <= previous_end,
            WithdrawalRequest.request_date >= previous_start,
            WithdrawalRequest.request_date == "Tamamlandı"
        ).all()])

        if withdrawal_requests_for_previous_period > 0:
            percentage_change = withdrawal_requests / withdrawal_requests_for_previous_period * 100
        else:
            percentage_change = 100

        return withdrawal_requests, percentage_change - 100


def calculate_ggr(date_start, date_end, compare_date_delta):
    with app.app_context():
        bet_transactions = sum([i.transaction_amount for i in TransactionLog.query.filter(
            TransactionLog.transaction_date >= date_start,
            TransactionLog.transaction_date <= date_end,
            TransactionLog.transaction_status == "completed",
            TransactionLog.transaction_type.in_(["place_bet", "casino_win", "casino_loss"])
        ).all()])
        bet_win_transactions = sum([i.transaction_amount for i in TransactionLog.query.filter(
            TransactionLog.transaction_date <= date_end,
            TransactionLog.transaction_date >= date_start,
            TransactionLog.transaction_status == "completed",
            TransactionLog.transaction_type.in_(["bet_win", "casino_win"])
        ).all()])

        previous_start = date_start - timedelta(days=compare_date_delta)
        previous_end = date_end - timedelta(days=compare_date_delta)

        bet_transactions_for_previous_period = sum([i.transaction_amount for i in TransactionLog.query.filter(
            TransactionLog.transaction_date <= previous_end,
            TransactionLog.transaction_date >= previous_start,
            TransactionLog.transaction_status == "completed",
            TransactionLog.transaction_type.in_(["place_bet", "casino_win", "casino_loss"])
        ).all()])
        bet_win_transactions_for_previous_period = sum([i.transaction_amount for i in TransactionLog.query.filter(
            TransactionLog.transaction_date <= previous_end,
            TransactionLog.transaction_date >= previous_start,
            TransactionLog.transaction_status == "completed",
            TransactionLog.transaction_type.in_(["bet_win", "casino_win"])
        ).all()])

        total_ggr = bet_transactions - bet_win_transactions
        total_ggr_for_previous_period = bet_transactions_for_previous_period - bet_win_transactions_for_previous_period

        if total_ggr_for_previous_period > 0:
            percentage_change = total_ggr / total_ggr_for_previous_period * 100
        else:
            percentage_change = 100

        return total_ggr, percentage_change - 100


def total_bet(date_start, date_end, compare_date_delta):
    with app.app_context():
        bet_transactions = sum([i.transaction_amount for i in TransactionLog.query.filter(
            TransactionLog.transaction_date <= date_end,
            TransactionLog.transaction_date >= date_start,
            TransactionLog.transaction_status == "completed",
            TransactionLog.transaction_type.in_(["place_bet", "casino_win", "casino_loss"])
        ).all()])

        previous_start = date_start - timedelta(days=compare_date_delta)
        previous_end = date_end - timedelta(days=compare_date_delta)

        bet_transactions_for_previous_period = sum([i.transaction_amount for i in TransactionLog.query.filter(
            TransactionLog.transaction_date <= previous_end,
            TransactionLog.transaction_date >= previous_start,
            TransactionLog.transaction_status == "completed",
            TransactionLog.transaction_type.in_(["place_bet", "casino_win", "casino_loss"])
        ).all()])

        if bet_transactions_for_previous_period > 0:
            percentage_change = bet_transactions / bet_transactions_for_previous_period * 100
        else:
            percentage_change = 100

        return bet_transactions, percentage_change - 100


def list_directory_contents_recursive(directory_path):
    contents = []
    for root, dirs, files in os.walk(directory_path):
        for name in dirs:
            contents.append(os.path.join(root, name))
        for name in files:
            contents.append(os.path.join(root, name))
    return contents
