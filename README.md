# LNChat - Lightning Node Management with ChatGPT

LNChat is a reckless experiment that combines the power of OpenAI's GPT-4 model with the capabilities of managing a Lightning node. 

## ⚠️ Warning: This is Reckless! ⚠️

This application directly executes the Python code generated by the GPT-4 model in response to your queries. While we've tried to ensure safety, there are no guarantees. There is a real risk that errors or malicious responses from the AI could cause you to lose funds.

**Use LNChat at your own risk. If you're not comfortable with this level of risk, do not use this application.**

## Prerequisites

- Python 3.6+
- Flask
- An OpenAI API key
- A Lightning node

## Installation

1. Clone the repository.
2. Install the dependencies with `pip install -r requirements.txt`.
3. Get ahold of your node's macaroon and cert (maybe from nodes.voltage.cloud/) and put them somewhere handy.
4. Copy the `.env.sample` to `.env` and fill in your environment variables.
5. Run the application with `python app.py`.

## Usage

1. Navigate to `http://127.0.0.1:5555` in your web browser.
2. Enter a query about managing your Lightning node. For example, "How many peers are connected to my node?"
3. Submit the query and view the response.

Remember, this application is #reckless. It's fun to experiment with, but use it responsibly and at your own risk.