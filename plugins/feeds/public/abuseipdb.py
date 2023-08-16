
import logging
from datetime import timedelta, datetime
from core.schemas import observable
from core.schemas import task
from core import taskmanager


from core.config.config import yeti_config


class AbuseIPDB(task.FeedTask):
    URL_FEED = "https://api.abuseipdb.com/api/v2/blacklist?&key=%s&plaintext&limit=10000"
    _defaults = {
        "frequency": timedelta(hours=5),
        "name": "AbuseIPDB",
        "description": "Black List IP generated by AbuseIPDB",
    }

    def run(self):
        api_key = yeti_config.get("abuseIPDB", "key")

        if not api_key:
            raise Exception("Your abuseIPDB API key is not set in the yeti.conf file")

        
        # change the limit rate if you subscribe to a paid plan
        
        data = self._make_request(self.URL_FEED % api_key, verify=True).text

        for line in data.split("\n"):
            self.analyze(line)


    def analyze(self, line):
        line = line.strip()

        ip_value = line

        context = {"source": self.name, "date_added": datetime.utcnow()}

        try:
            ip = observable.Observable.find(value=ip_value)
            if not ip:
                ip = observable.Observable(value=ip_value, type="ip").save()
            
            logging.debug("IP: %s" % ip_value)
            ip.add_context(self.name, context)
            ip.tag(["blocklist"])

        except Exception as e:
            logging.error(e)
taskmanager.TaskManager.register_task(AbuseIPDB)