from flask import Flask, render_template, request, jsonify
from agents.inventory_agent import run_inventory_agent

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    response = run_inventory_agent(user_input)
    return jsonify({"output": response.get("output", response)})

if __name__ == "__main__":
    app.run(debug=True)