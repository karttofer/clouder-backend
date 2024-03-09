# Reset Password Configs


def reset_password_messages(pin):
    reset_password_subject = "Password Reset Pin - From Clouder Team ☁️"
    reset_password_body = f"""
 <div style="margin-top: 40px; padding: 6% 15px 30px; max-width: 600px; margin: 0 auto; background-color: #fff; border-radius: 5px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
    <div style="width: 95%; text-align: center;">
        <!-- No image included -->
    </div>

    <div style="font-family: 'Roboto', sans-serif; text-align: left;">
        <h1 style="font-size: 32px; line-height: 36px; font-weight: 600; padding-bottom: 10px; color: #ff6000;text-align:center;">VERIFY YOUR IDENTITY</h1>
        <div style="font-size: 17px; line-height: 25px; color: #4d4d4d; font-weight: normal; margin: 13px 30px;">
            <p style="text-align:left;">Hello,</p>
            <p style="text-align:left;">You have requested to reset your password for <strong>Clouder</strong>. Use the following PIN to reset your password:</p>
            <div style="padding: 24px;font-size: 23px; line-height: 10px; color: #fff; font-weight: normal; background: #ff8f00; border-radius: 5px; text-align: center;">
                <b>{pin}</b>
            </div>
            <p style="text-align:left;">This code will expire in 1 hour, please verify soon.</p>
            <p style="text-align:left;">If this wasn't you, we highly recommend that you change your password right away. If you are unable to do this, please contact our support center for help.</p>
            <br/>
            <div>
            <p style="text-align:left;margin:0px">Thank you,</p>
            <p style="text-align:left;margin:0px">Clouder Team</p>
            </div>
        </div>
        <div style="margin: 0 30px;">
            <p style="height: 1px; background-color: #e5e5e5; border: 0; line-height: 1px; font-size: 0; padding: 0; width: 100%; margin-top: 0;">&nbsp;</p>
        </div>
        <div style="margin-bottom: 20px; vertical-align: middle;">
            <p style="margin-bottom: 0; font-size: 12px; line-height: 18px;" lang="x-size-12">@2020 Clouder. All rights reserved.</p>
        </div>
    </div>
</div>
"""
    return {"subject": reset_password_subject, "body": reset_password_body}
