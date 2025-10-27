from flask import Flask, request, render_template_string
import json, os
from orchestrator import orchestrate_sync

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML = '''
<!doctype html>
<title>Character Card Processor</title>
<h2>Upload a Character Card (JSON)</h2>
<form method=post enctype=multipart/form-data>
  <input type=file name=file>
  <input type=submit value=Upload>
</form>
{% if result %}
<h3>Processed Card</h3>
<pre>{{ result }}</pre>
<h4>Change Log</h4>
<pre>{{ changelog }}</pre>
{% endif %}
'''

@app.route('/', methods=['GET','POST'])
def index():
    result, changelog = None, None
    if request.method == 'POST':
        f = request.files['file']
        path = os.path.join(UPLOAD_FOLDER, f.filename)
        f.save(path)
        out = os.path.join(UPLOAD_FOLDER, 'out_' + f.filename)
        card, log = orchestrate_sync(path, out)
        result = json.dumps(card, indent=2)
        changelog = json.dumps(log, indent=2)
    return render_template_string(HTML, result=result, changelog=changelog)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

# Summary of what to do next
# (1.) Update endpoint → ✅ already done.
# (2.) Strengthen prompts for appearance/skills/dialogue → needed.
# (3.) Patch diff_json serialization → needed.
# (4.) Restart Flask → python app.py.