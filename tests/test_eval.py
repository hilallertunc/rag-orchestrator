import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.eval_service import evaluate_response

def test_good_response():
    result = evaluate_response("What is Python?", "Python is a high-level programming language used for web development, data science and AI.")
    assert result["passed"] == True
    assert result["score"] == 100

def test_short_response_fails():
    result = evaluate_response("What is Python?", "A language.")
    assert result["passed"] == False
    assert "answer_too_short" in result["issues"]

def test_empty_response_fails():
    result = evaluate_response("What is Python?", "ok")
    assert result["passed"] == False

def test_uncertainty_detected():
    result = evaluate_response("What is Python?", "I don't know the answer to this question about programming.")
    assert "uncertainty_detected" in result["issues"]

def test_score_is_never_negative():
    result = evaluate_response("x", "I don't know, I'm not sure, cannot answer")
    assert result["score"] >= 0