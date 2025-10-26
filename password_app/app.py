
from flask import Flask, render_template, request
import itertools, string, random

app = Flask(__name__)

def estimate_strength(pw):
    length = len(pw)
    score = min(40, length * 4)
    has_lower = any(c.islower() for c in pw)
    has_upper = any(c.isupper() for c in pw)
    has_digit = any(c.isdigit() for c in pw)
    has_sym = any(c in string.punctuation for c in pw)
    classes = sum((has_lower, has_upper, has_digit, has_sym))
    score += classes * 15
    lowers = pw.lower()
    commons = ['password','1234','qwerty','admin','letmein']
    if any(c in lowers for c in commons):
        score -= 30
    return max(0, min(100, score))

def generate_passwords(names, years, pets, extras):
    parts = [p for p in [names, years, pets, extras] if p]
    combos = list(itertools.product(*parts))
    random.shuffle(combos)
    samples = [''.join(c) for c in combos[:10]]
    return samples

@app.route('/', methods=['GET','POST'])
def index():
    result = None
    samples = None
    if request.method == 'POST':
        if 'check' in request.form:
            pw = request.form.get('password','')
            result = {'password': pw, 'score': estimate_strength(pw)}
        elif 'generate' in request.form:
            names = request.form.get('names','').split()
            years = request.form.get('years','').split()
            pets = request.form.get('pets','').split()
            extras = request.form.get('extras','').split()
            samples = generate_passwords(names, years, pets, extras)
    return render_template('index.html', result=result, samples=samples)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
