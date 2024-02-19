from app import app, db, Match, Team, Athlete, Points, Competition, User, Referrer, WithdrawalRequest
from sys import argv
import datetime


if argv[1] == "distribute-rewards":
    limiter = 0
    with app.app_context():
        for i in Competition.query.filter_by(end_date=datetime.datetime.today().date()-datetime.timedelta(days=1)).all():
            for c in i.drafts:
                limiter += 1
                c.give_prize_to_user()
                if limiter > i.prize_winners:
                    break


if argv[1] == "add-image":
    with app.app_context():
        Athlete.query.filter_by(athlete_name=argv[2].replace("-", " ")).first().add_image(argv[3])
        db.session.commit()
        print("image-added")

if argv[1] == "remove-athlete":
    with app.app_context():
        db.session.delete(Athlete.query.filter_by(athlete_name=argv[2].replace("-", " ")).first())
        db.session.commit()


if argv[1] == "add-referrer":
    with app.app_context():
        new_referrer = Referrer(id=argv[2], user_fk=User.query.filter_by(email=argv[3]).first().id,
                                commission_rate=float(argv[4]))
        db.session.add(new_referrer)
        db.session.commit()


if argv[1] == "change-request-status":
    with app.app_context():
        WithdrawalRequest.query.get(argv[2]).status = argv[3]
        if argv[3] == "Tamamlandı":
            WithdrawalRequest.query.get(argv[2]).user.balance -= WithdrawalRequest.query.get(argv[2]).withdrawal_amount
        db.session.commit()


if argv[1] == "add-team":
    with app.app_context():
        new_team = Team(team_name=argv[2].replace("-", " "))
        db.session.add(new_team)
        db.session.commit()
        new_team.add_image(argv[3])

if argv[1] == "list-teams":
    with app.app_context():
        for i in Team.query.all():
            print(i.team_name)

if argv[1] == "add-athlete":
    with app.app_context():
        new_athlete = Athlete(athlete_name=argv[2].replace("-", " "), athlete_cost=float(argv[3]),
                              team_fk=Team.query.filter_by(team_name=argv[4].replace("-", " ")).first().id)
        db.session.add(new_athlete)
        db.session.commit()
        print("athlete-added")

if argv[1] == "add-match":
    with app.app_context():
        new_match = Match(
            date=(datetime.datetime.today() + datetime.timedelta(days=int(argv[2]))).date(),
            team1_fk=Team.query.filter_by(team_name=argv[3]).first().id,
            team2_fk=Team.query.filter_by(team_name=argv[4].replace("-", " ")).first().id,
            match_league=argv[5].replace("-", " ")
        )
        db.session.add(new_match)
        db.session.commit()
        print("add match")


if argv[1] == "add-points":
    with app.app_context():
        new_point = Points(
            points=int(argv[2]),
            athlete_fk=Athlete.query.filter_by(athlete_name=argv[3].replace("-", " ")).first().id,
            point_date=(datetime.datetime.today() - datetime.timedelta(days=int(argv[4]))).date()
        )
        db.session.add(new_point)
        db.session.commit()

