from app import BetCoupon, BetOption, BetOdd, BetSelectedOption, OpenBet, app, db

with app.app_context():
    for i in BetCoupon.query.all():
        db.session.delete(i)
    for i in OpenBet.query.all():
        db.session.delete(i)
    for i in BetOption.query.all():
        db.session.delete(i)
    for i in BetOdd.query.all():
        db.session.delete(i)
    for i in BetSelectedOption.query.all():
        db.session.delete(i)

    db.session.commit()
