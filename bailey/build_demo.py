import json, re

fonts_css = open("fonts.css").read()
idx = open("/home/user/Test/bailey/static/index.html").read()

# 1) token + component CSS (inner of the first <style> block)
style_inner = idx.split("<style>", 1)[1].split("</style>", 1)[0]

# 2) body content: from <div id="app"  through the LAST </script>
# (there are now two script tags: the early viewport shim and the main app).
body = idx.split('<div id="app"', 1)[1]
body = '<div id="app"' + body.rsplit("</script>", 1)[0] + "</script>"

# 3) demo data
demo_a = json.load(open("/home/user/Test/bailey/sample_offers/demo_analysis.json"))
demo_b = json.load(open("/home/user/Test/bailey/sample_offers/demo_analysis_b.json"))
demo_js = "const DEMO=[%s,%s];let demoIdx=0;function nextDemo(){return JSON.parse(JSON.stringify(DEMO[demoIdx++%%DEMO.length]));}" % (
    json.dumps(demo_a), json.dumps(demo_b))

# 4) swap the networked flow for inlined demo data
# Replace the post()/analyzeFile/analyzeSample trio with demo versions.
old_flow_start = body.index("async function post(")
old_flow_end = body.index("function copyEmail(")
demo_flow = (
    demo_js + "\n"
    "function analyzeFile(file){beginAnalysis(function(){return Promise.resolve({filename:file.name,analysis:nextDemo()});},file.name);}\n"
    "function analyzeSample(){beginAnalysis(function(){return Promise.resolve({filename:\"Sample offer\",analysis:nextDemo()});},\"Sample offer\");}\n"
)
body = body[:old_flow_start] + demo_flow + body[old_flow_end:]

art = "<style>\n%s\n%s\n</style>\n%s\n" % (fonts_css, style_inner, body)
open("bailey-demo.html", "w").write(art)
print("artifact bytes:", len(art))
print("has DEMO:", "const DEMO=[" in art, "| post() removed:", "async function post(" not in art)

# Make the whole file pure ASCII so it renders identically under any charset:
# non-ASCII chars live inside JS string/template literals and CSS comments, so
# backslash escapes (\xNN / \uNNNN) reproduce them safely at runtime.
art = open("bailey-demo.html").read()
ascii_art = art.encode("ascii", "backslashreplace").decode("ascii")
open("bailey-demo.html", "w").write(ascii_art)
print("ascii-only:", all(ord(c) < 128 for c in ascii_art), "| bytes:", len(ascii_art))

# Also emit a STANDALONE full-document version with a real <head> (charset +
# viewport). This is hostable on any static host and renders correctly on
# phones — no artifact wrapper deciding the viewport for us.
demo_html = open("bailey-demo.html").read()  # ASCII body (style + content)
standalone = (
    "<!doctype html>\n<html lang=\"en\">\n<head>\n"
    "<meta charset=\"utf-8\">\n"
    "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
    "<title>Bailey - offer analysis for clinicians</title>\n"
    "</head>\n<body>\n" + demo_html + "\n</body>\n</html>\n"
)
open("bailey-demo-standalone.html", "w").write(standalone)
print("standalone bytes:", len(standalone), "| has head viewport:",
      'name="viewport"' in standalone.split("</head>")[0])

# Emit the same standalone doc as the Netlify publish artifact: public/index.html.
# Netlify's continuous deployment serves this directory, so regenerating it here
# means every push updates the live site automatically.
import os
os.makedirs("public", exist_ok=True)
open("public/index.html", "w").write(standalone)
print("public/index.html written:", len(standalone), "bytes")
