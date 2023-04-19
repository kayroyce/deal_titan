from flask import Flask, render_template
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from .extensions import db
from .routes import auth, main, cart

def create_app(config_file='settings.py'):
    app = Flask(__name__)
    app.config.from_pyfile(config_file)
    
    db.init_app(app)
    migrate = Migrate(app, db)
    
    csrf = CSRFProtect(app)
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(cart.bp)
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app

if __name__ == "__main__":
    app.run(debug=True, port=5000)
