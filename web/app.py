"""
Flask Web Application for Sports Data Analysis

Provides a web interface to analyze word frequencies from sports news.
"""
from flask import Flask, render_template, jsonify
from src.analyzer import analyze_records_by_date

app = Flask(__name__, template_folder='templates')


@app.route('/')
def index():
    """Serve the main index page."""
    return render_template('index.html')


@app.route('/api/analyze', methods=['GET'])
def api_analyze():
    """
    API endpoint to run analysis and return results.
    
    Returns:
        JSON with analysis results or error
    """
    try:
        print("[DEBUG] API /analyze called")
        results = analyze_records_by_date()
        print(f"[DEBUG] Analysis returned results for {len(results)} dates")
        return jsonify({'success': True, 'data': results})
    except Exception as e:
        print(f"[ERROR] Analysis failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("[INFO] Starting Sports Data Web App")
    print("[INFO] Visit http://localhost:5000 in your browser")
    app.run(debug=True, port=5000)
