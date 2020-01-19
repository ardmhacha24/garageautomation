# Software to monitor and control my garage doors via a raspberry pi.

import time, sys, syslog, uuid
import smtplib
import RPi.GPIO as gpio
import json
import httplib
import urllib
import subprocess

class Controller(object):
    def __init__(self, config):
        #setting up the control pins on relay switch
        gpio.setwarnings(False)
        gpio.cleanup()
        gpio.setmode(gpio.BCM)
        self.config = config
        self.doors = [Door(n, c) for (n, c) in config['doors'].items()]
        ##self.updateHandler = UpdateHandler(self)
        for door in self.doors:
            door.last_state = 'unknown'
            door.last_state_time = time.time()

        self.use_alerts = config['config']['use_alerts']
        self.alert_type = config['alerts']['alert_type']
        self.ttw = config['alerts']['time_to_wait']
        if self.alert_type == 'smtp':
            self.use_smtp = False
            smtp_params = ("smtphost", "smtpport", "smtp_tls", "username", "password", "to_email")
            self.use_smtp = ('smtp' in config['alerts']) and set(smtp_params) <= set(config['alerts']['smtp'])
            syslog.syslog("we are using SMTP")
        else:
            self.alert_type = None
            syslog.syslog("No alerts configured")

    def status_check(self):
        for door in self.doors:
            new_state = door.get_state()
            if (door.last_state != new_state):
                syslog.syslog('%s: %s => %s' % (door.name, door.last_state, new_state))
                door.last_state = new_state
                door.last_state_time = time.time()
                self.updateHandler.handle_updates()

            if new_state == 'open' and not door.msg_sent and time.time() - door.open_time >= self.ttw:
                if self.use_alerts:
                    title = "%s's garage door open" % door.name
                    etime = elapsed_time(int(time.time() - door.open_time))
                    message = "%s's garage door has been open for %s" % (door.name, etime)
                    if self.alert_type == 'smtp':
                        self.send_email(title, message)
                    door.msg_sent = True

            if new_state == 'closed':
                if self.use_alerts:
                    if door.msg_sent == True:
                        title = "%s's garage doors closed" % door.name
                        etime = elapsed_time(int(time.time() - door.open_time))
                        message = "%s's garage door is now closed after %s  "% (door.name, etime)
                        if self.alert_type == 'smtp':
                            self.send_email(title, message)
                door.open_time = time.time()
                door.msg_sent = False

    def send_email(self, title, message):
        try:
            if self.use_smtp:
                syslog.syslog("Sending email message")
                config = self.config['alerts']['smtp']

                message = MIMEText(message)
                message['Date'] = formatdate()
                message['From'] = config["username"]
                message['To'] = config["to_email"]
                message['Subject'] = config["subject"]
                message['Message-ID'] = make_msgid()

                server = smtplib.SMTP(config["smtphost"], config["smtpport"])
                if (config["smtp_tls"] == "True") :
                    server.starttls()
                server.login(config["username"], config["password"])
                server.sendmail(config["username"], config["to_email"], message.as_string())
                server.close()
        except Exception as inst:
            syslog.syslog("Error sending email: " + str(inst))

    def toggle(self, doorId):
        for d in self.doors:
            if d.id == doorId:
                syslog.syslog('%s: toggled' % d.name)
                d.toggle_relay()
                return

    def get_updates(self, lastupdate):
        updates = []
        for d in self.doors:
            if d.last_state_time >= lastupdate:
                updates.append((d.id, d.last_state, d.last_state_time))
        return updates

    def get_config_with_default(self, config, param, default):
        if not config:
            return default
        if not param in config:
            return default
        return config[param]

    def run(self):
        if self.config['config']['use_auth']:

        else:


        site = server.Site(root)

        if not self.get_config_with_default(self.config['config'], 'use_https', False):
            reactor.listenTCP(self.config['site']['port'], site)  # @UndefinedVariable
            reactor.run()  # @UndefinedVariable
        else:
            sslContext = ssl.DefaultOpenSSLContextFactory(self.config['site']['ssl_key'], self.config['site']['ssl_cert'])
            reactor.listenSSL(self.config['site']['port_secure'], site, sslContext)  # @UndefinedVariable
            reactor.run()  # @UndefinedVariable

# main loop
try:

    while True:
        if __name__ == '__main__':
            syslog.openlog('garage_controller')
            config_file = open('sysconfig.json')
            controller = Controller(json.load(config_file))
            config_file.close()
            controller.run()

# End program cleanly with keyboard
except KeyboardInterrupt:
    print ("Quitting...")
    # Reset GPIO settings
    gpio.cleanup()
    sys.exit(0)