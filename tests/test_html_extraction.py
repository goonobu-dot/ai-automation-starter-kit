from ai_automation_kit.core.html import extract_html_content


def test_extract_html_content_returns_title_and_clean_text():
    html = """
    <html><head><title>AI Tools</title><script>ignore()</script></head>
    <body><h1>AI Tools</h1><p>Workflow automation helps teams.</p></body></html>
    """

    content = extract_html_content(html)

    assert content.title == "AI Tools"
    assert "Workflow automation helps teams." in content.text
    assert "ignore()" not in content.text
