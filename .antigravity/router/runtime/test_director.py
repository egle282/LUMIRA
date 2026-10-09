from director import classify, route

def test_rag_route():
    t, r, s, h = classify("Добавь RAG по PDF с tenant isolation")
    agents, skills = route(t, r, s, h)
    assert "ai-engineer" in agents
    assert "security" in agents
    assert "rag" in skills

def test_seo_route():
    t, r, s, h = classify("Сделай SEO для landing page")
    agents, skills = route(t, r, s, h)
    assert "seo" in agents
    assert "seo" in skills

def test_payment_is_high_risk():
    t, r, s, h = classify("Исправь payment webhook в production")
    assert r == "high"
    agents, skills = route(t, r, s, h)
    assert "security" in agents
    assert "qa" in agents
