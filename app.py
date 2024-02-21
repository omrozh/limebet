import datetime
import os.path

import flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_required, login_user, UserMixin, logout_user
from flask_bcrypt import Bcrypt
import requests

import shortuuid
import feedparser
import base64
import telegram
from imap_tools import MailBox

app = flask.Flask(__name__)

app.config["SECRET_KEY"] = "ksjf-sjc-wsf12-sac"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

db = SQLAlchemy(app)

login_manager = LoginManager(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)


# TEST APP PASSWORD for kadromilyon@gmail.com: dbpixumfhzuvkvzu

def get_unread_emails(username, password):
    with MailBox('imap.gmail.com').login(username, password, 'INBOX') as mailbox:
        data = [(msg.subject, msg.text) for msg in mailbox.fetch()]


def get_unread_email(username, password):
    atom_feed_url = f"https://mail.google.com/mail/feed/atom"

    auth_str = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {"Authorization": f"Basic {auth_str}"}
    response = feedparser.parse(requests.get(atom_feed_url, headers=headers).text)

    unread_emails = []

    for entry in response.entries:
        sender = entry.author
        subject = entry.title
        summary = entry.summary

        unread_emails.append({"sender": sender, "subject": subject, "summary": summary})

    return unread_emails


class Referrer(db.Model):
    id = db.Column(db.String, primary_key=True)
    user_fk = db.Column(db.Integer)
    commission_rate = db.Column(db.Float)

    @property
    def user(self):
        return User.query.get(self.user_fk)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    is_admin = db.Column(db.Boolean, default=False)
    balance = db.Column(db.Float, default=0)
    referred_by = db.Column(db.String)

    @property
    def mybets(self):
        return BetCoupon.query.filter_by(user_fk=self.id).all()

    def update_balance(self):
        transactions = TransactionLog.query.filter_by(user_fk=self.id).filter_by(transaction_status="initiated").all()
        emails = get_unread_email("omrozh@gmail.com", "hikwdlfeucjrijxe")
        for i in transactions:
            if i.transaction_date < datetime.datetime.today().date() - datetime.timedelta(days=2):
                i.transaction_status = "cancelled"
            # TO DO: Change email

            for email in emails:

                if "bilgi@papara.com" in email.get("sender"):
                    if i.payment_unique_number in email.get("summary") and \
                            str(i.transaction_amount) == str(email.get("subject").split(" ")[1]).replace(",", "."):

                        i.transaction_status = "completed"
                        self.balance += i.transaction_amount
                        if self.referred_by is not None:
                            referrer = Referrer.query.get(self.referred_by)
                            referrer.user.balance += i.transaction_amount / 100 * referrer.commission_rate
                        db.session.commit()

                if "yapikredi@iletisim.yapikredi.com.tr" in email.get("sender"):
                    if email.get("subject") == "Akıllı Asistan-Gelen FAST":
                        for c in email.get("summary").split(" "):
                            if c == "tarihinde,":
                                start_index = email.get("summary").split(" ").index(c)+1
                            if c == "isimli/unvanlı":
                                end_index = email.get("summary").split(" ").index(c)
                        if i.transaction_amount == float(".".join(str(email.get("summary").split(" ")[15]).split(","))):
                            if i.payment_unique_number.upper().upper() == " ".join(email.get("summary").split(" ")[start_index:end_index]):
                                i.transaction_status = "completed"
                                i.payment_unique_number = email.get("summary").split(" ")[8] + " " + email.get("summary").split(" ")[9] + "-" + str(self.id)
                                if not len(TransactionLog.query.filter_by(payment_unique_number=i.payment_unique_number).all()) == 1:
                                    continue
                                else:
                                    self.balance += i.transaction_amount
                                    if self.referred_by is not None:
                                        referrer = Referrer.query.get(self.referred_by)
                                        referrer.user.balance += i.transaction_amount / 100 * referrer.commission_rate
                                db.session.commit()

                    # TO DO: Change this to different bank.

                # Make this support bank transfers as well.

    @property
    def user_information(self):
        user_information = UserInformation.query.filter_by(user_fk=self.id).first()

        if user_information is None:
            user_information = UserInformation(user_fk=self.id, tel_no="", address="", name="")
            db.session.add(user_information)
            db.session.commit()

        return user_information

    @property
    def active_drafts(self):
        drafts_for_user = Draft.query.filter_by(user_fk=self.id).all()
        active_drafts = []
        for i in drafts_for_user:
            if i.competition.end_date >= datetime.datetime.today().date():
                active_drafts.append(i)
        active_drafts.reverse()
        return active_drafts

    @property
    def previous_drafts(self):
        drafts_for_user = Draft.query.filter_by(user_fk=self.id).all()
        active_drafts = []
        for i in drafts_for_user:
            if i.competition.end_date < datetime.datetime.today().date():
                active_drafts.append(i)
        active_drafts.reverse()
        return active_drafts


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String)

    def add_image(self, image_url):
        img_data = requests.get(image_url).content
        with open("static/" + self.team_name + ".png", 'wb') as handler:
            handler.write(img_data)
        db.session.commit()


