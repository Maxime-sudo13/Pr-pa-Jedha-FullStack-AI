import os
D = os.path.dirname(os.path.abspath(__file__))
r = lambda p: open(os.path.join(D, "src", p)).read()
html = r("shell.html").replace("/*CSS*/", r("base.css") + r("extra.css") + r("cyber.css")).replace("/*JS*/", r("viz.js") + "\n" + r("app.js"))
open(os.path.join(D, "index.html"), "w").write(html)
print("index.html", len(html) // 1024, "Ko")
