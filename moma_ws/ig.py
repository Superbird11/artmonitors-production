import instagrapi as ig
from instagrapi.exceptions import LoginRequired
import sqlite3
import os
import pathlib
# import authenticator

KEYFILE = 'artmonitors/keys/ig.txt'
SETTINGSFILE = 'artmonitors/keys/settings.json'
MEDIA_ROOT = 'static/media'


# easily swappable function to modify the blacklist as needed
tries = 10
def work_is_not_on_blacklist(pagename: str, collection_abbrev: str):
    global tries
    tries -= 1
    if tries <= 0:
        raise ValueError("Could not find a non-blacklisted work within 10 tries")

    # don't show MACS works yet.
    if collection_abbrev.lower().startswith("macs"):
        return False
    # # NSMA has .gif files instead of .jpeg, which might cause problems
    # if collection_abbrev.lower() == "nsma":
    #     return False

    return True


# email functions
def sendmail_email(msg):
    # http://www.yak.net/fqa/84.html
    sendmail_location = "/usr/sbin/sendmail"
    sendmail = os.popen("{} -t".format(sendmail_location), 'w')
    sendmail.write(msg)
    status = sendmail.close()
    print("Sent the following email with sendmail, status {}:".format(status))
    print(msg)


def email_about_error(wd, errortext):
    # write email
    sendmail_email(f"""To: curator@artmonitors.com
From: autoupload@artmonitors.com
Subject: [ARTMONITORS IG ERROR] Failed to upload work {wd} to Instagram

Hello curator,

Trying to upload the work {wd} to Instagram failed, with the following stacktrace:

{errortext}

Thank you,
-Webservice.moma_ws.artmonitors
""")

def email_about_success(wd, code):
    sendmail_email(f"""To: curator@artmonitors.com
From: autoupload@artmonitors.com
Subject: [ARTMONITORS IG SUCCESS] Uploaded work {wd} to Instagram

Hello curator,

Uploading the work {wd} to Instagram appears to have been a success.

The instagram link for the work should be 
https://www.instagram.com/p/{code}/

If you'd like, double-check that it worked correctly

Thank you,
-Webservice.moma_ws.artmonitors
""")


if __name__ == '__main__':
    workdata = "(No work fetched yet)"

    try:
        # select random work from database that is not already on instagram
        # this is a static query so there should be no sql injection risk
        db = sqlite3.connect("db.sqlite3")
        cursor = db.cursor()

        while True:
            result = cursor.execute("""
                SELECT w.id, w.name, w.pagename, w.description, w.path, w.featured, c.abbrev
                    FROM artmonitors_work AS w
                    INNER JOIN artmonitors_collection AS c
                        ON w.collection_id = c.id
                    WHERE ig IS NULL
                    ORDER BY RANDOM()
                    LIMIT 1;
            """)
            work_id, name, pagename, description, partial_path, featured, coll = result.fetchone()
            workdata = f"{name} ({coll}/{pagename} - id={work_id})"
            if work_is_not_on_blacklist(pagename, coll):
                break
        work_path = pathlib.Path(MEDIA_ROOT, partial_path)
        desc_parts = [
            name,
            description,
            f"https://artmonitors.com/collections/{coll}/{pagename}",
            f"#artmonitors #{coll}{' #featured' if featured else ''}"
        ]
        work_desc = " \n- ".join(token for token in desc_parts if token)

        # upload to instagram
        with open(KEYFILE) as ig_cred_file:
            username, password, *_ = [t.strip() for t in ig_cred_file.readlines()]

        # do not necessarily do 2fa until we need to
        # since copying the entire settings breaks the login, instead just copy the settings we want using a
        # dummy client
        cl = ig.Client()
        cl2 = ig.Client()
        if os.path.exists(SETTINGSFILE):
            cl2.load_settings(pathlib.Path(SETTINGSFILE))
            cl.device_settings = cl2.device_settings
            cl.android_device_id = cl2.android_device_id
            cl.advertising_id = cl2.advertising_id
            cl.app_id = cl2.app_id
            cl.user_agent = cl2.user_agent
            cl.settings['device_settings'] = cl2.settings['device_settings']
            cl.settings['user_agent'] = cl2.settings['user_agent']

        logged_in = cl.login(username, password)
        try:
            cl.account_info()
        except LoginRequired:
            logged_in = cl.relogin()
        cl.dump_settings(pathlib.Path(SETTINGSFILE))
        post = cl.photo_upload(work_path, work_desc)

        post_code = post.dict()['code']

        # if the above executes without errors, then update the work
        # (prepared statement, no injection risk)
        successful_update = cursor.execute("""
            UPDATE artmonitors_work
                SET ig = ?
                WHERE id = ?
        """, (post_code, work_id))
        if not successful_update:
            raise ValueError(
                f"Failed to upload work {workdata} with instagram code {post_code}")
        print(f"Successfully uploaded work {workdata}. https://www.instagram.com/p/{post_code}")
        # email_about_success(workdata, ig)
    except Exception as ex:
        import traceback
        error_msg = "".join(traceback.TracebackException.from_exception(ex).format())
        print(f"Failed to upload to instagram: {workdata}")
        print(error_msg)
        email_about_error(workdata, error_msg)