@login_manager.user_loader
def user_loader(user_id):
    user = User.query.get(user_id)
    return user


class UserInformation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    tel_no = db.Column(db.String)
    user_fk = db.Column(db.Integer)
    address = db.Column(db.String)
    date_of_birth = db.Column(db.String)
    tc_kimlik_no = db.Column(db.Integer)


class OpenBet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_match_id = db.Column(db.String)
    bet_ending_datetime = db.Column(db.DateTime)
    league_icon_url = db.Column(db.String)
    match_league = db.Column(db.String)
    team_1 = db.Column(db.String)
    team_2 = db.Column(db.String)

    def update_results(self):
        from betting_utils import get_results
        get_results(self.api_match_id)

    @property
    def bet_options(self):
        return BetOption.query.filter_by(open_bet_fk=self.id).all()


class BetCoupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_fk = db.Column(db.Integer)
    total_value = db.Column(db.Float, default=0)
    status = db.Column(db.String, default="Oluşturuluyor")

    @property
    def all_selects(self):
        return BetSelectedOption.query.filter_by(bet_coupon_fk=self.id).all()

    @property
    def total_odd(self):
        total_odd = 1
        for i in BetSelectedOption.query.filter_by(bet_coupon_fk=self.id).all():
            total_odd *= i.odd.odd

        return total_odd

    @property
    def odd_options(self):
        if self.status == "Oluşturuluyor":
            for i in self.all_selects:
                if i.odd.ended:
                    db.session.delete(i)
                    db.session.commit()
        return [i.odd for i in self.all_selects]

    def is_successful(self):
        all_success = True
        for i in BetSelectedOption.query.filter_by(bet_coupon_fk=self.total_value).all():
            if i.odd.status == "Sonuçlanmadı":
                self.status = "Sonuçlanmadı"
                db.session.commit()
                return 0

            if i.odd.status == "Başarısız":
                all_success = False

        return all_success

    def give_reward(self):
        all_success = True
        total_odd = 1
        for i in BetSelectedOption.query.filter_by(bet_coupon_fk=self.total_value).all():
            if i.odd.status == "Sonuçlanmadı":
                self.status = "Sonuçlanmadı"
                db.session.commit()
                return 0

            if i.odd.status == "Başarısız":
                all_success = False

            total_odd *= i.odd.odd
        if all_success:
            self.status = "Başarısız"
            db.session.commit()
            return 0

        else:
            User.query.get(self.user_fk).balance = self.total_value * total_odd
            db.session.commit()
            self.status = "Başarılı"
            db.session.commit()
            return 0


class BetSelectedOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bet_odd_fk = db.Column(db.Integer)
    bet_coupon_fk = db.Column(db.Integer)

    @property
    def odd(self):
        return BetOdd.query.get(self.bet_odd_fk)


class BetOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_name = db.Column(db.String)
    game_details = db.Column(db.String)
    open_bet_fk = db.Column(db.Integer)
    match_name_row = db.Column(db.String)

    @property
    def match_name(self):
        open_bet = OpenBet.query.get(self.open_bet_fk)
        if not open_bet:
            return self.match_name_row
        self.match_name_row = open_bet.team_1 + " - " + open_bet.team_2
        db.session.commit()
        return self.match_name_row

    @property
    def bet_odds(self):
        return BetOdd.query.filter_by(bet_option_fk=self.id).all()


