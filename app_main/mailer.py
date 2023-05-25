from app_main import app, params
from flask_mail import Mail, Message
from flask import make_response
from app_main.api import token_required, verify_user ,admin_only

app.config["MAIL_SERVER"] = "smtp.googlemail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = params["email_mail"]
app.config["MAIL_PASSWORD"] = params["mailer_pass"]


mail = Mail(app)



@app.route("/send")
@token_required
@verify_user
@admin_only
def send_mail(decoded):
    try:
        msg = Message("Warning",sender=params["email"],recipients=[params["email_mail"]])
        msg.body="warning your application is going to expired in one month"
        mail.send(msg)
        return {"sent":True}
    except Exception as e:
        return make_response({
            "message": "Something went wrong",
            "data": None,
            "error": str(e)
        },500)