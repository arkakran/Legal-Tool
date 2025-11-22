from flask import render_template, Blueprint

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/results/<doc_id>')
def results(doc_id):
    return render_template('results.html', doc_id=doc_id)
