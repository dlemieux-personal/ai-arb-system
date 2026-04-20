"""
Tests for Markdown submission parser
"""

import pytest
from pathlib import Path
from datetime import datetime
from src.intake.submission_parser import SubmissionParser, MarkdownParseError


@pytest.fixture
def parser():
    """Create a parser instance"""
    return SubmissionParser()


@pytest.fixture
def sample_markdown(tmp_path):
    """Create a sample markdown submission"""
    content = """---
submission_id: TEST-0001-ABC123
team_name: "Test Engineering Team"
submission_date: 2024-02-28
system_title: "Test Architecture"
---

# Architecture Submission

## Executive Summary

This is a test architecture submission for testing purposes.

---

## 2. Security Architecture

### 2.1 Authentication & Authorization
- Using OAuth 2.0 for authentication
- Role-based access control implemented

### 2.2 Data Protection
- Encryption in Transit: - [x] Enabled
- Encryption at Rest: - [x] Enabled
- Data classification implemented

---

## 3. Scalability & Performance

### 3.1 Load Patterns
- Expected peak load: 10,000 requests/sec
- Auto-scaling configured

### 3.2 Performance Targets
- Target p50 latency: 100ms
- Target p99 latency: 500ms

---

## 10. Risk Assessment

### 10.1 Technical Risks
- **Operational complexity** (Severity: high, Mitigation: Comprehensive monitoring)
- **Data consistency** (Severity: medium, Mitigation: Event sourcing pattern)

---

## Additional Materials

- Architecture decision records
- Performance test results
"""
    md_file = tmp_path / "test-submission.md"
    md_file.write_text(content)
    return md_file


def test_parse_markdown_valid(parser, sample_markdown):
    """Test parsing valid markdown submission"""
    parsed = parser.parse(sample_markdown)
    
    assert parsed.metadata.submission_id == "TEST-0001-ABC123"
    assert parsed.metadata.team_name == "Test Engineering Team"
    assert parsed.metadata.system_title == "Test Architecture"
    assert parsed.metadata.submission_date.startswith("2024-02-28")
    
    # Check sections were parsed
    assert 'security' in parsed.sections
    assert 'scalability' in parsed.sections


def test_parse_markdown_missing_frontmatter(tmp_path, parser):
    """Test that missing frontmatter fields raise error"""
    invalid_md = tmp_path / "invalid.md"
    invalid_md.write_text("""---
submission_id: TEST-001
---

# Content without required fields
""")
    
    with pytest.raises(MarkdownParseError) as exc_info:
        parser.parse(invalid_md)
    
    assert "Missing required frontmatter fields" in str(exc_info.value)


def test_parse_markdown_no_frontmatter(tmp_path, parser):
    """Test that missing frontmatter raises error"""
    invalid_md = tmp_path / "no-frontmatter.md"
    invalid_md.write_text("""# No frontmatter here

Just markdown content.""")
    
    with pytest.raises(MarkdownParseError):
        parser.parse(invalid_md)


def test_parse_boolean_various_formats(parser):
    """Test boolean parsing with various formats"""
    assert parser._parse_boolean(True) is True
    assert parser._parse_boolean(False) is False
    assert parser._parse_boolean('true') is True
    assert parser._parse_boolean('false') is False
    assert parser._parse_boolean('yes') is True
    assert parser._parse_boolean('no') is False
    assert parser._parse_boolean('- [x]') is True
    assert parser._parse_boolean('- [ ]') is False


def test_parse_boolean_invalid(parser):
    """Test that invalid boolean values raise error"""
    with pytest.raises(MarkdownParseError):
        parser._parse_boolean('maybe')


def test_normalize_enum_case_insensitive(parser):
    """Test case-insensitive enum normalization"""
    valid_options = ['low', 'medium', 'high', 'critical']
    
    assert parser._normalize_enum('LOW', valid_options) == 'low'
    assert parser._normalize_enum('High', valid_options) == 'high'
    assert parser._normalize_enum('CRITICAL', valid_options) == 'critical'


def test_normalize_enum_invalid(parser):
    """Test that invalid enum values raise error"""
    valid_options = ['low', 'medium', 'high']
    
    with pytest.raises(MarkdownParseError):
        parser._normalize_enum('invalid', valid_options)


def test_extract_bullet_list(parser):
    """Test extracting bullet list items"""
    text = """### Section
- Item 1
- Item 2
- Item 3

### Next section"""
    
    items, _ = parser._extract_bullet_list(text, text.find('- Item'))
    assert items == ['Item 1', 'Item 2', 'Item 3']


def test_extract_bullet_list_with_checkboxes(parser):
    """Test extracting bullet list with checkbox notation"""
    text = """### Checklist
- [x] Done item
- [ ] Todo item
- Partial checkbox - [x] enabled"""
    
    items, _ = parser._extract_bullet_list(text, text.find('- [x]'))
    assert len(items) >= 1
    assert any('Done' in item for item in items)


def test_parse_json_valid(tmp_path, parser):
    """Test parsing valid JSON submission"""
    json_content = """{
  "submission_id": "JSON-0001-TEST",
  "team_name": "JSON Test Team",
  "submission_date": "2024-02-28T10:00:00Z",
  "system_overview": {
    "title": "JSON Test Architecture",
    "description": "Test JSON submission"
  },
  "sections": {
    "security": {"authentication": "OAuth2"}
  }
}"""
    
    json_file = tmp_path / "test.json"
    json_file.write_text(json_content)
    
    parsed = parser.parse(json_file)
    
    assert parsed.metadata.submission_id == "JSON-0001-TEST"
    assert parsed.metadata.team_name == "JSON Test Team"
    assert parsed.metadata.system_title == "JSON Test Architecture"


def test_flexible_date_parsing(tmp_path, parser):
    """Test flexible date parsing for various formats"""
    test_cases = [
        ("2024-02-28", "20240228"),
        ("2024-02-28T10:00:00Z", "20240228T100000Z"),
        ("Feb 28, 2024", "Feb28_2024"),
        ("02-28-2024", "02282024"),
    ]
    
    for test_date, safe_name in test_cases:
        md_content = f"""---
submission_id: TEST-0001-{safe_name}
team_name: "Test"
submission_date: {test_date}
system_title: "Test"
---

# Content
"""
        md_file = tmp_path / f"test_{safe_name}.md"
        md_file.write_text(md_content)
        
        parsed = parser.parse(md_file)
        assert parsed.metadata.submission_date  # Should parse without error
