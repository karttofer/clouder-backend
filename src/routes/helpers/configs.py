# Reset Password Configs


def reset_password_messages(pin):
    reset_password_subject = "Password Reset Pin - From Clouder Team ☁️"
    reset_password_body = f"""
<div style="margin: 40px auto; padding: 6% 15px 30px; max-width: 600px; background-color: #fff; border-radius: 5px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
    <div style="display:flex;justify-content:center;align-items:center;">
        <img style="width: 140px;" src="https://www.akc.org/wp-content/uploads/2017/11/Dogo-puppy.jpg"/>
    </div>

    <div style="font-family: 'Roboto', sans-serif; text-align: left;">
        <div style="font-size: 17px; line-height: 25px; color: #4d4d4d; font-weight: normal; margin: 13px 30px;">
            <p style="text-align: left;">Hello,</p>
            <p style="text-align: left;">You have requested to reset your password for <strong>Clouder</strong>. Use the following PIN to reset your password:</p>
            <div style="padding: 24px; font-size: 23px; line-height: 30px; color: #fff; font-weight: bold; background: black; border-radius: 5px; text-align: center;">
                {pin}
            </div>
            <p style="text-align: left;">This code will expire in 1 hour, please verify soon.</p>
            <p style="text-align: left;">If this wasn't you, we highly recommend that you change your password right away. If you are unable to do this, please contact our support center for help.</p>
            <br/>
            <div>
                <p style="text-align: left; margin: 0;">Thank you,</p>
                <p style="text-align: left; margin: 0;">Clouder Team</p>
            </div>
        </div>
        <div style="margin: 0 30px;">
            <p style="height: 1px; background-color: #e5e5e5; border: 0; line-height: 1px; font-size: 0; padding: 0; width: 100%; margin-top: 0;">&nbsp;</p>
        </div>
        <div style="margin-bottom: 20px; vertical-align: middle; text-align: center;">
            <p style="margin-bottom: 0; font-size: 12px; line-height: 18px;" lang="x-size-12">@2020 Clouder. All rights reserved.</p>
        </div>
    </div>
</div>
"""
    return {"subject": reset_password_subject, "body": reset_password_body}


def confirm_email_message(pin):
    reset_password_subject = "Password Reset Pin - From Clouder Team ☁️"
    reset_password_body = f"""
<div style="margin: 40px auto; padding: 6% 15px 30px; max-width: 600px; background-color: #fff; border-radius: 5px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
    <div style="display:flex;justify-content:center;align-items:center;">
        <img style="width: 140px;" src="https://www.akc.org/wp-content/uploads/2017/11/Dogo-puppy.jpg"/>
    </div>

    <div style="font-family: 'Roboto', sans-serif; text-align: left;">
        <div style="font-size: 17px; line-height: 25px; color: #4d4d4d; font-weight: normal; margin: 13px 30px;">
             <p style="text-align: left;">Hello,</p>
            <p style="text-align: left;">Thank you for signing up for <strong>Clouder</strong>. Please confirm your email address by using the PIN below.:</p>
            <div style="padding: 24px; font-size: 23px; line-height: 30px; color: #fff; font-weight: bold; background: black; border-radius: 5px; text-align: center;">
                {pin}
            </div>
            <p style="text-align: left;">This code will expire in 1 hour, please verify soon.</p>
            <p style="text-align: left;">If this wasn't you, we highly recommend that you change your password right away. If you are unable to do this, please contact our support center for help.</p>
            <br/>
            <div>
                <p style="text-align: left; margin: 0;">Thank you,</p>
                <p style="text-align: left; margin: 0;">Clouder Team</p>
            </div>
        </div>
        <div style="margin: 0 30px;">
            <p style="height: 1px; background-color: #e5e5e5; border: 0; line-height: 1px; font-size: 0; padding: 0; width: 100%; margin-top: 0;">&nbsp;</p>
        </div>
        <div style="margin-bottom: 20px; vertical-align: middle; text-align: center;">
            <p style="margin-bottom: 0; font-size: 12px; line-height: 18px;" lang="x-size-12">@2020 Clouder. All rights reserved.</p>
        </div>
    </div>
</div>
"""
    return {"subject": reset_password_subject, "body": reset_password_body}
