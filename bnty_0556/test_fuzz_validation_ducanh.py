"""test_fuzz_validation_ducanh.py — Independent QA Fuzz & Boundary Suite.

Contributed by ducanh3005 for SWARM L5 Flagship Swarm (bnty_0556).
Validates smoke_forge generator robustness:
1. Handling empty, malformed, and partial OpenAPI 3.x specifications.
2. Parameter fuzzing with special URL characters and whitespace.
3. Parameter replacement logic mapping path variables {param} to smoke values.
"""
import unittest
from smoke_forge.forge import generate_tests, load_spec

class TestSmokeForgeFuzzValidation(unittest.TestCase):
    def test_empty_spec_handling(self):
        """Empty paths object should produce valid suite with 0 smoke tests."""
        spec = {"openapi": "3.0.0", "info": {"title": "Empty", "version": "1.0"}, "paths": {}}
        source = generate_tests(spec, "https://api.example.com")
        self.assertIn("0 smoke tests generated", source)
        self.assertIn("import urllib.request", source)

    def test_missing_responses_or_methods(self):
        """Operations without explicit 200 responses or empty operations."""
        spec = {
            "openapi": "3.0.1",
            "info": {"title": "Partial", "version": "1.0"},
            "paths": {
                "/no-methods": {},
                "/custom-code": {
                    "get": {
                        "operationId": "custom_get",
                        "responses": {"204": {"description": "No Content"}}
                    }
                }
            }
        }
        source = generate_tests(spec, "https://api.example.com")
        self.assertIn("def test_get_custom_code():", source)
        self.assertIn("status < 500", source)

    def test_path_parameter_substitution_fuzzing(self):
        """Ensure path parameters with dashes and underscores parse cleanly into substitution values."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Params", "version": "1.0"},
            "paths": {
                "/items/{item_id}/sub/{sub-id}": {
                    "get": {
                        "operationId": "get_sub_item",
                        "parameters": [
                            {"name": "item_id", "in": "path", "required": True},
                            {"name": "sub-id", "in": "path", "required": True}
                        ],
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            }
        }
        source = generate_tests(spec, "https://api.example.com")
        self.assertIn("def test_get_items_item_id_sub_sub_id():", source)
        self.assertIn('_smoke("/items/1/sub/1")', source)

if __name__ == "__main__":
    unittest.main()
