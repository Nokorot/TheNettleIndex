from .. import NettleApp


def route(app: NettleApp):
    from datetime import datetime, timedelta

    @app.flask_app.template_filter("pretty_time")
    def pretty_time_filter(timestamp):
        if timestamp is None:
            return "Unknown"

        if type(timestamp) == str:
            timestamp = float(timestamp)
        ## return "timestamp"

        now = datetime.utcnow()
        dt = datetime.utcfromtimestamp(timestamp)
        diff = now - dt

        if diff < timedelta(minutes=1):
            return "just now"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff < timedelta(days=2):
            return f"yesterday"
        elif diff < timedelta(days=7):
            days = int(diff.total_seconds() / 3600 / 24)
            return f"{days} days ago"
        else:
            return dt.strftime("%B %d, %Y")