class BetOdd(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String)
    odd = db.Column(db.Float)
    value = db.Column(db.String)
    bet_option_fk = db.Column(db.Integer)
    status = db.Column(db.String, default="Sonuçlanmadı")

    @property
    def ended(self):
        return OpenBet.query.get(BetOption.query.get(self.bet_option_fk).open_bet_fk).bet_ending_datetime < datetime.datetime.now()

    @property
    def bet_option(self):
        return BetOption.query.get(self.bet_option_fk)

    @property
    def user_selected(self):
        current_coupon = BetCoupon.query.filter_by(user_fk=current_user.id).filter_by(status="Oluşturuluyor").first()
        if not current_coupon:
            return False
        selected_odds = [i.bet_odd_fk for i in BetSelectedOption.query.filter_by(bet_coupon_fk=current_coupon.id)]
        return self.id in selected_odds


class TransactionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_amount = db.Column(db.Float)
    transaction_type = db.Column(db.String)
    transaction_status = db.Column(db.String, default="initiated")
    transaction_date = db.Column(db.Date)
    payment_information_fk = db.Column(db.Integer)
    user_fk = db.Column(db.Integer)
    payment_unique_number = db.Column(db.String)


class WithdrawalRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    withdrawal_amount = db.Column(db.Float)
    status = db.Column(db.String, default="Beklemede")
    user_fk = db.Column(db.Integer)
    withdraw_to = db.Column(db.String)

    @property
    def user(self):
        return User.query.get(self.user_fk)

    @property
    def full_info(self):
        return UserInformation.query.filter_by(user_fk=self.user_fk).first().name + "/" + self.withdraw_to


class BankInformation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    iban = db.Column(db.String)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    user_fk = db.Column(db.String)


