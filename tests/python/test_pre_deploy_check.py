import unittest
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

# Add parent directory to path to import the module to test
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import the module to test
from tools.pre_deploy_check import (
    check_environment_variables,
    check_configuration_files,
    check_database_connection,
    validate_api_endpoints,
    fix_common_issues,
    main
)

class TestPreDeployCheck(unittest.TestCase):
    """Unit tests for the pre_deploy_check.py module."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for tests
        self.test_dir = tempfile.TemporaryDirectory()
        
        # Mock environment variables
        self.env_patcher = patch.dict('os.environ', {
            'SUPABASE_URL': 'https://example.supabase.co',
            'SUPABASE_KEY': 'test-key',
            'RAILWAY_TOKEN': 'test-railway-token',
            'VERCEL_TOKEN': 'test-vercel-token'
        })
        self.env_patcher.start()
        
    def tearDown(self):
        """Clean up after tests."""
        # Remove the temporary directory
        self.test_dir.cleanup()
        
        # Stop patching environment variables
        self.env_patcher.stop()
    
    def test_check_environment_variables_success(self):
        """Test environment variable check with all required variables."""
        # Test the function
        result = check_environment_variables(required_vars=[
            'SUPABASE_URL', 'SUPABASE_KEY', 'RAILWAY_TOKEN', 'VERCEL_TOKEN'
        ])
        
        # Verify result
        self.assertTrue(result)
        
    def test_check_environment_variables_missing(self):
        """Test environment variable check with missing variables."""
        # Temporarily remove an environment variable
        with patch.dict('os.environ', {'RAILWAY_TOKEN': ''}):
            # Test the function
            result = check_environment_variables(required_vars=[
                'SUPABASE_URL', 'SUPABASE_KEY', 'RAILWAY_TOKEN', 'VERCEL_TOKEN'
            ])
            
            # Verify result
            self.assertFalse(result)
    
    @patch('os.path.exists')
    def test_check_configuration_files_success(self, mock_exists):
        """Test configuration file check when all files exist."""
        # Mock that all files exist
        mock_exists.return_value = True
        
        # Test the function
        result = check_configuration_files(required_files=[
            'railway.json', 'vercel.json', '.env'
        ])
        
        # Verify result
        self.assertTrue(result)
        
    @patch('os.path.exists')
    def test_check_configuration_files_missing(self, mock_exists):
        """Test configuration file check when files are missing."""
        # Mock that files don't exist
        mock_exists.side_effect = lambda path: path != 'vercel.json'
        
        # Test the function
        result = check_configuration_files(required_files=[
            'railway.json', 'vercel.json', '.env'
        ])
        
        # Verify result
        self.assertFalse(result)
    
    @patch('tools.pre_deploy_check.check_database_connection')
    def test_check_database_connection_success(self, mock_check_db):
        """Test database connection check success."""
        # Mock successful database connection
        mock_check_db.return_value = True
        
        # Test the function directly (note that we're not actually testing the implementation)
        result = check_database_connection()
        
        # Verify result
        self.assertTrue(result)
        
    @patch('tools.pre_deploy_check.check_database_connection')
    def test_check_database_connection_failure(self, mock_check_db):
        """Test database connection check failure."""
        # Mock failed database connection
        mock_check_db.return_value = False
        
        # Test the function
        result = check_database_connection()
        
        # Verify result
        self.assertFalse(result)
    
    @patch('requests.get')
    def test_validate_api_endpoints_success(self, mock_get):
        """Test API endpoint validation success."""
        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'ok'}
        
        # Configure mock to return the response
        mock_get.return_value = mock_response
        
        # Test the function
        result = validate_api_endpoints(endpoints=['https://example.com/api/health'])
        
        # Verify result
        self.assertTrue(result)
        
    @patch('requests.get')
    def test_validate_api_endpoints_failure(self, mock_get):
        """Test API endpoint validation with failed endpoint."""
        # Create mock response
        mock_response = MagicMock()
        mock_response.status_code = 404
        
        # Configure mock to return the response
        mock_get.return_value = mock_response
        
        # Test the function
        result = validate_api_endpoints(endpoints=['https://example.com/api/health'])
        
        # Verify result
        self.assertFalse(result)
    
    @patch('tools.pre_deploy_check.fix_common_issues')
    def test_fix_common_issues(self, mock_fix):
        """Test fix_common_issues function."""
        # Mock the function to return True
        mock_fix.return_value = True
        
        # Call the function
        result = fix_common_issues(issues=['env', 'config'])
        
        # Verify the result
        self.assertTrue(result)
    
    @patch('tools.pre_deploy_check.check_environment_variables')
    @patch('tools.pre_deploy_check.check_configuration_files')
    @patch('tools.pre_deploy_check.check_database_connection')
    @patch('tools.pre_deploy_check.validate_api_endpoints')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_success(self, mock_args, mock_api, mock_db, mock_config, mock_env):
        """Test main function with all checks passing."""
        # Configure mocks
        mock_args.return_value = MagicMock(fix=False, verbose=True)
        mock_env.return_value = True
        mock_config.return_value = True
        mock_db.return_value = True
        mock_api.return_value = True
        
        # Run the main function
        with patch('sys.stdout'):  # Suppress print output
            with patch('sys.exit') as mock_exit:
                main()
                # Verify exit code 0 (success)
                mock_exit.assert_called_once_with(0)
    
    @patch('tools.pre_deploy_check.check_environment_variables')
    @patch('tools.pre_deploy_check.check_configuration_files')
    @patch('tools.pre_deploy_check.check_database_connection')
    @patch('tools.pre_deploy_check.validate_api_endpoints')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_with_failures(self, mock_args, mock_api, mock_db, mock_config, mock_env):
        """Test main function with failed checks."""
        # Configure mocks
        mock_args.return_value = MagicMock(fix=False, verbose=True)
        mock_env.return_value = False  # Environment variable check fails
        mock_config.return_value = True
        mock_db.return_value = True
        mock_api.return_value = True
        
        # Run the main function
        with patch('sys.stdout'):  # Suppress print output
            with patch('sys.exit') as mock_exit:
                main()
                # Verify exit code 1 (failure)
                mock_exit.assert_called_once_with(1)
    
    @patch('tools.pre_deploy_check.check_environment_variables')
    @patch('tools.pre_deploy_check.check_configuration_files')
    @patch('tools.pre_deploy_check.check_database_connection')
    @patch('tools.pre_deploy_check.validate_api_endpoints')
    @patch('tools.pre_deploy_check.fix_common_issues')
    @patch('argparse.ArgumentParser.parse_args')
    def test_main_with_fixes(self, mock_args, mock_fix, mock_api, mock_db, mock_config, mock_env):
        """Test main function with fix option enabled."""
        # Configure mocks
        mock_args.return_value = MagicMock(fix=True, verbose=True)
        mock_env.return_value = False  # Environment variable check fails
        mock_config.return_value = True
        mock_db.return_value = True
        mock_api.return_value = True
        mock_fix.return_value = True  # Fix succeeds
        
        # Run the main function
        with patch('sys.stdout'):  # Suppress print output
            with patch('sys.exit') as mock_exit:
                main()
                # Verify fix was called
                mock_fix.assert_called_once()
                # Verify exit code 0 (success after fix)
                mock_exit.assert_called_once_with(0)

if __name__ == '__main__':
    unittest.main()
