"""
Comprehensive test suite for generative agents.
Tests security, functionality, and performance aspects.
"""
import unittest
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class TestSecurityUtils(unittest.TestCase):
    """Test security utilities and validation functions."""
    
    def setUp(self):
        """Set up test environment."""
        try:
            from security_utils import (
                safe_literal_eval, safe_json_parse, 
                validate_gpt_response, sanitize_input,
                validate_persona_name, validate_file_path
            )
            self.security_utils = {
                'safe_literal_eval': safe_literal_eval,
                'safe_json_parse': safe_json_parse,
                'validate_gpt_response': validate_gpt_response,
                'sanitize_input': sanitize_input,
                'validate_persona_name': validate_persona_name,
                'validate_file_path': validate_file_path
            }
        except ImportError as e:
            self.skipTest(f"Security utils not available: {e}")
    
    def test_safe_literal_eval_valid_input(self):
        """Test safe literal eval with valid inputs."""
        func = self.security_utils['safe_literal_eval']
        
        # Test valid inputs
        self.assertEqual(func('[1, 2, 3]'), [1, 2, 3])
        self.assertEqual(func('{"key": "value"}'), {"key": "value"})
        self.assertEqual(func('"hello"'), "hello")
        self.assertEqual(func('42'), 42)
        self.assertEqual(func('True'), True)
    
    def test_safe_literal_eval_malicious_input(self):
        """Test safe literal eval rejects malicious inputs."""
        func = self.security_utils['safe_literal_eval']
        
        # Test malicious inputs
        self.assertIsNone(func('__import__("os").system("rm -rf /")'))
        self.assertIsNone(func('exec("print(1)")'))
        self.assertIsNone(func('eval("1+1")'))
        self.assertIsNone(func('open("/etc/passwd")'))
    
    def test_sanitize_input(self):
        """Test input sanitization."""
        func = self.security_utils['sanitize_input']
        
        # Test normal input
        self.assertEqual(func("Hello World!"), "Hello World!")
        
        # Test input with dangerous characters
        self.assertEqual(func("Hello<script>alert('xss')</script>"), "Helloscriptalert('xss')script")
        
        # Test length limit
        long_input = "a" * 2000
        result = func(long_input, max_length=100)
        self.assertEqual(len(result), 100)
    
    def test_validate_persona_name(self):
        """Test persona name validation."""
        func = self.security_utils['validate_persona_name']
        
        # Valid names
        self.assertTrue(func("John Doe"))
        self.assertTrue(func("Mary-Jane"))
        self.assertTrue(func("O'Connor"))
        
        # Invalid names
        self.assertFalse(func(""))
        self.assertFalse(func("John123"))
        self.assertFalse(func("John<script>"))
        self.assertFalse(func("A" * 100))  # Too long
    
    def test_validate_file_path(self):
        """Test file path validation."""
        func = self.security_utils['validate_file_path']
        
        # Valid paths
        self.assertTrue(func("data/file.txt"))
        self.assertTrue(func("persona/memory.json"))
        
        # Invalid paths (path traversal)
        self.assertFalse(func("../../../etc/passwd"))
        self.assertFalse(func("/etc/passwd"))
        self.assertFalse(func("data/../../../secret.txt"))

class TestConfiguration(unittest.TestCase):
    """Test configuration management."""
    
    def test_config_imports(self):
        """Test that config can be imported."""
        try:
            import config
            self.assertTrue(hasattr(config, 'OPENAI_API_KEY'))
            self.assertTrue(hasattr(config, 'DJANGO_SECRET_KEY'))
        except ImportError:
            self.skipTest("Config module not available")
    
    def test_legacy_compatibility(self):
        """Test that legacy variable names are still available."""
        try:
            import config
            # Test legacy names
            self.assertTrue(hasattr(config, 'openai_api_key'))
            self.assertTrue(hasattr(config, 'debug'))
            self.assertTrue(hasattr(config, 'maze_assets_loc'))
        except ImportError:
            self.skipTest("Config module not available")

class TestLogging(unittest.TestCase):
    """Test logging configuration."""
    
    def test_logger_setup(self):
        """Test that logging is properly configured."""
        try:
            from logger_config import get_logger, log_security_event, log_api_call
            
            logger = get_logger('test')
            self.assertIsNotNone(logger)
            
            # Test that functions don't crash
            log_security_event("TEST", "Test security event")
            log_api_call("test_api", 0.001, True)
            
        except ImportError:
            self.skipTest("Logger config not available")

class TestPersonaBasics(unittest.TestCase):
    """Test basic persona functionality."""
    
    def test_persona_import(self):
        """Test that persona module can be imported."""
        try:
            sys.path.insert(0, str(project_root / 'reverie' / 'backend_server'))
            from persona.persona import Persona
            self.assertTrue(callable(Persona))
        except ImportError as e:
            self.skipTest(f"Persona module not available: {e}")

class TestGPTStructure(unittest.TestCase):
    """Test GPT structure and API handling."""
    
    def test_gpt_structure_import(self):
        """Test that GPT structure can be imported."""
        try:
            sys.path.insert(0, str(project_root / 'reverie' / 'backend_server' / 'persona' / 'prompt_template'))
            from gpt_structure import ChatGPT_single_request
            self.assertTrue(callable(ChatGPT_single_request))
        except ImportError as e:
            self.skipTest(f"GPT structure not available: {e}")

def run_all_tests():
    """Run all tests and return results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestSecurityUtils,
        TestConfiguration, 
        TestLogging,
        TestPersonaBasics,
        TestGPTStructure
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result

if __name__ == '__main__':
    print("Running Generative Agents Test Suite")
    print("=" * 50)
    
    result = run_all_tests()
    
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    exit_code = 0 if result.wasSuccessful() else 1
    sys.exit(exit_code)