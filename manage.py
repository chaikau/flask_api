from app import create_app
from app.models import User
from app.meta import user_db
import config

app = create_app(config)


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=user_db, User=User)


if __name__ == "__main__":
    app.run()