class Draft(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_fk = db.Column(db.String)
    draft_name = db.Column(db.String)
    competition_fk = db.Column(db.Integer)

    def give_prize_to_user(self):
        self.user.balance += self.competition.calculate_prize_by_point(self.total_points)
        db.session.commit()

    @property
    def user(self):
        return User.query.get(self.user_fk)

    @property
    def competition(self):
        return Competition.query.get(self.competition_fk)

    @property
    def chosen_athletes(self):
        return [i for i in DraftedAthlete.query.filter_by(draft_fk=self.id).all()]

    @property
    def total_points(self):
        return sum([i.current_points for i in DraftedAthlete.query.filter_by(draft_fk=self.id).all()])

    @property
    def draft_value(self):
        return sum([i.athlete.athlete_cost for i in DraftedAthlete.query.filter_by(draft_fk=self.id).all()])

    @property
    def current_rank(self):
        return self.competition.calculate_rank_by_point(self.total_points)

    @property
    def current_prize(self):
        return self.competition.calculate_prize_by_point(self.total_points)


class Competition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    competition_name = db.Column(db.String)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    entry_fee = db.Column(db.Float)
    competition_type = db.Column(db.String)
    allow_multiple_entries = db.Column(db.Boolean)

    # prize properties
    highest_prize = db.Column(db.Float)
    max_number_of_participants = db.Column(db.Integer)
    prize_winners = db.Column(db.Integer)
    prize_decrease_multiplier = db.Column(db.Integer)
    minimum_prize = db.Column(db.Float)
    manual_prize_override = db.Column(db.String)

    @property
    def participant_max(self):
        return self.max_number_of_participants if \
            self.max_number_of_participants > self.total_participants else "Yarışma Dolu"

    @property
    def available_athletes(self):
        matches_between_dates = Match.query.filter(self.start_date <= Match.date).filter(
            self.end_date >= Match.date).filter_by(match_league=self.competition_type).all()
        all_available_athletes = []
        for i in matches_between_dates:
            for c in Athlete.query.filter_by(team_fk=i.team1_fk).all():
                all_available_athletes.append(c)
            for c in Athlete.query.filter_by(team_fk=i.team2_fk).all():
                all_available_athletes.append(c)
        return set(all_available_athletes)

    @property
    def prize_pool(self):
        total_price = self.highest_prize
        temp_price = self.highest_prize

        manual_override = self.manual_prize_override
        prize_ranges = {}

        if manual_override is not None:
            total_price = 0
            for i in manual_override.split("/"):
                prize_ranges[i.split(":")[0]] = float(i.split(":")[-1])
            for i in prize_ranges.keys():
                try:
                    number_of_people_in_range = int(i.split("-")[-1]) - int(i.split("-")[0])+1
                except IndexError:
                    number_of_people_in_range = 1
                prize_in_range = number_of_people_in_range * int(prize_ranges.get(i))
                total_price += prize_in_range
            return total_price

        for i in range(self.prize_winners):
            temp_price = temp_price / self.prize_decrease_multiplier if temp_price / self.prize_decrease_multiplier > self.minimum_prize else self.minimum_prize
            total_price += temp_price

        return total_price

    @property
    def total_participants(self):
        return Draft.query.filter_by(competition_fk=self.id).count()

    @property
    def all_prizes(self):
        all_prizes = {}
        temp_price = self.highest_prize
        manual_override = self.manual_prize_override
        prize_ranges = {}

        if manual_override is not None:
            for i in manual_override.split("/"):
                prize_ranges[i.split(":")[0]] = float(i.split(":")[-1])

            return prize_ranges

        for i in range(self.prize_winners):
            if temp_price in all_prizes.values():
                all_prizes.pop(i)
                all_prizes[str(i) + "-" + str(self.prize_winners)] = self.minimum_prize
                return all_prizes
            all_prizes[i + 1] = temp_price
            temp_price = temp_price / self.prize_decrease_multiplier if temp_price / self.prize_decrease_multiplier > self.minimum_prize else self.minimum_prize

        return all_prizes

    def calculate_players_by_point(self, point):
        num_of_players_at_point = 0
        for c in Draft.query.filter_by(competition_fk=self.id):
            if sum([i.current_points for i in DraftedAthlete.query.filter_by(draft_fk=c.id).all()]) == point:
                num_of_players_at_point += 1
        return num_of_players_at_point

    def calculate_prize_by_point(self, point):
        drafts = Draft.query.filter_by(competition_fk=self.id).all()
        draft_ranking = []

        for draft in drafts:
            total_points = 0
            drafted_athletes = DraftedAthlete.query.filter_by(draft_fk=draft.id).all()

            for drafted_athlete in drafted_athletes:
                athlete_points = Points.query.filter_by(athlete_fk=drafted_athlete.athlete_fk).filter(
                    Points.point_date >= self.start_date).filter(Points.point_date <= self.end_date).all()
                if athlete_points:
                    for i in athlete_points:
                        total_points += i.points

            draft_ranking.append({'draft_id': draft.id, 'total_points': total_points})

        draft_ranking.sort(key=lambda x: x['total_points'], reverse=True)

        ranking = next((i + 1 for i, d in enumerate(draft_ranking) if d['total_points'] == point), None)
        if self.manual_prize_override is not None:
            for i in self.manual_prize_override.split("/"):
                prize_range = i.split(":")[0]
                try:
                    if int(prize_range.split("-")[1]) >= ranking >= int(prize_range.split("-")[0]):
                        return float(i.split(":")[-1]) / self.calculate_players_by_point(point)
                except IndexError:
                    if ranking == int(prize_range):
                        return float(i.split(":")[-1]) / self.calculate_players_by_point(point)


        ranking -= 1
        customer_price = self.highest_prize

        if ranking > self.prize_winners:
            return 0

        for i in range(ranking):
            customer_price = customer_price / self.prize_decrease_multiplier if customer_price / self.prize_decrease_multiplier > self.minimum_prize else self.minimum_prize

        final_prize = customer_price / self.calculate_players_by_point(point)

        return final_prize

    @property
    def drafts(self):
        return Draft.query.filter_by(competition_fk=self.id).all()

    def calculate_rank_by_point(self, point):
        drafts = Draft.query.filter_by(competition_fk=self.id).all()
        draft_ranking = []

        for draft in drafts:
            total_points = 0
            drafted_athletes = DraftedAthlete.query.filter_by(draft_fk=draft.id).all()

            for drafted_athlete in drafted_athletes:
                athlete_points = Points.query.filter_by(athlete_fk=drafted_athlete.athlete_fk).filter(
                    Points.point_date >= self.start_date).filter(Points.point_date <= self.end_date).all()
                if athlete_points:
                    for i in athlete_points:
                        total_points += i.points

            draft_ranking.append({'draft_id': draft.id, 'total_points': total_points})

        draft_ranking.sort(key=lambda x: x['total_points'], reverse=True)

        ranking = next((i + 1 for i, d in enumerate(draft_ranking) if d['total_points'] == point), None)

        return ranking


class Athlete(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    athlete_name = db.Column(db.String)
    athlete_cost = db.Column(db.Float)
    athlete_position = db.Column(db.String)
    team_fk = db.Column(db.Integer)
    image_url = db.Column(db.String)

    def add_image(self, image_url):
        img_data = requests.get(image_url).content
        with open("static/" + self.athlete_name + ".png", 'wb') as handler:
            handler.write(img_data)
        self.image_url = "set"
        db.session.commit()

    @property
    def image_is_set(self):
        if self.image_url == "set":
            return "Evet"
        else:
            return "Hayır"

    @property
    def team_name(self):
        return Team.query.get(self.team_fk).team_name


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    team1_fk = db.Column(db.Integer)
    team2_fk = db.Column(db.Integer)
    match_league = db.Column(db.String)


class Points(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Integer)
    athlete_fk = db.Column(db.Integer)
    point_date = db.Column(db.Date)
    # How it works: Enter points for each athlete for every day. Use start and end dates of competitions to calculate
    # points per competition


class DraftedAthlete(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    athlete_fk = db.Column(db.String)
    draft_fk = db.Column(db.String)

    @property
    def athlete(self):
        return Athlete.query.get(self.athlete_fk)

    @property
    def calculate_reward(self):
        related_draft = Draft.query.get(self.draft_fk)
        return related_draft.competition.calculate_prize_by_point(self.current_points)

    @property
    def current_points(self):
        current_competition = Draft.query.get(self.draft_fk).competition
        all_points = Points.query.filter_by(athlete_fk=self.athlete_fk). \
            filter(current_competition.start_date <= Points.point_date). \
            filter(current_competition.end_date >= Points.point_date).all()
        return sum([i.points for i in all_points])


@app.route("/admin_console", methods=["POST", "GET"])
def admin_console():
    if not current_user.is_admin:
        return flask.redirect("/")
    if flask.request.method == "POST":
        if flask.request.values["command"] == "help":
            return '''
                distribute-rewards
                <br>
                // Ödülleri günlük dağıt
                <br>

                add-image <oyuncu_adı> <görsel_url>
                <br>
                // Oyuncuya görsel ekle
                <br>

                add-referrer <öneri_kodu> <kullanıcı_emaili> <komisyon_oranı>
                <br>
                // Affiliate ekle
                <br>
                
                add-team <takım_adı> <görsel_url>
                <br>
                // Takım ekle
                <br>
                
                add-athlete <oyuncu_adı> <oyuncu_maliyeti> <takım_adı>
                <br>
                // Oyuncu ekle
                <br>
                
                add-match <maçın_bugünden_kaç_gün_sonra_olacağı> <takım_1> <takım_2> <maçın_ligi>
                <br>
                // Maç ekle
                <br>
                
                change-request-status <status_id> <new_status>
                <br>
                // Ödeme Statüsü Değiştir
                <br>
                
                add-points <puan_miktarı> <oyuncu_adı> <puanın_kaç_gün_önce_kazanıldığı>
                <br>
                // Puan ekle
                <br>
                
                remove-athlete <oyuncu_adı>
                <br>
                // Oyuncuyu sil
                <br>
                
                list-players
                <br>
                // Oyuncuların listesi
                <br>
                
                list-teams
                <br>
                // Takımların listesi 
            '''.replace("<", "[").replace(">", "]").replace("[br]", "<br>")
        elif "add-team" in flask.request.values["command"]:
            new_team = Team(team_name=flask.request.values["command"].split(" ")[1].replace("-", " "))
            db.session.add(new_team)
            db.session.commit()
            new_team.add_image(flask.request.values["command"].split(" ")[2])
        elif "add-image" in flask.request.values["command"]:
            Athlete.query.filter_by(athlete_name=flask.request.values["command"].split(" ")[1].replace("-", " ")).first().add_image(flask.request.values["command"].split(" ")[2])
            db.session.commit()
        elif "list-players" == flask.request.values["command"]:
            return str("<br>".join(i.athlete_name + " / Görsel Eklendi: " + i.image_is_set for i in Athlete.query.all()))
        elif "list-teams" == flask.request.values["command"]:
            return str("<br>".join(i.team_name for i in Team.query.all()))
        else:
            os.system("python3 util.py " + flask.request.values["command"])

    withdrawal_requests = WithdrawalRequest.query.filter(WithdrawalRequest.status != "Tamamlandı").\
        filter(WithdrawalRequest.status != "Reddedildi").all()
    return flask.render_template("admin_console.html", withdrawal_requests=reversed(withdrawal_requests))


@app.route("/howtoplay")
def how_to_play():
    return flask.render_template("how_to_play.html", current_user=current_user)
    # TO DO: write a how to play page.


@app.route("/logout")
def logout():
    logout_user()
    return flask.redirect("/")


@app.route("/telegram/bot", methods=["POST", "GET"])
async def telegram_bot():
    competitions = Competition.query.filter(
        Competition.start_date >= datetime.datetime.today().date() + datetime.timedelta(days=1))
    try:
        chat_id = dict(flask.request.json).get("message").get("from").get("id")
        message = dict(flask.request.json).get("message").get("text")
    except:
        return "OK"
    if not message:
        return "OK"

    bot = telegram.Bot("7067705563:AAECNO-7EapKCIvce0xWCR8oIRAlS1N1Uj4")

    if message == "/yarismalar":
        await bot.send_message(
            text="\n".join([i.competition_name + ": " + str(i.prize_pool) + "₺" for i in competitions]),
            chat_id=chat_id)

    if "/katil" in message:
        await bot.send_message(
            text=f"https://kadromilyon.com/competition/{competitions.filter_by(competition_name=message.replace('/katil ', '')).first().id}",
            chat_id=chat_id)

    if message == "/yardım":
        await bot.send_message(chat_id=chat_id, text="\nAktif yarışmaları ve ödül havuzlarını görmek için: /yarismalar yaz\n Bir yarışmaya katılmak için: /katil [yarışma adını buraya yaz] yaz gönder.")

    else:
        await bot.send_message(chat_id=chat_id, text="Yardım için /yardım yaz gönder!")

    return "OK"


@app.route("/profile", methods=["POST", "GET"])
def profile():
    if not current_user.is_authenticated:
        return flask.redirect("/")
    if flask.request.method == "POST":
        values = flask.request.values
        if flask.request.values["form-type"] == "user-info":
            user_info = UserInformation.query.filter_by(user_fk=current_user.id).first()

            user_info.name = values["name"]
            user_info.address = values["address"]
            user_info.tel_no = values["telno"]

            db.session.commit()

            return flask.redirect("/profile")
        if flask.request.values["form-type"] == "withdraw-money":
            new_wr = WithdrawalRequest(
                withdrawal_amount=float(flask.request.values["amount"]),
                user_fk=current_user.id,
                withdraw_to=flask.request.values["iban"]
            )
            db.session.add(new_wr)
            db.session.commit()

    return flask.render_template("profile.html", current_user=current_user, withdrawal_requests=reversed(WithdrawalRequest.query.filter_by(user_fk=current_user.id).all()))


@app.route("/")
def index():
    competitions = Competition.query.filter(
        Competition.start_date >= datetime.datetime.today().date()+datetime.timedelta(days=1))
    filter_q = flask.request.args.get("filter_q", False)
    if filter_q:
        if filter_q == "daily":
            competitions = competitions.filter(Competition.start_date == Competition.end_date)
        elif filter_q == "weekly":
            competitions = competitions.filter(Competition.start_date != Competition.end_date)
        elif filter_q == "high_limit":
            competitions = competitions.filter(Competition.entry_fee > 50)
        elif filter_q == "low_participants":
            competitions = competitions.filter(Competition.max_number_of_participants < 5001)
        elif filter_q == "single_participation":
            competitions = competitions.filter(not Competition.allow_multiple_entries)
        elif filter_q == "multiple_participation":
            competitions = competitions.filter(Competition.allow_multiple_entries)
        elif filter_q == "high_reward":
            competitions = competitions.filter(Competition.highest_prize > 50000)
        elif filter_q == "cheap_entry":
            competitions = competitions.filter(Competition.entry_fee < 20)
        elif filter_q == "seasonal":
            competitions = competitions.filter(Competition.start_date != Competition.end_date)
        else:
            competitions = competitions.filter(Competition.competition_type == filter_q.replace("-", " "))

    resp = flask.make_response(flask.render_template("index.html", current_user=current_user,
                                                     competitions=competitions.all()))
    if flask.request.args.get("ref", False):
        resp.set_cookie('referrer', flask.request.args.get("ref"))

    return resp


@app.route("/competition/<competition_id>")
def competition(competition_id):
    if Competition.query.get(competition_id).total_participants >= \
            Competition.query.get(competition_id).max_number_of_participants:
        return flask.redirect("/")

    if not current_user.is_authenticated:
        return flask.redirect("/login")
    return flask.render_template("competition.html", competition=Competition.query.get(competition_id))


@app.route("/refresh-balance")
@login_required
def refresh_balance():
    current_user.update_balance()
    return "%.2f" % current_user.balance


@app.route("/deposit/bank", methods=["POST", "GET"])
def deposit_bank():
    if flask.request.method == "POST":
        values = flask.request.values
        if float(values["transaction_amount"]) < 500:
            return flask.redirect("/deposit/bank")
        new_transaction = TransactionLog(transaction_amount=float(values["transaction_amount"]),
                                         transaction_type="bank", transaction_date=datetime.date.today(),
                                         user_fk=current_user.id,
                                         payment_unique_number=flask.request.values["name"])
        db.session.add(new_transaction)
        db.session.commit()
        return flask.render_template("bank_deposit.html", fullname="Ömer Özhan", iban="TR91 0006 7010 0000 0096 8371 49")
    return flask.render_template("bank_deposit_form.html")


@app.route("/deposit/papara", methods=["POST", "GET"])
def deposit_papara():
    if flask.request.method == "POST":
        values = flask.request.values
        if float(values["transaction_amount"]) < 200:
            return flask.redirect("/deposit/papara")
        new_transaction = TransactionLog(transaction_amount=float(values["transaction_amount"]),
                                         transaction_type="papara", transaction_date=datetime.date.today(),
                                         user_fk=current_user.id,
                                         payment_unique_number=str(shortuuid.ShortUUID().random(length=8)))
        db.session.add(new_transaction)
        db.session.commit()
        return flask.render_template("papara_deposit.html", transaction=new_transaction, papara_no="8405869792")
    return flask.render_template("papara_deposit_form.html")


@app.route("/athlete/image/<a_id>")
def athlete_image(a_id):
    athlete = Athlete.query.get(a_id)
    if athlete.image_url:
        return flask.send_file("static/" + athlete.athlete_name + ".png" if os.path.exists(
            "static/" + athlete.athlete_name + ".png") else "/static/player.png")
    return flask.send_file("static/" + athlete.team_name + ".png")


@app.route("/draft/<competition_id>", methods=["POST", "GET"])
def draft(competition_id):
    if not current_user.is_authenticated:
        return flask.redirect("/")

    current_competition = Competition.query.get(competition_id)

    if not current_competition.start_date >= datetime.datetime.today().date()+datetime.timedelta(days=1):
        return "Unauthorized"

    if flask.request.method == "POST":
        if current_user.balance < current_competition.entry_fee:
            return '''
                <script>
                    alert('Yetersiz bakiye')
                    document.location = '/'
                </script>
            '''
        current_user.balance -= current_competition.entry_fee

        values = flask.request.values
        if len(Draft.query.filter_by(user_fk=current_user.id).filter_by(competition_fk=competition_id).all()) > 0 \
                and not current_competition.allow_multiple_entries:
            return '''
                <script>
                    alert('Bu yarışmaya birden fazla kez katılamazsınız.')
                </script>
            '''

        new_draft = Draft(user_fk=current_user.id, draft_name=current_competition.competition_name,
                          competition_fk=competition_id)
        db.session.add(new_draft)
        db.session.commit()

        drafted_athletes = []
        draft_id = new_draft.id

        for i in values.keys():
            if "athlete" in i:
                if values[i]:
                    new_draft = DraftedAthlete(athlete_fk=int(values[i]), draft_fk=draft_id)
                    drafted_athletes.append(new_draft)
                    db.session.add(new_draft)

        total_cost_of_draft = 0

        for i in drafted_athletes:
            total_cost_of_draft += i.athlete.athlete_cost

        if total_cost_of_draft > 50000:
            return "Hatalı Seçim"

        db.session.commit()
        return flask.render_template("completed_draft.html")

    return flask.render_template("draft.html", competition=current_competition,
                                 desktop=flask.request.args.get("desktop", False), mobile=flask.request.args.get("mobile", False))


@app.route("/static/<filename>")
def static_file(filename):
    return flask.send_file("static/" + filename)


@app.route("/admin", methods=["POST", "GET"])
def admin():
    if not current_user.is_admin:
        return ""
    return flask.render_template("admin.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if flask.request.method == "POST":
        values = flask.request.values
        user_from_email = User.query.filter_by(email=values["email"]).first()
        if user_from_email:
            if bcrypt.check_password_hash(user_from_email.password, values["password"]):
                login_user(user_from_email, remember=True)
                return flask.redirect("/")
    return flask.render_template("login.html")


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if flask.request.method == "POST":
        values = flask.request.values
        new_user = User(
            username=values["username"],
            email=values["email"],
            password=bcrypt.generate_password_hash(values["password"]),
            referred_by=flask.request.cookies.get('somecookiename', None)
        )
        db.session.add(new_user)
        db.session.commit()
        new_user.user_information.tel_no = flask.request.values["tel_no"]
        db.session.commit()
        return flask.redirect("/login")
    return flask.render_template("signup.html")


@app.route("/admin_portal", methods=["POST", "GET"])
def admin_portal():
    if not current_user.is_admin:
        return flask.redirect("/")

    if flask.request.method == "POST":
        values = flask.request.values
        new_competition = Competition(
            competition_name=values["competition_name"],
            start_date=datetime.datetime.strptime(values["start_date"], '%Y-%m-%d'),
            end_date=datetime.datetime.strptime(values["end_date"], '%Y-%m-%d'),
            entry_fee=float(values["entry_fee"]),
            competition_type=values["competition_type"],
            highest_prize=float(values["highest_prize"]),
            max_number_of_participants=int(values["max_number_of_participants"]),
            prize_winners=int(values["prize_winners"]),
            prize_decrease_multiplier=float(values["prize_decrease_multiplier"]),
            minimum_prize=float(values["minimum_prize"]),
            allow_multiple_entries=bool(values.get("allow_multiple_entries", False))
        )
        db.session.add(new_competition)
        db.session.commit()
        return flask.redirect("/")
    return flask.render_template("admin.html")


@app.route("/bahis")
def bahis():
    open_bets = OpenBet.query.filter(OpenBet.bet_ending_datetime > datetime.datetime.now()).all()
    return flask.render_template("bahis/bahis.html", open_bets=open_bets)


@app.route("/bahis/mac/<bahis_id>")
def bahis_mac(bahis_id):
    open_bet = OpenBet.query.get(bahis_id)
    return flask.render_template("bahis/bahis_detay.html", open_bet=open_bet)


@app.route("/take_bet/<odd_id>")
def take_bet(odd_id):
    if not current_user.is_authenticated:
        return flask.redirect("/login")
    current_coupon = BetCoupon.query.filter_by(user_fk=current_user.id).filter_by(status="Oluşturuluyor").first()
    if not current_coupon:
        current_coupon = BetCoupon(user_fk=current_user.id, status="Oluşturuluyor", total_value=0)
        db.session.add(current_coupon)
        db.session.commit()
    if BetSelectedOption.query.filter_by(bet_odd_fk=odd_id).filter_by(bet_coupon_fk=current_coupon.id).first():
        return flask.redirect("/bahis")
    new_coupon_bet = BetSelectedOption(bet_coupon_fk=current_coupon.id, bet_odd_fk=odd_id)
    db.session.add(new_coupon_bet)
    db.session.commit()
    option_fk = BetOdd.query.get(odd_id).bet_option_fk
    option = BetOption.query.get(option_fk)
    return flask.redirect(f"/bahis/mac/{option.open_bet_fk}")


@app.route("/remove_bet/<odd_id>")
def remove_bet(odd_id):
    current_coupon = BetCoupon.query.filter_by(user_fk=current_user.id).filter_by(status="Oluşturuluyor").first()
    db.session.delete(BetSelectedOption.query.filter_by(bet_odd_fk=odd_id).filter_by(bet_coupon_fk=current_coupon.id).first())
    db.session.commit()
    option_fk = BetOdd.query.get(odd_id).bet_option_fk
    option = BetOption.query.get(option_fk)

    return flask.redirect(f"/bahis/mac/{option.open_bet_fk}")


@app.route("/coupon", methods=["POST", "GET"])
def coupon():
    if not current_user.is_authenticated:
        return flask.redirect("/login")
    current_coupon = BetCoupon.query.filter_by(user_fk=current_user.id).filter_by(status="Oluşturuluyor").first()
    if not current_coupon:
        current_coupon = BetCoupon(user_fk=current_user.id, status="Oluşturuluyor", total_value=0)
        db.session.add(current_coupon)
        db.session.commit()
    if flask.request.method == "POST":
        if current_user.balance < float(flask.request.values["coupon_value"]):
            return '''
                <script>
                    alert('Yetersiz bakiye')
                    document.location = '/coupon'
                </script>
            '''
        current_coupon.status = "Oluşturuldu"
        current_coupon.total_value = float(flask.request.values["coupon_value"])
        current_user.balance -= float(flask.request.values["coupon_value"])
        db.session.commit()
        return flask.redirect("/profile")
    return flask.render_template("bahis/coupon.html", current_coupon=current_coupon)
