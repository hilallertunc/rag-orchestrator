import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.router_service import classify_question, select_model

def test_simple_question():
    result = classify_question("Python nedir?")
    assert result == "simple"

def test_complex_question():
    result = classify_question("Python ve JavaScript arasındaki farkları karşılaştır ve analiz et")
    assert result == "complex"

def test_long_question_is_complex():
    result = classify_question("Bir yazılım projesinde hangi programlama dilini seçmeliyim ve neden bu kadar önemli bir karar")
    assert result == "complex"

def test_free_simple_model():
    result = select_model("simple", "free")
    assert result == "llama-3.1-8b-instant"

def test_free_complex_model():
    result = select_model("complex", "free")
    assert result == "llama-3.3-70b-versatile"

def test_premium_always_large_model():
    result = select_model("simple", "premium")
    assert result == "llama-3.3-70b-versatile"